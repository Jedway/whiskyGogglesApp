# src/identification.py

import cv2
import numpy as np
import pickle
import os
import sys
import pandas as pd # Import pandas

# Import configuration variables
try:
    import config
except ModuleNotFoundError:
    print("Error: config.py not found. Make sure it's in the 'src' directory.")
    sys.exit(1) # Exit if config is missing, as it's crucial

# --- Global Variables ---
orb = None
bf = None
reference_features = []
bottle_details_df = pd.DataFrame() # Global DataFrame to hold all bottle details

def initialize_matcher_and_data():
    """
    Loads features, initializes ORB/Matcher, and loads the full bottle details DataFrame.
    """
    global orb, bf, reference_features, bottle_details_df
    print("Initializing matcher, loading reference features, and bottle details...")

    # 1. Load Reference Features
    if not os.path.exists(config.FEATURES_FILE):
        print(f"Error: Feature file '{config.FEATURES_FILE}' not found.")
        print("Please run the data_preparation.py script first.")
        return False

    try:
        with open(config.FEATURES_FILE, 'rb') as f:
            reference_features = pickle.load(f)
        if not reference_features:
             print(f"Warning: Feature file '{config.FEATURES_FILE}' is empty or invalid.")
             return False
        print(f"Loaded {len(reference_features)} reference bottle features.")
    except Exception as e:
        print(f"Error loading feature file '{config.FEATURES_FILE}': {e}")
        return False

    # 2. Load Full Bottle Details from Excel
    try:
        # Read the Excel file using pandas
        bottle_details_df = pd.read_excel(config.EXCEL_FILE_PATH)
        # Set the bottle ID column as the index for efficient lookup
        if config.COL_ID in bottle_details_df.columns:
            # Handle potential duplicate IDs if necessary, here we just keep the first
            bottle_details_df = bottle_details_df.loc[~bottle_details_df[config.COL_ID].duplicated(keep='first')]
            bottle_details_df.set_index(config.COL_ID, inplace=True)
            print(f"Loaded details for {len(bottle_details_df)} bottles from '{config.EXCEL_FILE_PATH}'.")
        else:
            print(f"Error: ID column '{config.COL_ID}' not found in Excel file '{config.EXCEL_FILE_PATH}'.")
            return False

    except FileNotFoundError:
        print(f"Error: Excel file not found at '{config.EXCEL_FILE_PATH}'")
        return False
    except Exception as e:
        print(f"Error reading or processing Excel file '{config.EXCEL_FILE_PATH}': {e}")
        return False

    # 3. Initialize ORB and Matcher
    try:
        orb = cv2.ORB_create(nfeatures=config.N_FEATURES_ORB)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        print("ORB detector and BFMatcher initialized.")
        return True # Indicate success
    except Exception as e:
        print(f"Error initializing OpenCV components: {e}")
        return False

# --- Call initialization when the module is loaded ---
INITIALIZATION_SUCCESSFUL = initialize_matcher_and_data()

def find_best_match(image_path):
    """
    Identifies the best matching whisky bottle ID and confidence.

    Args:
        image_path (str): Path to the input image file.

    Returns:
        tuple: (best_match_id, confidence_score, good_matches_count)
               Returns (None, 0.0, 0) if no match is found or an error occurs.
    """
    if not INITIALIZATION_SUCCESSFUL or orb is None or bf is None or not reference_features:
        print("Error: Matcher not initialized successfully. Cannot perform matching.")
        return None, 0.0, 0

    # ...(rest of the image loading and feature extraction logic remains the same)...
    if not os.path.exists(image_path):
        print(f"Error: Query image file not found at '{image_path}'")
        return None, 0.0, 0

    try:
        img_query = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img_query is None:
            print(f"Error: Could not load query image '{image_path}'.")
            return None, 0.0, 0

        kp_query, des_query = orb.detectAndCompute(img_query, None)

        if des_query is None or len(des_query) < config.MIN_MATCH_COUNT:
             return None, 0.0, 0

        all_match_results = []
        for ref in reference_features:
            ref_id = ref['id']
            des_ref = ref['descriptors']

            if des_ref is None or len(des_ref) < 2: continue

            try:
                matches = bf.knnMatch(des_query, des_ref, k=2)
            except cv2.error as e:
                print(f"Warning: OpenCV error during knnMatch for ref ID {ref_id}. Skipping. Error: {e}")
                continue

            good_matches = []
            for match_pair in matches:
                if len(match_pair) == 2:
                    m, n = match_pair
                    if m.distance < config.MATCHER_THRESHOLD * n.distance:
                        good_matches.append(m)

            if len(good_matches) >= config.MIN_MATCH_COUNT:
                all_match_results.append({
                    'id': ref_id,
                    'match_count': len(good_matches)
                })

        if not all_match_results:
            return None, 0.0, 0

        best_match = max(all_match_results, key=lambda x: x['match_count'])
        confidence_score = best_match['match_count'] # Raw count as score

        # Return only ID, score, and count. Name lookup is done via get_bottle_details
        return best_match['id'], confidence_score, best_match['match_count']

    except cv2.error as e:
         print(f"An OpenCV error occurred during matching for image '{image_path}': {e}")
         return None, 0.0, 0
    except Exception as e:
        print(f"An unexpected error occurred during matching for image '{image_path}': {e}")
        return None, 0.0, 0


def get_bottle_details(bottle_id):
    """
    Retrieves all details for a given bottle ID from the loaded DataFrame.

    Args:
        bottle_id: The ID of the bottle to look up.

    Returns:
        pandas.Series: A series containing bottle details, or None if not found.
                       Excludes the image_url column.
    """
    global bottle_details_df
    if not INITIALIZATION_SUCCESSFUL or bottle_details_df.empty:
        print("Error: Bottle details DataFrame not loaded.")
        return None

    try:
        # Lookup the bottle by its ID (which is the DataFrame index)
        details = bottle_details_df.loc[bottle_id]

        # Drop the image_url column if it exists
        if config.COL_IMAGE_URL in details.index:
            details = details.drop(config.COL_IMAGE_URL)

        return details
    except KeyError:
        print(f"Warning: Details not found for bottle ID '{bottle_id}' in the loaded DataFrame.")
        return None
    except Exception as e:
        print(f"Error retrieving details for bottle ID '{bottle_id}': {e}")
        return None

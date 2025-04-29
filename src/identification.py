# src/identification.py

import cv2
import numpy as np
import pickle
import os
import sys
import pandas as pd # Import pandas
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import imutils

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
executor = ThreadPoolExecutor(max_workers=4)  # For parallel processing

def preprocess_image(image):
    """
    Preprocess image for better feature detection.
    """
    # Resize image to a reasonable size while maintaining aspect ratio
    if max(image.shape) > 1024:
        image = imutils.resize(image, width=1024)
    
    # Apply CLAHE for better contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    return clahe.apply(image)

@lru_cache(maxsize=100)
def get_bottle_details_cached(bottle_id):
    """
    Cached version of get_bottle_details for faster repeated lookups.
    """
    try:
        details = bottle_details_df.loc[bottle_id]
        if config.COL_IMAGE_URL in details.index:
            details = details.drop(config.COL_IMAGE_URL)
        return details
    except (KeyError, Exception) as e:
        print(f"Error retrieving details for bottle ID '{bottle_id}': {e}")
        return None

def process_reference_match(args):
    """
    Process a single reference match (for parallel processing).
    """
    des_query, ref = args
    ref_id = ref['id']
    des_ref = ref['descriptors']

    if des_ref is None or len(des_ref) < 2:
        return None

    try:
        matches = bf.knnMatch(des_query, des_ref, k=2)
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < config.MATCHER_THRESHOLD * n.distance:
                    good_matches.append(m)

        if len(good_matches) >= config.MIN_MATCH_COUNT:
            return {
                'id': ref_id,
                'match_count': len(good_matches)
            }
    except cv2.error:
        pass
    return None

def initialize_matcher_and_data():
    """
    Loads features, initializes ORB/Matcher, and loads the full bottle details DataFrame.
    """
    global orb, bf, reference_features, bottle_details_df
    print("Initializing matcher, loading reference features, and bottle details...")

    try:
        # 1. Load Reference Features
        if not os.path.exists(config.FEATURES_FILE):
            print(f"Error: Feature file '{config.FEATURES_FILE}' not found.")
            return False

        with open(config.FEATURES_FILE, 'rb') as f:
            reference_features = pickle.load(f)
        if not reference_features:
            print(f"Warning: Feature file '{config.FEATURES_FILE}' is empty or invalid.")
            return False
        print(f"Loaded {len(reference_features)} reference bottle features.")

        # 2. Load Full Bottle Details from Excel
        bottle_details_df = pd.read_excel(config.EXCEL_FILE_PATH)
        if config.COL_ID not in bottle_details_df.columns:
            print(f"Error: ID column '{config.COL_ID}' not found in Excel file.")
            return False
            
        # Handle potential duplicate IDs
        bottle_details_df = bottle_details_df.loc[~bottle_details_df[config.COL_ID].duplicated(keep='first')]
        bottle_details_df.set_index(config.COL_ID, inplace=True)
        print(f"Loaded details for {len(bottle_details_df)} bottles.")

        # 3. Initialize ORB and Matcher with optimized settings
        orb = cv2.ORB_create(
            nfeatures=config.N_FEATURES_ORB,
            scaleFactor=1.2,
            nlevels=8,
            edgeThreshold=31,
            firstLevel=0,
            WTA_K=2,
            patchSize=31,
            fastThreshold=20
        )
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        print("ORB detector and BFMatcher initialized with optimized settings.")
        return True

    except Exception as e:
        print(f"Error during initialization: {e}")
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

    if not os.path.exists(image_path):
        print(f"Error: Query image file not found at '{image_path}'")
        return None, 0.0, 0

    try:
        # Load and preprocess image
        img_query = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img_query is None:
            print(f"Error: Could not load query image '{image_path}'.")
            return None, 0.0, 0

        # Preprocess image
        img_query = preprocess_image(img_query)
        
        # Detect features
        kp_query, des_query = orb.detectAndCompute(img_query, None)

        if des_query is None or len(des_query) < config.MIN_MATCH_COUNT:
            return None, 0.0, 0

        # Process matches in parallel
        match_args = [(des_query, ref) for ref in reference_features]
        match_results = list(executor.map(process_reference_match, match_args))
        
        # Filter out None results and find best match
        all_match_results = [result for result in match_results if result is not None]

        if not all_match_results:
            return None, 0.0, 0

        best_match = max(all_match_results, key=lambda x: x['match_count'])
        confidence_score = best_match['match_count']

        return best_match['id'], confidence_score, best_match['match_count']

    except Exception as e:
        print(f"An unexpected error occurred during matching for image '{image_path}': {e}")
        return None, 0.0, 0

def get_bottle_details(bottle_id):
    """
    Retrieves all details for a given bottle ID using the cached function.
    """
    return get_bottle_details_cached(bottle_id)

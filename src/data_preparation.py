# src/data_preparation.py

import pandas as pd
import requests
import cv2
import numpy as np
import pickle
import os
import time
from pathlib import Path
import sys

# Import configuration variables
try:
    import config
except ModuleNotFoundError:
    print("Error: config.py not found. Make sure it's in the 'src' directory.")
    sys.exit(1)

def download_images(df_bottles):
    """Downloads images specified in the dataframe."""
    print(f"\n--- Starting Image Downloads to '{config.IMAGE_DOWNLOAD_DIR}' ---")
    os.makedirs(config.IMAGE_DOWNLOAD_DIR, exist_ok=True)
    download_count = 0
    download_errors = 0
    image_paths = {} # Dictionary to store {id: path}

    for index, row in df_bottles.iterrows():
        bottle_id = row[config.COL_ID]
        image_url = row[config.COL_IMAGE_URL]

        if not image_url or not isinstance(image_url, str):
            print(f"Warning: Invalid or missing URL for ID {bottle_id}. Skipping.")
            download_errors += 1
            continue

        try:
            # Create a filename using the bottle ID
            file_extension = Path(image_url).suffix if Path(image_url).suffix else '.jpg'
            safe_id_str = str(bottle_id).replace('/','_').replace('\\','_').replace(':','_') # Sanitize common problematic chars
            image_filename = f"{safe_id_str}{file_extension}"
            # Construct path relative to the project root
            image_path = os.path.join(config.IMAGE_DOWNLOAD_DIR, image_filename)

            if not os.path.exists(image_path):
                try:
                    response = requests.get(image_url, stream=True, timeout=20) # Increased timeout
                    response.raise_for_status()

                    with open(image_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    download_count += 1
                    image_paths[bottle_id] = image_path # Store path on success
                    # print(f"Downloaded: {image_filename}") # Verbose output
                    time.sleep(0.05) # Small delay

                except requests.exceptions.RequestException as e:
                    print(f"Error downloading {image_url} for ID {bottle_id}: {e}")
                    download_errors += 1
                except Exception as e:
                    print(f"Error saving file {image_filename} for ID {bottle_id}: {e}")
                    download_errors += 1
            else:
                # print(f"Skipped (already exists): {image_filename}") # Verbose output
                image_paths[bottle_id] = image_path # Store path even if exists

        except Exception as e:
            print(f"Error processing row for ID {bottle_id} (URL: {image_url}): {e}")
            download_errors += 1

    print(f"\nImage download complete.")
    print(f"  Successfully downloaded: {download_count} new images.")
    print(f"  Found existing/downloaded: {len(image_paths)} images.")
    print(f"  Errors encountered: {download_errors}.")
    return image_paths


def extract_features(image_paths_dict):
    """Extracts ORB features from images and saves them."""
    print(f"\n--- Starting Feature Extraction (using {config.N_FEATURES_ORB} features) ---")

    orb = cv2.ORB_create(nfeatures=config.N_FEATURES_ORB)
    reference_features = []
    extraction_errors = 0
    processed_count = 0
    total_images = len(image_paths_dict)

    for bottle_id, image_path in image_paths_dict.items():
        try:
            # Load image in grayscale
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

            if img is None:
                print(f"Warning: Could not load image {image_path} for ID {bottle_id}. Skipping.")
                extraction_errors += 1
                continue

            # Detect keypoints and compute descriptors
            keypoints, descriptors = orb.detectAndCompute(img, None)

            if descriptors is None or len(descriptors) == 0:
                print(f"Warning: No descriptors found for image {image_path} (ID: {bottle_id}). Skipping.")
                extraction_errors += 1
                continue

            # Fetch the name from the original dataframe (needs df passed or accessed)
            # Assuming df_bottles is accessible in this scope or passed as argument
            bottle_name = df_bottles.loc[df_bottles[config.COL_ID] == bottle_id, config.COL_NAME].iloc[0]

            reference_features.append({
                'id': bottle_id,
                'name': bottle_name,
                'descriptors': descriptors
            })
            processed_count += 1

            # Progress indicator
            if processed_count % 50 == 0 or processed_count == total_images:
               print(f"  Processed {processed_count}/{total_images} images...")


        except Exception as e:
            print(f"Error processing image {image_path} for ID {bottle_id}: {e}")
            extraction_errors += 1

    print(f"\nFeature extraction complete.")
    print(f"  Successfully processed: {processed_count} images.")
    print(f"  Errors/Skipped: {extraction_errors}.")

    # --- Save the features ---
    if reference_features:
        try:
            with open(config.FEATURES_FILE, 'wb') as f:
                pickle.dump(reference_features, f)
            print(f"Reference features saved to '{config.FEATURES_FILE}'")
        except Exception as e:
            print(f"Error saving features to {config.FEATURES_FILE}: {e}")
    else:
        print("Warning: No features were extracted. Feature file not saved.")

# --- Main Execution Logic ---
if __name__ == "__main__":
    print("Starting Data Preparation...")

    # 1. Load Dataframe
    try:
        df = pd.read_excel(config.EXCEL_FILE_PATH)
        # Ensure required columns exist
        required_cols = [config.COL_ID, config.COL_NAME, config.COL_IMAGE_URL]
        if not all(col in df.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df.columns]
            print(f"Error: Missing required columns in Excel file: {missing}")
            print(f"Please ensure columns '{config.COL_ID}', '{config.COL_NAME}', and '{config.COL_IMAGE_URL}' exist.")
            sys.exit(1)

        # Select and clean data
        df_bottles = df[required_cols].copy()
        df_bottles.dropna(subset=[config.COL_IMAGE_URL], inplace=True)
        df_bottles.dropna(subset=[config.COL_ID], inplace=True) # Ensure IDs are present
        df_bottles = df_bottles.astype({config.COL_IMAGE_URL: str}) # Ensure URL is string
        df_bottles = df_bottles[df_bottles[config.COL_IMAGE_URL].str.startswith(('http://', 'https://'))] # Basic URL check
        print(f"Loaded {len(df_bottles)} valid bottle records from '{config.EXCEL_FILE_PATH}'")

    except FileNotFoundError:
        print(f"Error: Excel file not found at '{config.EXCEL_FILE_PATH}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        sys.exit(1)

    # 2. Download Images
    # Make df_bottles global or pass it around if needed in extract_features without redefining it
    image_paths_map = download_images(df_bottles)

    # Filter dataframe to only include bottles whose images were successfully found/downloaded
    successful_ids = list(image_paths_map.keys())
    df_bottles = df_bottles[df_bottles[config.COL_ID].isin(successful_ids)].copy()
    print(f"Proceeding with feature extraction for {len(df_bottles)} bottles with images.")


    # 3. Extract Features
    if not df_bottles.empty:
        extract_features(image_paths_map)
    else:
        print("No images were successfully downloaded or found. Skipping feature extraction.")

    print("\nData Preparation Script Finished.")
    
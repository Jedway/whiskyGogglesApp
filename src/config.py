# src/config.py

import os

# Get the project root directory (one level up from src)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# --- File Paths ---
# IMPORTANT: Make sure 'your_dataset.xlsx' is the correct name of your Excel file
EXCEL_FILE_PATH = os.path.join(PROJECT_ROOT, 'data', 'bottle_dataset.xlsx')
IMAGE_DOWNLOAD_DIR = os.path.join(PROJECT_ROOT, 'whisky_images')  # Absolute path to image directory
FEATURES_FILE = os.path.join(PROJECT_ROOT, 'bottle_features.pkl')  # Absolute path to features file

# --- Feature Extraction Parameters (ORB) ---
# Adjust nfeatures based on testing - more features might improve accuracy but slow down processing
N_FEATURES_ORB = 2000

# --- Matching Parameters ---
# Lowe's ratio test threshold for filtering good matches (lower means stricter)
MATCHER_THRESHOLD = 0.75
# Minimum number of good matches required to consider a result valid
MIN_MATCH_COUNT = 10

# --- Dataset Column Names (Adjust if your Excel file uses different names) ---
COL_ID = 'id'
COL_NAME = 'name'
COL_IMAGE_URL = 'image_url'

# src/config.py

# --- File Paths ---
# IMPORTANT: Make sure 'your_dataset.xlsx' is the correct name of your Excel file
EXCEL_FILE_PATH = 'data/bottle_dataset.xlsx'
IMAGE_DOWNLOAD_DIR = 'whisky_images' # Relative to the root project directory
FEATURES_FILE = 'bottle_features.pkl' # Relative to the root project directory

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

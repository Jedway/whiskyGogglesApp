# src/config.py

import os
import multiprocessing

# Get the project root directory (one level up from src)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# --- File Paths ---
# IMPORTANT: Make sure 'your_dataset.xlsx' is the correct name of your Excel file
EXCEL_FILE_PATH = os.path.join(PROJECT_ROOT, 'data', 'bottle_dataset.xlsx')
IMAGE_DOWNLOAD_DIR = os.path.join(PROJECT_ROOT, 'whisky_images')  # Absolute path to image directory
FEATURES_FILE = os.path.join(PROJECT_ROOT, 'bottle_features.pkl')  # Absolute path to features file

# --- Feature Extraction Parameters (ORB) ---
# Optimized for better accuracy while maintaining performance
N_FEATURES_ORB = 1500  # Reduced from 2000 for better performance while maintaining accuracy
SCALE_FACTOR = 1.2    # Scale factor between levels in the scale pyramid
N_LEVELS = 8         # Number of pyramid levels
EDGE_THRESHOLD = 31  # Size of the border where features are not detected
FIRST_LEVEL = 0     # Level of pyramid to put source image
WTA_K = 2           # Number of points to produce each element of the oriented BRIEF descriptor
PATCH_SIZE = 31     # Size of the patch used by the oriented BRIEF descriptor
FAST_THRESHOLD = 20 # FAST detector threshold

# --- Matching Parameters ---
MATCHER_THRESHOLD = 0.75  # Lowe's ratio test threshold
MIN_MATCH_COUNT = 10     # Minimum number of good matches required

# --- Performance Optimization ---
MAX_IMAGE_SIZE = 1024    # Maximum image dimension for processing
NUM_WORKERS = min(multiprocessing.cpu_count(), 4)  # Number of worker threads
CACHE_SIZE = 100         # Size of the LRU cache for bottle details

# --- Dataset Column Names (Adjust if your Excel file uses different names) ---
COL_ID = 'id'
COL_NAME = 'name'
COL_IMAGE_URL = 'image_url'

# --- Production Settings ---
TEMP_FILE_CLEANUP_AGE = 300  # Clean up temp files older than 5 minutes (300 seconds)
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB max upload size

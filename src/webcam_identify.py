# src/webcam_identify.py

import cv2
import os
import time
import sys
import pandas as pd # Import pandas for type hinting if needed

# Try to import the matching function and config
try:
    # Import the necessary functions and the initialization status flag
    from identification import find_best_match, get_bottle_details, INITIALIZATION_SUCCESSFUL
    import config
except ModuleNotFoundError:
    print("Error: Could not import from 'identification.py' or 'config.py'.")
    print("Ensure these files exist in the 'src' directory, along with '__init__.py',")
    print("and you are running this script from the project root ('whisky_goggles/').")
    sys.exit(1)
except ImportError as e:
     print(f"Error importing required modules: {e}")
     sys.exit(1)

# --- Configuration ---
WEBCAM_INDEX = 0
TEMP_CAPTURE_FILENAME = "_temp_capture.jpg"

if __name__ == "__main__":
    print("--- Webcam Whisky Identifier ---")

    if not INITIALIZATION_SUCCESSFUL:
        print("\nExiting because matcher initialization failed. Please check previous errors.")
        sys.exit(1)

    print(f"\nInitializing webcam (index {WEBCAM_INDEX})...")
    cap = cv2.VideoCapture(WEBCAM_INDEX)

    if not cap.isOpened():
        print(f"Error: Could not open webcam at index {WEBCAM_INDEX}.")
        sys.exit(1)

    print("Webcam initialized successfully.")
    print("\nInstructions:")
    print(" - Position the bottle label clearly in front of the webcam.")
    print(" - Press [SPACEBAR] to capture and identify.")
    print(" - Press [q] to quit.")

    last_match_time = 0
    match_result_display = "" # Text to display on webcam feed

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Can't receive frame. Exiting ...")
            break

        display_frame = frame.copy()

        # Display brief result text on screen
        if time.time() - last_match_time < 5.0:
            cv2.putText(display_frame, match_result_display, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow('Webcam - Press SPACE to Capture, Q to Quit', display_frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("\nQuitting...")
            break

        elif key == ord(' '):
            print("\nCapturing image...")
            capture_path = os.path.join(".", TEMP_CAPTURE_FILENAME)

            try:
                success = cv2.imwrite(capture_path, frame)
                if not success:
                     print(f"Error: Failed to save captured image to {capture_path}")
                     continue

                print(f"Image saved temporarily to {capture_path}")
                print("Attempting to identify...")

                # --- Perform Identification ---
                bottle_id, score, matches_count = find_best_match(capture_path)

                # --- Get and Display Details ---
                if bottle_id is not None:
                    print(f"\n--- Match Found ---")
                    print(f"  Identified Bottle ID: {bottle_id}")
                    print(f"  Good Matches: {matches_count}")
                    print(f"  Confidence Score (raw): {score}")

                    # Get the full details using the ID
                    details = get_bottle_details(bottle_id)

                    if details is not None:
                        print("\n  --- Bottle Details ---")
                        # Print details neatly (Series to string handles formatting)
                        details_str = details.to_string()
                        for line in details_str.split('\n'):
                            print(f"    {line.strip()}")

                        # Update display text for webcam window (keep it short)
                        match_result_display = f"Match: {details.get('name', bottle_id)}" # Use name if available
                    else:
                         print(f"  Warning: Could not retrieve details for ID {bottle_id}.")
                         match_result_display = f"Match: ID {bottle_id} (details missing)"

                else:
                    print("\n--- No matching bottle found. ---")
                    match_result_display = "No Match Found"

                last_match_time = time.time()

                # Clean up temp file
                try:
                    os.remove(capture_path)
                except OSError as e:
                    print(f"Error removing temporary file {capture_path}: {e}")

            except Exception as e:
                print(f"An error occurred during capture/identification: {e}")

    cap.release()
    cv2.destroyAllWindows()
    print("Webcam released and windows closed.")
    
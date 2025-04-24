# src/main.py

import sys
import os

# Try to import the matching function
try:
    from identification import find_best_match, INITIALIZATION_SUCCESSFUL
except ModuleNotFoundError:
    print("Error: Could not import from 'identification.py'.")
    print("Ensure 'identification.py' and '__init__.py' exist in the 'src' directory,")
    print("and you are running this script from the project root ('whisky_goggles/').")
    sys.exit(1)
except ImportError as e:
     print(f"Error importing identification module: {e}")
     sys.exit(1)


if __name__ == "__main__":
    # Check if matcher initialized correctly
    if not INITIALIZATION_SUCCESSFUL:
        print("Exiting because matcher initialization failed. Please check previous errors.")
        sys.exit(1)

    # --- Get Test Image Path ---
    if len(sys.argv) > 1:
        test_image_path = sys.argv[1]
        print(f"Input image path provided: {test_image_path}")
    else:
        # --- IMPORTANT: Provide a default test image path if no argument is given ---
        # --- Or prompt the user, or exit ---
        print("\nUsage: python src/main.py <path_to_your_test_image>")
        # Example default path (replace or remove):
        test_image_path = 'whisky_images/default_test_image.jpg' # Adjust this default path
        print(f"No image path provided. Using default: {test_image_path}")
        # Alternatively, exit:
        # print("Error: Please provide the path to the image you want to identify.")
        # sys.exit(1)


    if not os.path.exists(test_image_path):
         print(f"Error: Test image not found at '{test_image_path}'.")
         sys.exit(1)


    # --- Perform Identification ---
    print(f"\nAttempting to identify: {os.path.basename(test_image_path)}")
    bottle_id, bottle_name, score, matches_count = find_best_match(test_image_path)

    # --- Display Results ---
    if bottle_id is not None:
        print(f"\n--- Best Match Found ---")
        print(f"  ID: {bottle_id}")
        print(f"  Name: {bottle_name}")
        print(f"  Good Matches: {matches_count}")
        print(f"  Confidence Score (raw count): {score}")
    else:
        print("\n--- No matching bottle found meeting the criteria. ---")

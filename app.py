# app.py (in project root)

from flask import Flask, request, jsonify, render_template, make_response, send_from_directory
import os
import pandas as pd
import sys
import werkzeug.utils
import datetime # <-- import datetime for footer timestamp

# --- Add src directory to Python path ---
# This allows importing modules from 'src' when running app.py from the root
src_dir = os.path.join(os.path.dirname(__file__), 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# --- Import Identification Logic ---
try:
    # Now imports should work relative to the src directory
    from identification import find_best_match, get_bottle_details, INITIALIZATION_SUCCESSFUL
    import config # If needed for paths etc. directly here (unlikely now)
except ModuleNotFoundError as e:
     print(f"Error importing identification module: {e}")
     print("Ensure 'src' directory and its contents (config.py, identification.py, __init__.py) exist.")
     sys.exit(1)

# --- Flask App Setup ---
app = Flask(__name__, template_folder='templates', static_folder='static')

# Configure a directory for temporary uploads (relative to app.py)
UPLOAD_FOLDER = '_temp_uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Routes ---
@app.route('/')
def index():
    """Serves the main HTML page."""
    current_year = datetime.datetime.now().year # <-- Get current year
    if not INITIALIZATION_SUCCESSFUL:
         return render_template('index.html', init_error=True, current_year=current_year) # Pass year
    return render_template('index.html', init_error=False, current_year=current_year) # Pass year

@app.route('/identify', methods=['POST'])
def identify_bottle_api():
    """API endpoint to handle image upload and identification."""
    if not INITIALIZATION_SUCCESSFUL:
         return jsonify({'success': False, 'error': 'Server Error: Identification module not initialized.'}), 500

    if 'bottle_image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file part in the request.'}), 400

    file = request.files['bottle_image']

    if file.filename == '':
        return jsonify({'success': False, 'error': 'No image file selected.'}), 400

    if file:
        # Use werkzeug's secure_filename for safety
        filename = werkzeug.utils.secure_filename(f"upload_{os.urandom(8).hex()}_{file.filename}")
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        try:
            file.save(temp_path)

            # --- Call identification logic ---
            bottle_id, score, matches_count = find_best_match(temp_path)

            if bottle_id is not None:
                details = get_bottle_details(bottle_id)
                if details is not None:
                    # Convert details Series to dict for JSON compatibility
                    result_data = details.to_dict()
                    # Add match info
                    result_data['_match_confidence_score'] = score
                    result_data['_match_good_matches'] = matches_count
                    # Convert numpy types to standard Python types
                    for key, value in result_data.items():
                        if hasattr(value, 'item'):
                            result_data[key] = value.item() # Convert numpy int/float to python int/float
                        elif pd.isna(value): # Handle potential Pandas NaNs
                            result_data[key] = None

                    return jsonify({'success': True, 'data': result_data})
                else:
                    # Found ID but couldn't get details (less likely now details are loaded)
                    return jsonify({'success': False, 'error': f'Match found (ID: {bottle_id}) but details unavailable.'}), 500
            else:
                # No match found meeting criteria
                return jsonify({'success': False, 'error': 'No matching bottle found.'})

        except Exception as e:
             app.logger.error(f"Error during identification process: {e}", exc_info=True) # Log full error
             return jsonify({'success': False, 'error': 'An internal error occurred during identification.'}), 500
        finally:
            # --- Clean up the temporary file ---
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError as e:
                    app.logger.error(f"Error removing temp file {temp_path}: {e}")

    return jsonify({'success': False, 'error': 'Invalid file or upload error.'}), 400

@app.route('/static/js/service-worker.js')
def serve_service_worker():
    response = make_response(send_from_directory('static/js', 'service-worker.js'))
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'
    return response

@app.route('/static/manifest.json')
def serve_manifest():
    return send_from_directory('static', 'manifest.json')

# --- Main Execution Guard ---
if __name__ == '__main__':
    if not INITIALIZATION_SUCCESSFUL:
         print("-----------------------------------------------------")
         print("ERROR: Identification module failed to initialize.")
         print("Please check previous errors (e.g., feature file missing, excel file issues).")
         print("The web server cannot function without it.")
         print("-----------------------------------------------------")
         # Optionally prevent server start: sys.exit(1)
    else:
         print("Identification module initialized successfully.")

    print("Starting Flask development server...")
    print("Access at: http://127.0.0.1:5000")
    # Set debug=False for production
    app.run(host='127.0.0.1', port=5000, debug=True)
    
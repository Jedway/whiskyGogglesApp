# app.py (in project root)

from flask import Flask, request, jsonify, render_template, make_response, send_from_directory
import os
import pandas as pd
import sys
import werkzeug.utils
import datetime
import time
from threading import Thread
import mimetypes

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
app.config['MAX_CONTENT_LENGTH'] = config.MAX_UPLOAD_SIZE
app.config['UPLOAD_FOLDER'] = '_temp_uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def cleanup_old_files():
    """Clean up old temporary files periodically."""
    while True:
        current_time = time.time()
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                if os.path.getmtime(filepath) < current_time - config.TEMP_FILE_CLEANUP_AGE:
                    os.remove(filepath)
            except OSError:
                continue
        time.sleep(300)  # Run every 5 minutes

def is_valid_image(file):
    """Check if the uploaded file is a valid image."""
    if not file or not file.filename:
        return False
    
    # Check file extension
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        return False
    
    # Check MIME type
    try:
        mime_type = mimetypes.guess_type(file.filename)[0]
        return mime_type and mime_type.startswith('image/')
    except:
        return False

# --- Routes ---
@app.route('/')
def index():
    """Serves the main HTML page."""
    current_year = datetime.datetime.now().year
    return render_template('index.html', 
                         init_error=not INITIALIZATION_SUCCESSFUL,
                         current_year=current_year)

@app.route('/identify', methods=['POST'])
def identify_bottle_api():
    """API endpoint to handle image upload and identification."""
    if not INITIALIZATION_SUCCESSFUL:
        return jsonify({
            'success': False,
            'error': 'Server Error: Identification module not initialized.'
        }), 500

    # Validate request
    if 'bottle_image' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No image file part in the request.'
        }), 400

    file = request.files['bottle_image']
    
    # Validate file
    if not is_valid_image(file):
        return jsonify({
            'success': False,
            'error': 'Invalid file type. Please upload a valid image file.'
        }), 400

    try:
        # Generate secure filename with random component
        filename = werkzeug.utils.secure_filename(f"upload_{os.urandom(8).hex()}_{file.filename}")
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Save and process file
        file.save(temp_path)

        try:
            # Call identification logic
            bottle_id, score, matches_count = find_best_match(temp_path)

            if bottle_id is not None:
                details = get_bottle_details(bottle_id)
                if details is not None:
                    # Convert details to dict and add match info
                    result_data = details.to_dict()
                    result_data['_match_confidence_score'] = score
                    result_data['_match_good_matches'] = matches_count

                    # Convert numpy types to Python types
                    for key, value in result_data.items():
                        if hasattr(value, 'item'):
                            result_data[key] = value.item()
                        elif pd.isna(value):
                            result_data[key] = None

                    return jsonify({'success': True, 'data': result_data})
                else:
                    return jsonify({
                        'success': False,
                        'error': f'Match found (ID: {bottle_id}) but details unavailable.'
                    }), 500
            else:
                return jsonify({
                    'success': False,
                    'error': 'No matching bottle found.'
                }), 404

        except Exception as e:
            app.logger.error(f"Error during identification process: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': 'An internal error occurred during identification.'
            }), 500
        finally:
            # Clean up the temporary file
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except OSError as e:
                app.logger.error(f"Error removing temp file {temp_path}: {e}")

    except Exception as e:
        app.logger.error(f"Error handling upload: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'An error occurred while processing the upload.'
        }), 500

@app.route('/static/js/service-worker.js')
def serve_service_worker():
    response = make_response(send_from_directory('static/js', 'service-worker.js'))
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'
    return response

@app.route('/static/manifest.json')
def serve_manifest():
    return send_from_directory('static', 'manifest.json')

# --- Error Handlers ---
@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        'success': False,
        'error': f'File too large. Maximum size is {config.MAX_UPLOAD_SIZE / (1024 * 1024)}MB'
    }), 413

@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error(f"Internal Server Error: {error}", exc_info=True)
    return jsonify({
        'success': False,
        'error': 'An internal server error occurred.'
    }), 500

# --- Main Execution Guard ---
if __name__ == '__main__':
    if not INITIALIZATION_SUCCESSFUL:
        print("-----------------------------------------------------")
        print("ERROR: Identification module failed to initialize.")
        print("Please check previous errors.")
        print("The web server cannot function without it.")
        print("-----------------------------------------------------")
    else:
        print("Identification module initialized successfully.")

    # Start cleanup thread
    cleanup_thread = Thread(target=cleanup_old_files, daemon=True)
    cleanup_thread.start()

    # Start server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
    
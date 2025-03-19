from flask import Flask, request, jsonify
import os
import pydicom

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run():
    """Receive a request with a series path, read the first DICOM file, and return its metadata."""
    data = request.json

    # Ensure the request contains "series_path"
    series_path = data.get("series_path")
    if not series_path:
        return jsonify({'error': "Missing 'series_path' in request data"}), 400

    # Validate that the directory exists
    if not os.path.isdir(series_path):
        return jsonify({'error': f"Series path not found: {series_path}"}), 404

    # Find the first DICOM file in the directory
    dicom_files = sorted([f for f in os.listdir(series_path) if f.lower().endswith(".dcm")])
    if not dicom_files:
        return jsonify({'error': "No DICOM files found in the series directory"}), 404

    dicom_path = os.path.join(series_path, dicom_files[0])

    try:
        # Read the DICOM file
        dicom_data = pydicom.dcmread(dicom_path)

        # Extract metadata (excluding pixel data)
        metadata = {tag: str(dicom_data[tag].value) for tag in dicom_data.keys() if tag != (0x7FE0, 0x0010)}

        return jsonify({'metadata': metadata}), 200

    except Exception as e:
        return jsonify({'error': f"Failed to read DICOM: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)

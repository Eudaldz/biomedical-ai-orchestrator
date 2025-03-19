from flask import Flask, request, jsonify
import os
import logging
from algorithm import run_segmentation
import traceback

app = Flask(__name__)
DICOM_DIR = "/dicom" # Directori on es guarden els DICOMs dins del contenidor

logging.basicConfig(level=logging.INFO)

@app.route('/run', methods=['POST'])
def predict():
    logging.info("Vascular Segmenter service received a request")
    logging.info(f"Request data: {request.json}")
    data = request.get_json()
    directory = data.get('directory')
    logging.info(directory)
    if not directory:
        logging.info(f"directory field not found: Directory is required")
        return jsonify({"status": "failed", "message": "Directory is required"}), 400

    directory = directory.strip()

    dicom_dir = os.path.abspath(os.path.join(DICOM_DIR, directory))
    
    if not os.path.exists(dicom_dir):
        logging.info(f"directory field not found: {dicom_dir}")
        return jsonify({"status": "failed", "message": "Directory not found"}), 404

    try:
        # Processar tots els fitxers dins del directori
        result = run_segmentation(dicom_dir)
        return jsonify({"status": "success", "result": dicom_dir}), 200

    except Exception as e:
        error_trace = traceback.format_exc()  # ⬅️ Captura el error detallado
        logging.error(f"❌ Error in process_dicom:\n{error_trace}")  # ⬅️ Muestra el error
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
from flask import Flask, request, jsonify
import pydicom
import numpy as np
import os
import logging
import traceback

app = Flask(__name__)
DICOM_DIR = "/dicom"  # Directori on es guarden els DICOMs dins del contenidor

logging.basicConfig(level=logging.INFO)

@app.route('/run', methods=['POST'])
def process_dicom():
    logging.info("Process service received a request")
    logging.info(f"Request data: {request.json}")
    data = request.get_json()
    directory = data.get('directory')
    logging.info(directory)
    if not directory:
        logging.info(f"directory field not found: Directory is required")
        return jsonify({"status": "failed", "message": "Directory is required"}), 400

    dicom_dir = os.path.join(DICOM_DIR, directory)
    print(f"📂 Buscando archivos en: {dicom_dir}")
    if not os.path.exists(dicom_dir):
        logging.info(f"directory field not found: {dicom_dir}")
        return jsonify({"status": "failed", "message": "Directory not found"}), 404

    try:
        # Processar tots els fitxers dins del directori
        dicom_files = [f for f in os.listdir(dicom_dir) if f.lower().endswith('.dcm')]
        if not dicom_files:
            logging.info(f"No DICOM files found in directory: {dicom_dir}")
            return jsonify({"status": "failed", "message": "No DICOM files found in directory"}), 404
        
        logging.info(f"reading files: {dicom_dir}")
        pixel_values = []
        for dicom_file in dicom_files:
            dicom_path = os.path.join(dicom_dir, dicom_file)
            dicom_data = pydicom.dcmread(dicom_path)
            pixel_array = dicom_data.pixel_array.astype(np.float32)
            pixel_values.append(np.mean(pixel_array))

        # Calcular la mitjana de tots els píxels
        mean_pixel_value = float(np.mean(pixel_values))
        logging.info(f"returning mean value: {mean_pixel_value}")
        return jsonify({"status": "success", "result": mean_pixel_value}), 200

    except Exception as e:
        error_trace = traceback.format_exc()  # ⬅️ Captura el error detallado
        logging.error(f"❌ Error in process_dicom:\n{error_trace}")  # ⬅️ Muestra el error
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
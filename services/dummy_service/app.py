from flask import Flask, request, jsonify
import time
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/run', methods=['POST'])
def predict():
    try:
        logging.info("Dummy service received a request")
        logging.info(f"Request data: {request.json}")
        time.sleep(8)  # Simula temps de processament
        return jsonify({'result': 'success'}), 200
    except Exception as e:
        logging.error(f"Error in dummy service: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

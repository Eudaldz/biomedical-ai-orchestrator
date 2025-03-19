# AI Orchestrator

## Project Structure

```
project-root/
├── docker-compose.yml
├── services/
│   ├── dummy_service/
│   │   ├── Dockerfile
│   │   ├── app.py
│   │   ├── requirements.txt
│   ├── echo_dicom/
│   │   ├── Dockerfile
│   │   ├── app.py
│   │   ├── requirements.txt
│   ├── process_dicom/
│   │   ├── Dockerfile
│   │   ├── app.py
│   │   ├── requirements.txt
│   ├── vascular_segmentation/
│   ├── modules/
│   ├── utils/
│   │   ├── image.py
│   ├── algorithm.py
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
├── server/
│   ├── static/
│   ├── templates/
│   ├── Dockerfile
│   ├── pacs.py
│   ├── server.py
│   ├── requirements.txt
├── monitoring/
│   ├── prometheus.yml
│   ├── grafana/
│   │   ├── dashboards/
├── logs/
├── dicom/
└── .env
```

## How to Use

### 1. Setup

- Install **Docker** and **Docker Compose**.
- Clone the repository:

  ```bash
  cd <project-root>
  git clone https://github.com/Eudaldz/biomedical-ai-orchestrator.git
  ```

- **Windows Setup:**

  - Install **Docker Desktop** from the official site: https://www.docker.com/products/docker-desktop/
  - Verify installation:
    ```bash
    docker --version
    ```

- **Linux Setup:**
  - Install Docker:
    ```bash
    sudo apt-get update
    sudo apt-get install -y docker.io
    ```
  - Add your user to the Docker group:
    ```bash
    sudo usermod -aG docker $USER
    ```
  - Install **Docker Compose**:
    ```bash
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    ```

### 2. Build and Run

- Build and start all services in Visual Studio Code:

  ```bash
  cd <project-root>
  docker-compose build --no-cache
  docker-compose up
  ```

- Shutting down:

  ```bash
  docker-compose down
  ```

### 3. Developing Microservices

- Each microservice has its own **Dockerfile** and runs a **Flask API**.
- Example **Dockerfile** for a microservice:

  ```dockerfile
  FROM python:3.9-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY . .
  CMD ["python", "app.py"]
  ```

- Example **Flask API** (`app.py`):

  ```python
  from flask import Flask, request, jsonify
  app = Flask(__name__)

  @app.route('/predict', methods=['POST'])
  def predict():
      data = request.json
      return jsonify({'result': 'success', 'data': data})

  if __name__ == '__main__':
      app.run(host='0.0.0.0', port=5000)
  ```

### 4. Monitoring and API Calls

- Use **Postman** to monitor and make API calls to the Flask microservices.
  - Create a new collection in Postman.
  - Add requests to the collection for each endpoint you want to test.
  - Add the case you want to tret to the `/dicom` folder
  - Example request to test the `/predict` endpoint:
    - Method: POST
    - URL: `http://localhost:5000/run/vascular_segmentation?directory=Serie0`
    - Body: JSON
      ```json
      {
        "dictionary": "Serie"
      }
      ```
- Frontend in server.py:

  - The server.py file includes a simple frontend built using Flask's templating engine (Jinja2)
    and static files (HTML, CSS, JavaScript).

  - The frontend serves as a user interface to interact with the microservices,
    displaying results and status updates.

  - Static files are stored in the server/static/ directory,
    and templates are located in server/templates/.

### 5. Scaling and Deployment

- To scale microservices, modify `docker-compose.yml`:
  ```yaml
  version: "3.8"
  services:
    microservice1:
      build: ./services/microservice1
      ports:
        - "5001:5000"
    microservice2:
      build: ./services/microservice2
      ports:
        - "5002:5000"
  ```

### 6. Logging and Health Checks

- Add **structured logging** to microservices:

  ```python
  import logging
  logging.basicConfig(level=logging.INFO)
  app.logger.info('Service started')
  ```

- Implement **health check endpoints**:
  ```python
  @app.route("/status/<int:task_id>", methods=["GET"])
  def task_status(task_id):
      if task_id in tasks:
          task = tasks[task_id]
          return jsonify({
              "task_id": task["task_id"],
              "microservice": task["microservice"],
              "status": task["status"],
              "ellapsed_time": task.get("ellapsed_time", "pending"),
              "result": task.get("result", "ok"),
              "created_at": task["created_at"]
          }), 200
      else:
          return jsonify({"error": "Task not found or expired"}), 404
  ```

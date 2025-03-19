from flask import Flask, request, jsonify, render_template_string
import requests
import threading
import queue
import time
import logging
import os

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

# Inicialitza la cua de tasques i el diccionari de tasques
task_queue = queue.Queue()
tasks = {}

# Configuración de los microservicios
microservices = {
    "dummy": "dummy_service:5001",
    "process_dicom": "process_dicom:5002",
    "vascular_segmentation": "vascular_segmentation:5003",
}


# Worker thread per processar les tasques
def worker():
    while True:
        task_id = task_queue.get()
        if task_id is None:  # Permet tancar el worker
            break
        task = tasks[task_id]
        task["status"] = "running"
        task["started_at"] = time.time()

        # Obté la configuració del microservei
        logging.info(task)
        microservice = task["microservice"]
        address = task["address"]
        data = task["data"]
        logging.info(f"Inentant processar task {task_id} with microservice {microservice} at {address}")
        try:
            # Envia la petició al microservei
            logging.info(f"Processing task {task_id} with microservice {microservice} at {address}")
            response = requests.post(f"http://{address}/run", json=data, timeout=3600)
            print(response)
            # Gestiona la resposta
            if response.status_code == 200:
                result = response.json()
                logging.info(result)
                task["status"] = "completed"
                task["result"] = result.get("result", "ok")  # 🔹 Només guarda el valor numèric o "ok" 
            else:
                task["status"] = "failed"
                task["result"] = {
                    "http_status": response.status_code,
                    "response_text": response.text
                }
        except Exception as e:
            logging.error(f"Error processing task {task_id}: {e}")
            task["status"] = "failed"
            task["result"] = {"error": str(e)}
        
        task["completed_at"] = time.time()  # Guardem quan finalitza
        task["ellapsed_time"] = round(task["completed_at"] - task["started_at"], 3)  # Temps en segons
       
        task_queue.task_done()

# Inicia el worker thread
worker_thread = threading.Thread(target=worker, daemon=True)
worker_thread.start()

@app.route("/run/dummy", methods=["POST"])
def run_task():
    microservice = "dummy"
    if microservice not in microservices:
        return jsonify({"error": "Service not found"}), 404

    task_id = int(time.time() * 1000)
    task = {
        "task_id": task_id,
        "microservice": microservice,
        "address": microservices[microservice],
        "status": "queued",
        "data": request.json,
        "result": None,
        "created_at": time.time(),
        "source_path": "N/A",  # 🔹 Guarda el directory si existeix
    }
    tasks[task_id] = task
    task_queue.put(task_id)

    return jsonify({"microservice": microservice, "task_id": task_id, "status": "queued"}), 202

@app.route("/run/process_dicom", methods=["GET"])
def run_task_with_directory():
    microservice = "process_dicom"
    if microservice not in microservices:
        return jsonify({"error": "Service not found"}), 404
    
    directory = request.args.get('directory').strip()
    
    if not directory:
        return jsonify({"error": "Directory parameter is required"}), 400
    
    task_id = int(time.time() * 1000)
    
    task = {
        "task_id": task_id,
        "microservice": microservice,
        "address": microservices[microservice],
        "status": "queued",  # Al principio está en cola
        "data": {"directory": directory},
        "result": None,
        "created_at": time.time(),
        "source_path": directory,  # 🔹 Guarda el directory si existeix
    }
    
    tasks[task_id] = task
    task_queue.put(task_id)  # Si tienes una cola de tareas para procesamiento
    return jsonify({"microservice": microservice, "task_id": task_id, "status": "queued"}), 202

@app.route("/run/vascular_segmentation", methods=["GET"])
def run_task_with_directory_vascular_segmentation():
    microservice = "vascular_segmentation"
    if microservice not in microservices:
        return jsonify({"error": "Service not found"}), 404
    
    directory = request.args.get('directory')
    
    if not directory:
        return jsonify({"error": "Directory parameter is required"}), 400
    
    task_id = int(time.time() * 1000)
    
    task = {
        "task_id": task_id,
        "microservice": microservice,
        "address": microservices[microservice],
        "status": "queued",  # Al principio está en cola
        "data": {"directory": directory},
        "result": None,
        "created_at": time.time(),
        "source_path": directory,  # 🔹 Guarda el directory si existeix
    }
    
    tasks[task_id] = task
    task_queue.put(task_id)  # Si tienes una cola de tareas para procesamiento
    return jsonify({"microservice": microservice, "task_id": task_id, "status": "queued"}), 202

@app.route("/status/<int:task_id>", methods=["GET"])
def task_status(task_id):
    if task_id in tasks:
        task = tasks[task_id]
        return jsonify({
            "task_id": task["task_id"],
            "microservice": task["microservice"],
            "status": task["status"],
            "ellapsed_time": task.get("ellapsed_time", "pending"),  # Si no ha acabat, posem "pending"
            "result": task.get("result", "ok"),  # Mostra "ok" si no hi ha cap resultat
            "created_at": task["created_at"]
        }), 200
    else:
        return jsonify({"error": "Task not found or expired"}), 404

@app.route("/tasks", methods=["GET"])
def get_all_tasks():
    return jsonify({"tasks": list(tasks.values())}), 200

@app.route("/", methods=["GET"])
def index():
    html_content = """
    <!DOCTYPE html>

    <html>
    <head>
        <title>AI Services Orchestrator - CMR</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                padding: 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
                background-color: #1c272c; /* Fons de la pàgina */
                color: white; /* Text blanc per contrastar */
            }
            .image-container {
                position: absolute;
                top: 10px;
                left: 10px;
            }
            h1 {
                margin-top: 120px; /* Afegir espai per a l'imatge */
                text-align: center;
            }
            table {
                width: 90%;
                border-collapse: collapse;
                margin-top: 100px;
                background: white;
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                overflow: hidden;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }
            th {
                background-color: #007bff;
                color: white;
                cursor: pointer;
            }
            th:hover {
                background-color: #0056b3;
            }
            /* Colors based on task status */
            .status-queued {
                background-color: #f0ad4e;
                color: white;
            }
            .status-running {
                background-color: #5bc0de;
                color: white;
            }
            .status-completed {
                background-color: #5cb85c;
                color: white;
            }
            .status-failed {
                background-color: #d9534f;
                color: white;
            }
  
        </style>
        <script>
            let tasks = [];
            let sortDirection = 1;
            let sortColumn = "task_id";

            async function fetchTasks() {
                try {
                    const response = await fetch('/tasks');
                    const data = await response.json();
                    tasks = data.tasks;
                    sortTasks();
                    displayTasks();
                } catch (error) {
                    console.error('Error fetching tasks:', error);
                }
            }

            function sortTasks() {
                tasks.sort((a, b) => {
                    if (a[sortColumn] < b[sortColumn]) return -1 * sortDirection;
                    if (a[sortColumn] > b[sortColumn]) return 1 * sortDirection;
                    return 0;
                });
            }

            function displayTasks() {
                const taskTable = document.getElementById('task-table-body');
                taskTable.innerHTML = '';

                tasks.forEach(task => {
                    const row = document.createElement('tr');
                    row.classList.add(`status-${task.status.toLowerCase()}`);

                    row.innerHTML = `
                        <td>${task.task_id}</td>
                        <td>${task.microservice}</td>
                        <td>${task.source_path || "N/A"}</td>  <!-- 🔹 Afegim el source path -->
                        <td>
                            ${task.status === 'running' 
                                ? '<progress value="50" max="100"></progress>' 
                                : task.status}
                        </td>
                        <td>${new Date(task.created_at * 1000).toLocaleString()}</td>
                        <td>${task.ellapsed_time !== undefined ? task.ellapsed_time + ' s' : 'pending'}</td>
                        <td>${task.result !== undefined ? task.result : 'ok'}</td>
                    `;
                    taskTable.appendChild(row);
                });
            }

            function setSort(column) {
                if (sortColumn === column) {
                    sortDirection *= -1;
                } else {
                    sortColumn = column;
                    sortDirection = 1;
                }
                sortTasks();
                displayTasks();
            }

            setInterval(fetchTasks, 2000);
            window.onload = fetchTasks;
        </script>
    </head>
    <body>
        <h1>AI Services Orchestrator - CMR</h1>
        <div class="image-container">
            <img src="{{ url_for('static', filename='logo.png') }}" alt="AAAORCH Image" width="200">
        </div>
        <table>
            <thead>
                <tr>
                    <th onclick="setSort('task_id')">Task ID</th>
                    <th onclick="setSort('microservice')">Microservice</th>
                    <th onclick="setSort('source_path')">Source Path</th>
                    <th onclick="setSort('status')">Status</th>
                    <th onclick="setSort('created_at')">Created At</th>
                    <th onclick="setSort('ellapsed_time')">Elapsed Time</   th> 
                    <th onclick="setSort('result')">Result</th>
                </tr>
            </thead>
            <tbody id="task-table-body"></tbody>
        </table>
    </body>
    </html>
    """
    return render_template_string(html_content)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

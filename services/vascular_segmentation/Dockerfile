# Usamos una imagen base de Python para CPU
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copy the server code into the container
COPY app.py ./
COPY algorithm.py ./
COPY utils ./utils  
COPY modules ./modules  


# Install required Python libraries (add a requirements.txt if needed)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu124 
RUN pip install --no-cache-dir -e /app/modules/nnUNet
RUN pip install --no-cache-dir /app/modules/hiddenlayer-master

RUN mkdir ./IN
RUN mkdir ./OUT

# Ejecuta el script predict_file.py cuando inicie el contenedor
CMD ["python", "app.py"] 
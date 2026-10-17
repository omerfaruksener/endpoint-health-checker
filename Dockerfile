FROM python:3.12-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ENTRYPOINT ile bu konteynerin artık bir "Terminal Komutu" gibi davranmasını sağlıyoruz
ENTRYPOINT ["python", "app/main.py"]


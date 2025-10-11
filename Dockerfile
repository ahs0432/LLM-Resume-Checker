# 1. Base Image
FROM python:3.11-slim

# 2. Set Environment Variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set Working Directory
WORKDIR /app

# 4. Install Dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# 5. Copy Application Code
COPY . .

# 6. Expose Port
EXPOSE 8501

# 7. Set Healthcheck
HEALTHCHECK CMD streamlit healthcheck

# 8. Define Entrypoint
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]

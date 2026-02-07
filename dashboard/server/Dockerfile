FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# FIX: If main.py is in the root of your /server folder, this works perfectly.
# If your code is in a subfolder like /server/app/main.py, use "app.main:app"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

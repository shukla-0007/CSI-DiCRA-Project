# 1. Use the official lightweight Python image
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements file and install dependencies
# We use --no-cache-dir to keep the container small
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the application code and the trained model
COPY src/ /app/src/

# 5. Expose the port the app runs on
EXPOSE 8000

# 6. Command to run the FastAPI application
# Notice we point to 'src.main:app' because the code is inside the src/ folder
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"] 
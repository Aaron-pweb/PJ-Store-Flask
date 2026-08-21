# Step 1: Base Image Selection
FROM python:3.11-slim

# Step 2: Set the Working Directory
WORKDIR /app

# Step 3: Layering - Copy dependencies first
COPY requirements.txt .

# Step 4: Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Layering - Copy the rest of the application
COPY . .

# Step 6: Define Environment Variables
ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Step 7: Expose the application port
EXPOSE 5000

# Step 8: Set the execution command
CMD ["flask", "run"]

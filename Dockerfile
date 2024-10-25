
# Use a lighter Python runtime as a parent image
FROM python:3.12.3-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements.txt first to leverage Docker cache
COPY requirements.txt /app/

# Install dependencies first
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

# Install additional packages required for spaCy language models
RUN pip install --no-cache-dir spacy && python -m spacy download en_core_web_sm

# Copy the rest of the application code into the container
COPY . /app

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Expose the port the app runs on
EXPOSE 4000

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0", "--port=4000"]

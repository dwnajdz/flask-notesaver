FROM python:3-alpine

# Create app folder 
RUN mkdir /app

# Set the working directory inside the container
WORKDIR /app

# Copy the source code to the working directory
COPY src/ .

# Install all requirements
RUN pip install -r requirements.txt
RUN pip install itsdangerous==1.1.0

# Run waitress flask server
CMD ["python", "app.py"]
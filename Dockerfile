# Set base image (host OS)
FROM python:3.9-alpine

RUN python -m pip install --upgrade pip

# By default, listen on port 5000
EXPOSE 5000
ENV FLASK_APP=app.py

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements-prod.txt .

# Install any dependencies
RUN python3 -m pip install -r requirements-prod.txt

# Copy the content of the local src directory to the working directory
COPY . .

# Specify the command to run on container start
CMD [ "python", "app.py", "flask", "run", "-h", "0.0.0.0", "-p", "5000" ]
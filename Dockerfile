# Use an official Python runtime as a parent image
FROM python:3.7-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
#RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
#ENV NAME World

# Run run.py when the container launches
CMD ["nohup", "gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "run:app", ">nohup.log", "2>&1", "&"]

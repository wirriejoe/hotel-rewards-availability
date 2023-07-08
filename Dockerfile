# Use an official Python runtime as a parent image
FROM python:3.11.3

# Set the working directory in the container to /app
WORKDIR /app

# Install necessary packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        unzip \
        xvfb \
        libxi6 \
        libgconf-2-4 \
        default-jdk \
        wget \
        libpq-dev \
    && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install
    && apt-get upgrade -y


# Chrome Driver
RUN wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/bin/chromedriver \
    && chown root:root /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Run server/search_awards.py when the container launches
CMD ["python", "server/search_awards.py"]
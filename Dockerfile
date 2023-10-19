# Dockerfile

# Use an official Python runtime as the base image
FROM python:3.8-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl build-essential wget unzip git zsh

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Set the PATH for Rust
ENV PATH="/root/.cargo/bin:${PATH}"

# Install Ngrok
RUN curl -Lo ngrok.zip https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip && \
    unzip ngrok.zip && \
    rm ngrok.zip

# Install Powerlevel10k
# RUN git clone --depth=1 https://github.com/romkatv/powerlevel10k.git /root/powerlevel10k
# RUN echo 'source /root/powerlevel10k/powerlevel10k.zsh-theme' >> ~/.zshrc
# RUN echo 'ZSH_THEME="powerlevel10k/powerlevel10k"' >> ~/.zshrc

# Copy the current directory contents into the container at /app
COPY . /app

# Upgrade pip
RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5001 available to the world outside this container
EXPOSE 5001
EXPOSE 5002

# Set the NGROK_AUTH_TOKEN environment variable
ARG NGROK_AUTH_TOKEN
ENV NGROK_AUTH_TOKEN=$NGROK_AUTH_TOKEN

# Run app.py when the container launches
CMD ["python", "app.py"]
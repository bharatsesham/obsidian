Title: A Quick Guide to Useful Docker Commands

Introduction:
Docker is an essential tool for developers, making it easier to create, deploy, and run applications using containerization. It enables applications to work in any environment, making the whole process more efficient and flexible. This blog post will introduce you to some of the most important Docker commands, helping you get up and running quickly with this powerful tool.

1. Building Docker Images:
The Docker `build` command builds an image from a Dockerfile. It's usually used in the same directory as your Dockerfile.

```bash
docker build -t my-app .
```

Here, `my-app` is the name you want to give your Docker image, and the `.` indicates that Docker should look for the Dockerfile in the current directory.

2. Running Docker Containers:
You can run a Docker container from an image using the `run` command.

```bash
docker run -d -p 5000:5000 my-app
```

The `-d` option runs the container in detached mode (in the background), and the `-p` option maps the host port to the container port.

3. Listing Docker Containers:
To list all running Docker containers, use the `ps` command. 

```bash
docker ps
```

To list all Docker containers, whether running or stopped, use `ps -a`.

```bash
docker ps -a
```

4. Accessing a Running Container's Shell:
You can use the `exec` command to access the shell of a running Docker container.

```bash
docker exec -it my-container /bin/bash
```

Here, `my-container` is the name of your running container, and `/bin/bash` opens a Bash shell in the container.

5. Stopping and Removing Docker Containers:
To stop a running Docker container, use the `stop` command.

```bash
docker stop my-container
```

After a container is stopped, you can remove it with the `rm` command.

```bash
docker rm my-container
```

6. Pulling Docker Images:
You can pull an image from Docker Hub using the `pull` command.

```bash
docker pull my-image
```

7. Pushing Docker Images:
If you want to push an image to Docker Hub, use the `push` command.

```bash
docker push my-image
```

8. Docker Logs:
To view the logs of a Docker container, use the `logs` command.

```bash
docker logs my-container
```

9. Building with Build Arguments:
Sometimes, you may need to pass build-time variables to Docker. This can be achieved using the `--build-arg` argument.

```bash
docker build --build-arg VAR=value -t my-app .
```

10. Setting Environment Variables:
You can set environment variables in Docker using the `-e` flag in the `run` command.

```bash
docker run -d -p 5000:5000 -e VAR=value my-app
```

Conclusion:
Mastering Docker commands can significantly speed up your development workflow and reduce the "it works on my machine" problem. This guide should serve as a good starting point for developers new to Docker, but remember, practice is key when it comes to learning and mastering any new tool. Happy Dockering!





# Old Post
Here is the list of commands that you would need to run to build, run and setup ngrok:

1. **Build Docker Image**:

    ```bash
    docker build -t docker-llm .
    ```

2. **Run Docker Container**:

    ```bash
    docker run -d -p 5001:5001 --name=llm-container docker-llm
    ```
   The `-d` option is used to run the container in the background (detached mode).

3. **Access the Running Docker Container's Shell**:

    ```bash
    docker exec -it llm-container /bin/bash
    ```
   If `/bin/bash` doesn't work, you might try `/bin/sh`.

4. **Start Ngrok Inside the Docker Container**:

    ```bash
    ./ngrok http 5001
    ```
   
Please remember to replace `docker-llm` with your Docker image name and `llm-container` with the name you want to give to your Docker container. Also, be sure to be in the Dockerfile's directory while building the Docker image.

This will provide you with an HTTP and HTTPS URL to access your application from the internet.

Also, please be aware that this setup is suitable for development or testing purposes, but not for production use. For a production environment, you'd typically use a proper web server setup with a reverse proxy and SSL configuration.
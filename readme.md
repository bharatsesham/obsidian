Quick Guide to Run Docker Commands.

Introduction:
Docker is an essential tool for developers, making it easier to create, deploy, and run applications using containerization. It enables applications to work in any environment, making the whole process more efficient and flexible. This blog post will introduce you to some of the most important Docker commands, helping you get up and running quickly with this powerful tool.

1. Building Docker Images:
The Docker `build` command builds an image from a Docker file. It's usually used in the same directory as your Dockerfile.

```bash
docker build --build-arg NGROK_AUTH_TOKEN=<your_ngrok_auth_token> -t docker-llm .
```

Here, `docker-llm` is the name you want to give your Docker image, and the `.` indicates that Docker should look for the Dockerfile in the current directory.

2. Running Docker Containers:
You can run a Docker container from an image using the `run` command.

```bash
docker run -d -p 5001:5001 --name=llm-container docker-llm
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

4. Start the Docker Container: 
To start a running Docker container, use the `start` command.

```bash
docker start llm-container
```

5. Accessing a Running Container's Shell:
You can use the `exec` command to access the shell of a running Docker container.

```bash
docker exec -it llm-container /bin/bash
```

Here, `my-container` is the name of your running container, and `/bin/bash` opens a Bash shell in the container.

6. Stopping and Removing Docker Containers:
To stop a running Docker container, use the `stop` command.

```bash
docker stop my-container
```

After a container is stopped, you can remove it with the `rm` command.

```bash
docker rm my-container
```
Run Ngrok commands after running `docker exec`: 

7. **Inside the Docker container shell, authenticate your ngrok instance**. Replace `your_auth_token` with the auth token from your ngrok account. You can find this token on the "Auth" page of the ngrok dashboard:

```bash
./ngrok authtoken your_auth_token
```

8. **Start ngrok inside the Docker container**:

```bash
./ngrok http --hostname=ml-engine.ngrok.app 5001
```

Remember, the authentication step needs to be performed every time a new Docker container is run from the image. This is because the Docker container does not persist the state between restarts, so the authenticated ngrok state is lost when the Docker container is stopped.

Unfortunately, it's not advisable to put your ngrok authentication token directly in your Dockerfile, as this would be a security risk. Anyone who has access to the Dockerfile would be able to see and use your ngrok auth token.

Remember that this setup is mainly for development purposes. For a more secure and production-ready setup, consider using environment variables for sensitive data like the ngrok auth token, and a production-grade reverse proxy setup (like Nginx or Apache) for exposing your application to the internet.


9. Pulling Docker Images:
You can pull an image from Docker Hub using the `pull` command.

```bash
docker pull my-image
```

10. Pushing Docker Images:
If you want to push an image to Docker Hub, use the `push` command.

```bash
docker push my-image
```

11. Docker Logs:
To view the logs of a Docker container, use the `logs` command.

```bash
docker logs my-container
```

12. Building with Build Arguments:
Sometimes, you may need to pass build-time variables to Docker. This can be achieved using the `--build-arg` argument.

```bash
docker build --build-arg VAR=value -t my-app .
```

13. Setting Environment Variables:
You can set environment variables in Docker using the `-e` flag in the `run` command.

```bash
docker run -d -p 5000:5000 -e VAR=value my-app
```

Make sure to create an account at https://ngrok.com/ and use the Authtoken from the account. Also, replace the URL in the index.html with the ngrok URL when created.  

Conclusion:
Mastering Docker commands can significantly speed up your development workflow and reduce the "it works on my machine" problem. This guide should serve as a good starting point for developers new to Docker, but remember, practice is key when it comes to learning and mastering any new tool. Happy Dockering!

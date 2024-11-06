# SATX-Campaign-Finance

## Running in Docker 
This assumes Docker is [installed](https://docs.docker.com/desktop/install/mac-install/) and running on your computer. See [data-210/dev-resources](https://github.com/data-210/dev-resources?tab=readme-ov-file#docker) for more instruction and explanation of Docker terminology. 

1. Open a terminal via your preferred method (Terminal, iTerm2, or from within your IDE such as VSCode) and navigate to your local repository.

2. Build a Docker image from the Dockerfile. Replace `$IMAGE_NAME` with whatever variable you want to use.
```bash
docker build -t $IMAGE_NAME .
```

3. Run the container
```bash
docker run -p 8050:8050 $IMAGE_NAME
```
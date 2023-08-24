# Pickpod Docker

Build the docker (from the parent folder):

```
docker build -t my-pickpod -f docker/Dockerfile .
```

Use the docker
```
docker run -d -v ~/.cache:/root/.cache -p 8051:8051 --gpus all --ipc=host my-pickpod
```

Then visit `http://127.0.0.1:8051` in the browser.

(The flag `-v ~/.cache:/root/.cache` is used to avoid downloading model weights repeatedly, and thus is optional.)



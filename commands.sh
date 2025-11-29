# running a simple valkey for testing
podman run -d -p 6379:6379 -it docker.io/valkey/valkey:latest

podman run -d --name worst-authy -p 5020:5020 worst/worst-auth:0.5.0

git pull && sudo docker rm umalat --force && sudo docker build -t nkrokhmal/umalat:latest -f Dockerfile.prod . && sudo docker run --name umalat -d -p 5000:5000 nkrokhmal/umalat:latest

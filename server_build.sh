git pull && sudo docker rm umalat --force && sudo docker build -t nkrokhmal/umalat:dev -f Dockerfile.prod . && sudo docker run --name umalat -d -p 5000:5000 nkrokhmal/umalat:dev

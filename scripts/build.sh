sh save_batches.sh &&
cd .. &&
git checkout db/prod/  &&
git pull &&
docker-compose down &&
docker-compose up --build -d &&
cd scripts &&
sleep 7 &&
sh upload_batches.sh

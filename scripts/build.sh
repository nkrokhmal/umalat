sh save_batches.sh &&
cd .. &&
git checkout db/prod/data.sqlite  &&
git pull &&
docker-compose -f docker-compose-test.yaml up --build &&
docker-compose down &&
docker-compose up --build -d &&
cd scripts &&
sleep 60 &&
sh upload_batches.sh

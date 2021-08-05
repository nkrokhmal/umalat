sh save_batches.sh &&
cd .. &&
git checkout db/prod/data.sqlite  &&
git pull &&
python tests/run_tests.py &&
docker-compose down &&
docker-compose up --build -d &&
cd scripts &&
sleep 7 &&
sh upload_batches.sh

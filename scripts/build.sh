cd .. && cd scripts && sh save_last_batches.sh && cd .. && git checkout . && git pull && docker-compose up --build -d && cd scripts && sleep 5 && sh upload_last_batches.sh

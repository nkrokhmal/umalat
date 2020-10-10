Команда для сборки докер контейнера
```sh
  docker build -t registry/name .
```

Запуск контейнера
```sh
  docker run -d -p 5000:5000 registry/name .
```

Контейнер можно спулить
```sh
  docker push nkrokhmal/umalat-front:latest
```

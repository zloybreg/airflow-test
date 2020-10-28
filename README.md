## Описание

* За основу Docker образа взят [Ubuntu 18.04](https://hub.docker.com/_/ubuntu)
* Вторым слоем установил Python 3.8. Команду установки взял из образа [python:3.8-slim-buster](https://hub.docker.com/_/python/). 
Убрал GPG ключи.
* Далее из простора github выбрал самый "звездный" репозиторий [puckel/docker-airflow](https://github.com/puckel/docker-airflow)
* Поменял основу образа на свой образ с Ubuntu.
* Были проблемы с "sql-alchemy=1.3.20". Решил вопрос даунгрейдом до 1.3.15.
* Дополнительно ставил pip пакет "typing_extensions".
* Настройки по конфигурации сервера Airflow не стал менять ради экономии времени. Да и народ говорит, что почти prod-ready 

## Запуск

Основной образ лежит в Docker Hub. "Поднять" вебсервер можно сразу запустив команду:

    docker-compose up --build

- Airflow: [localhost:8080](http://localhost:8080/)

## Установка
Образ с Ubuntu 18.04 лежит в папке *ubuntu_image*.
    
    cd ubuntu_image
    docker build --rm -t zloybreg/ubuntu:18.04 .
    
Далее переходим в корневую папку и "собираем" проект

    docker-compose up --build


## Тестовые DAGи
Тестовые даги лежат в папке *./dags* метафайлы для конфигурации DAGов в папке *./meta*  

Первый метафайл тестового DAGа прописан в переменной среды docker-compose. Это базовый пример реализации 
тасков и связей между ними
     
    - AIRFLOW_VAR_META_PATH1=./meta/meta_file1.json

Второй кейс более сложный с использованием шаблонов Jinja и переменных xcom для передачи данных между тасками.
Путь до второго второго метафайла можно "прокинуть" через Админ панель. Или задать в коде, 
**название перменной** *meta_path2*. В текущем варианте так же прокинут через docker compose
    
    - AIRFLOW_VAR_META_PATH2=./meta/meta_file2.json
    
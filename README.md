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

Первый метафайл тестового DAGа прописан в переменной среды docker-compose
     
    - AIRFLOW_VAR_META_PATH=./meta/test_case1.json

Путь до второго второго метафайла можно "прокинуть" через Админ панель. Или задать в коде, 
**название перменной** *meta_path2*
    
    meta_file_path = Variable.get("meta_path2")


К сожалению не успел по времени сделать второй тест-кейс (сложный вариант). Наработки лежат в файле *test_case2.py*  
Не совсем понял, как можно передать *python* код через *json* файл. Поэтому начал реализацию через передачу
названия метода как обычный *string* и привести тип к *Callable*. 
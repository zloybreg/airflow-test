from datetime import datetime

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.models import Variable, BaseOperator

import json


def create_dag(_dag_name: str, _default_args: dict) -> DAG:
    """
    Создаем DAG динамически.

    :param _dag_name: название DAG
    :param _default_args: аргументы DAG

    :return: новый DAG
    """

    _dag = DAG(_dag_name, default_args=_default_args, schedule_interval='@once')

    return _dag


def create_task(
        _dag: DAG,
        _task_id: str,
        _trigger_rule: str,
        _operator_type: str,
        _command: str
) -> BashOperator:
    """
    Создаем таски

    :param _dag: DAG
    :param _trigger_rule: триггер
    :param _operator_type: тип оператора
    :param _task_id: имя таска
    :param _command: bash команда для таска

    :return: BashOperator
    """
    _task = BashOperator(
        task_id=_task_id,
        bash_command=_command,
        trigger_rule=_trigger_rule,
        dag=_dag,
    )

    return _task


def read_meta_file(_meta_file_path: str) -> dict:
    """
    Загружаем из переменной среды путь до файла с meta данными.

    :param: путь к файлу метаданных

    :return: сериализованный json
    """
    with open(_meta_file_path, 'r') as f:
        f = json.load(f)
        return f


def parse_dag_meta_json(_data: dict) -> tuple:
    """
    Парсим метаданные для DAG

    :param: данные json

    :return: dag_name, default_args, tasks
    """
    _dag_name: str = _data.get('dag_name')
    _default_args: dict = _data.get('default_args')
    _tasks: [] = _data.get('tasks')
    _dependencies: [] = _data.get('dependencies')

    return _dag_name, _default_args, _tasks, _dependencies


# импортируем Airflow переменную с ссылкой до метаданных
meta_file_path = Variable.get("meta_path1")

# считываем файл с метданными
data = read_meta_file(meta_file_path)

# возвращаем кортеж с данными
dag_name, default_args, tasks, dependencies = parse_dag_meta_json(data)

# настраиваем когфигурацию ДАГа
default_args = {
    "owner": default_args["owner"],
    "start_date": datetime.strptime(default_args["start_date"], "%d%m%Y"),
}

# создаем DAG для простого-прямого примера связывания
dag = create_dag(dag_name, default_args)

# будем записывать Таски в dict, что бы свзать их по именам
task1: {str: BaseOperator} = {}

# генерим таски и пакуем в dict
for task in tasks:
    task1[task['task_id']] = create_task(dag, task['task_id'], task['trigger_rule'], task['operator_type'],
                                         task['command'])

# связываем такси между собой вытаскивая из коллекции по именам
for dep in dependencies:
    task1[dep['task_id_from']].set_downstream(task1[dep['task_id_to']])

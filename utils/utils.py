from airflow import DAG
from airflow.operators.bash_operator import BashOperator

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


def create_bash_task(_task_id: str, _bash_command: str, _params: dict, _dag: DAG) -> BashOperator:
    """
    Создаем таски

    :param _task_id: имя таска
    :param _bash_command: bash команда для таска
    :param _params: перменные для заполнения Jinja шаблонов
    :param _dag: DAG

    :return: BashOperator
    """
    _task = BashOperator(
        task_id=_task_id,
        bash_command=_bash_command,
        params=_params,
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
    _dag_name: str = _data['dag_name']
    _default_args: dict = _data['default_args']
    _tasks: [] = _data['tasks']

    return _dag_name, _default_args, _tasks

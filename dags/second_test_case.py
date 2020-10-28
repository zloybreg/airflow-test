from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.models import Variable, BaseOperator

from datetime import datetime
import json
import random


# отправляем xcom значение
def producer(*args, **kwargs):
    kwargs['ti'].xcom_push('key', 'World')
    print('Send half text')


# принимаем xcom параметр
def consumer(*args, **kwargs):
    req = kwargs['ti'].xcom_pull(task_ids='Second', key='key')
    print('Hello, {}'.format(req))


# ветвление выбираем между тасками. Можно было бы реализовать сложный пример с передачей xcom значения так же рандомно.
# Например, producer отправляет одно из значений ['Second', 'Fourth'], тут принимаем значение и дальше выбираем. Но в
# целом пример получается полноценным
def branch(**context):
    # выбираем рандомно любой таск из нашего списка
    _tasks: [] = ['Second', 'Fourth']
    return random.choice(_tasks)


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
        _command: str,
        _params: dict = None
) -> BashOperator:
    """
    Создаем таски

    :param _dag: DAG
    :param _trigger_rule: триггер
    :param _operator_type: тип оператора
    :param _task_id: имя таска
    :param _command: команда для таска
    :param _params: перменные для заполнения Jinja шаблонов

    :return: BashOperator
    """
    _task = None

    if _operator_type.lower() == 'bash':
        _task = BashOperator(
            task_id=_task_id,
            bash_command=_command,
            trigger_rule=_trigger_rule,
            params=_params,
            dag=_dag,
        )
    elif _operator_type.lower() == 'python':
        _task = PythonOperator(
            task_id=_task_id,
            python_callable=globals()[_command],
            trigger_rule=_trigger_rule,
            dag=_dag,
            provide_context=True
        )
    elif _operator_type.lower() == 'branch':
        _task = BranchPythonOperator(
            task_id=_task_id,
            python_callable=globals()[_command],
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
meta_file_path = Variable.get("meta_path2")

# считываем файл с метданными
data = read_meta_file(meta_file_path)

# возвращаем кортеж с данными
dag_name, default_args, tasks, dependencies = parse_dag_meta_json(data)

# настраиваем когфигурацию ДАГа
default_args = {
    "owner": default_args["owner"],
    "start_date": datetime.strptime(default_args["start_date"], "%d%m%Y")
}

# создаем DAG для простого-прямого примера связывания
dag = create_dag(dag_name, default_args)

# будем записывать Таски в dict, что бы свзать их по именам
task1: {str: BaseOperator} = {}

for task in tasks:
    task1[task['task_id']] = create_task(dag, task['task_id'], task['trigger_rule'], task['operator_type'],
                                         task['command'])

# связываем такси между собой вытаскивая из коллекции по именам
for dep in dependencies:
    task1[dep['task_id_from']].set_downstream(task1[dep['task_id_to']])

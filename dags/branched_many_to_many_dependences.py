from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.branch_operator import BaseBranchOperator
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.models import Variable

from datetime import timedelta, datetime
import json
import random


def create_dag(_dag_name: str, _default_args: dict) -> DAG:
    """
    Создаем DAG динамически.

    :param _dag_name: название DAG
    :param _default_args: аргументы DAG

    :return: новый DAG
    """

    _dag = DAG(_dag_name, default_args=_default_args, schedule_interval='@once')

    return _dag


def create_bash_task(_task_id: str, _bash_command: str, _params: dict, _dag: DAG, _xcom: bool) -> BashOperator:
    """
    Создаем таски

    :param _task_id: имя таска
    :param _bash_command: bash команда для таска
    :param _params: перменные для заполнения Jinja шаблонов
    :param _dag: DAG
    :param _xcom: коммуникация между тасками

    :return: BashOperator
    """
    _task = BashOperator(
        task_id=_task_id,
        bash_command=_bash_command,
        params=_params,
        dag=_dag,
        xcom_push=_xcom
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


# импортируем Airflow переменную с ссылкой до метаданных
meta_file_path = Variable.get("meta_path")

# считываем файл с метданными
data = read_meta_file(meta_file_path)

# возвращаем кортеж с данными
dag_name, default_args, tasks = parse_dag_meta_json(data)

# настраиваем когфигурацию ДАГа
default_args = {
    "owner": default_args["owner"],
    "depends_on_past": default_args["depends_on_past"],
    "start_date": datetime.strptime(default_args["start_date"], "%d%m%Y"),
    "email": default_args["email"],
    "email_on_failure": default_args["email_on_failure"],
    "email_on_retry": default_args["email_on_retry"],
    "retries": int(default_args["retries"]),
    "retry_delay": timedelta(minutes=int(default_args["retry_delay"]))
}


def branch_func(**context):
    """
    функция ветвления между тасками
    :param context:
    :return: название тасков
    """
    # выбираем рандомно любой таск из нашего списка
    return random.choice([_task['task_id'] for _task in tasks])


# создаем DAG
dag = create_dag('branch_many_to_many', default_args)

# пустой Таск для начала
start_task = DummyOperator(
    task_id='start',
    dag=dag
)

# пустой Таск для окончания
end_task = DummyOperator(
    task_id='end',
    dag=dag
)

branch_task = BranchPythonOperator(
    task_id='branch_operator',
    dag=dag,
    provide_context=True,
    python_callable=branch_func
)


# создаем Таски
for i, task in enumerate(tasks):
    my_task1 = create_bash_task(task['task_id'], task['command'], task['params'], dag,
                                task['xcom'])

    my_task2 = create_bash_task('{}_{}'.format(i, task['task_id']), task['command'], task['params'], dag,
                                task['xcom'])

    start_task >> branch_task >> my_task1 >> my_task2 >> end_task

from airflow.configuration import conf
from airflow.models import DagBag
from airflow.models.baseoperator import BaseOperator
from airflow.models.baseoperatorlink import BaseOperatorLink
from airflow.models.taskinstancekey import TaskInstanceKey

from os.path import abspath, dirname, relpath
from urllib.parse import quote
from dags_explorer.views import DagsExplorerView


class ExplorerLink(BaseOperatorLink):
    name = "View in Folder"

    def get_link(self, operator: BaseOperator, *, ti_key: TaskInstanceKey):
        dag_bag = DagBag(include_examples=False)
        dag = dag_bag.get_dag(ti_key.dag_id)
        if not dag or not dag.fileloc:
            return DagsExplorerView.root_base

        dags_folder = abspath(conf.get("core", "dags_folder"))
        dag_file_dir = abspath(dirname(dag.fileloc))
        rel_path = quote(relpath(dag_file_dir, dags_folder))

        # https://github.com/apache/airflow/issues/43252
        # base_url = conf.get("webserver", "base_url").rstrip("/")
        # return f"{base_url}/dags_explorer/{rel_path}"
        return f"{DagsExplorerView.root_base}/{rel_path}"



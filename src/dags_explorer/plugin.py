from airflow.plugins_manager import AirflowPlugin
from dags_explorer.links import ExplorerLink
from dags_explorer.views import DagsExplorerView
from flask import Blueprint
from os.path import dirname, join

class DagsExplorerPlugin(AirflowPlugin):
    name = "dags_explorer_plugin"
    flask_blueprints = [
        Blueprint("dags_explorer_bp", __name__, template_folder=join(dirname(__file__), "templates"))
    ]
    appbuilder_views = [
        {
            "category": "Extras",
            "name": "Explorer",
            "view": DagsExplorerView()
        }
    ]
    global_operator_extra_links = [
        ExplorerLink(),
    ]

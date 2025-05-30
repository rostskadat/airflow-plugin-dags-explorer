from airflow.plugins_manager import AirflowPlugin
from dag_creator.views import DagCreatorView
from flask import Blueprint


class DagCreatorPlugin(AirflowPlugin):
    name = "dag_creator_plugin"
    flask_blueprints = [
        Blueprint("dag_creator_bp",
                  __name__,
                  template_folder='templates',
                  static_folder='static'
                  )
    ]
    appbuilder_views = [
        {
            "category": "Extras",
            "name": "Dag Creator",
            "view": DagCreatorView()
        }
    ]

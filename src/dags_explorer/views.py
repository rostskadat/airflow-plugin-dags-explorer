import os

from airflow.auth.managers.models.resource_details import DagAccessEntity, DagDetails
from airflow.configuration import conf
from airflow.models import DagBag
from airflow.utils.state import State
from airflow.www import auth
from airflow.www.extensions.init_auth_manager import get_auth_manager

from flask_appbuilder import expose, BaseView as AppBuilderBaseView
from flask import current_app, g
from itsdangerous import URLSafeSerializer
from os.path import abspath, dirname, exists, isdir, join, relpath


class DagsExplorerView(AppBuilderBaseView):

    root_base = "/dagsexplorerview"

    @expose('/')
    @expose('/<path:subpath>')
    @auth.has_access_view()
    def list(self, subpath=None):
        dags_folder = conf.get('core', 'dags_folder')
        base_path = abspath(dags_folder)
        current_path = join(base_path, subpath) if subpath else base_path

        # Build breadcrumb
        rel_path = relpath(current_path, base_path)
        parts = rel_path.split(os.sep) if rel_path != '.' else []
        breadcrumb = [("Root", self.root_base)]
        running_path = ""
        for part in parts:
            running_path = join(running_path, part)
            breadcrumb.append((part, f"{self.root_base}/{running_path}"))

        # List folders and dags
        folders = []
        dags = []
        if exists(current_path):
            for entry in os.listdir(current_path):
                full_path = join(current_path, entry)
                if isdir(full_path) and entry != '__pycache__':
                    folders.append(entry)

        # Load dags using DagBag and filter those in current path
        file_tokens = {}
        dag_bag = DagBag(dag_folder=current_path, include_examples=False)
        for dag_id, dag in dag_bag.dags.items():
            if dirname(dag.fileloc) == current_path:
                dag.can_edit = get_auth_manager().is_authorized_dag(
                    method="PUT", details=DagDetails(id=dag.dag_id), user=g.user
                )
                can_create_dag_run = get_auth_manager().is_authorized_dag(
                    method="POST",
                    access_entity=DagAccessEntity.RUN,
                    details=DagDetails(id=dag.dag_id),
                    user=g.user,
                )
                dag.can_trigger = dag.can_edit and can_create_dag_run
                dag.can_delete = get_auth_manager().is_authorized_dag(
                    method="DELETE", details=DagDetails(id=dag.dag_id), user=g.user
                )
                url_serializer = URLSafeSerializer(current_app.config["SECRET_KEY"])
                file_tokens[dag.dag_id] = url_serializer.dumps(dag.fileloc)
                dags.append(dag)

        state_color_mapping = State.state_color.copy()
        state_color_mapping["null"] = state_color_mapping.pop(None)

        return self.render_template("dags_explorer.html.j2",
                                    breadcrumb=breadcrumb,
                                    folders=folders,
                                    dags=dags,
                                    current_path=rel_path,
                                    file_tokens=file_tokens,
                                    state_color=state_color_mapping,
                                    auto_refresh_interval=conf.getint("webserver", "auto_refresh_interval"),
                                    )


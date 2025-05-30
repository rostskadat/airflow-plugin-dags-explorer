import os
import boto3

from airflow.configuration import conf
from airflow.models import Variable
from airflow.utils.log.logging_mixin import LoggingMixin
from croniter import croniter
from datetime import datetime

from jinja2 import Environment, FileSystemLoader
from os.path import dirname, join

class DagGenerator(LoggingMixin):

    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket = Variable.get("S3_DAG_BUCKET", default_var="s3_dag_bucket")

    def is_valid_cron(self, expr: str) -> bool:
        try:
            croniter(expr, datetime.now())
            return True
        except (ValueError, KeyError):
            return False

    def sanitize(self, name):
        return ''.join(c if c.isalnum() or c in ('_', '-') else '_' for c in name.lower())

    def render_dag(self, data):
        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        env = Environment(loader=FileSystemLoader(template_path))
        template = env.get_template('power_mgmt_dag.py.j2')
        return template.render(**data)

    def upload_to_s3(self, content, key):
        new_dag = join(conf.get('core', 'dags_folder'), key)
        os.makedirs(dirname(new_dag), exist_ok=True)
        with open(new_dag, "w") as f:
            f.write(content)
        # self.s3_client.put_object(Body=content, Bucket=self.bucket, Key=key)

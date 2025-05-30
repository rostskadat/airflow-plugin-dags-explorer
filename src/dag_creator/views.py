from airflow.www import auth
from airflow.www.app import csrf

from flask_appbuilder import expose, BaseView
from flask import request, redirect, flash, url_for
from dag_creator.dag_generator import DagGenerator

# REF: https://flask-appbuilder.readthedocs.io/en/latest/views.html

class DagCreatorView(BaseView):

    root_base = "/dag_creator"

    default_view = "index"

    @expose('/', methods=["GET", "POST"])
    @auth.has_access_view()
    def index(self):
        if request.method == 'POST':
            csrf.protect()  # Ensure CSRF protection on form submission

            region = request.form['region']
            environment = request.form['environment']
            application = request.form['application']
            start_schedule = request.form['start_schedule'] or 'None'
            stop_schedule = request.form['stop_schedule'] or 'None'
            details_types = request.form.getlist('detail_type')
            details_values = request.form.getlist('detail_value')

            application_details = [
                {'type': t, 'value': v} for t, v in zip(details_types, details_values)
            ]

            # Validate unique types
            types = [d['type'] for d in application_details]
            if len(types) != len(set(types)):
                flash("Each application detail type must be unique.", "danger")
                return redirect(request.url)

            dag_gen = DagGenerator()
            if start_schedule != 'None' and not dag_gen.is_valid_cron(start_schedule):
                flash("Invalid cron expression for start schedule.", "danger")
                return redirect(request.url)

            if stop_schedule != 'None' and not dag_gen.is_valid_cron(stop_schedule):
                flash("Invalid cron expression for stop schedule.", "danger")
                return redirect(request.url)

            sanitized_app = dag_gen.sanitize(application)

            dag_content = dag_gen.render_dag({
                'region': region,
                'environment': environment,
                'application': sanitized_app,
                'start_schedule': start_schedule if start_schedule != 'None' else None,
                'stop_schedule': stop_schedule if stop_schedule != 'None' else None,
                'application_details': application_details
            })

            key = f"dag_creator/{environment}/{region}/{sanitized_app}.py"
            dag_gen.upload_to_s3(dag_content, key)
            flash("DAG successfully created and uploaded to S3", "success")
            return redirect(url_for('DagCreatorView.index'))

        return self.render_template('dag_creator.html.j2',
                                    regions=['eu-west-1', 'eu-central-1'],
                                    environments=['snd', 'dev', 'uat', 'pro'],
                                    application_details=["rds_instance_tags","rds_cluster_tags","ec2_instance_tags","cw_alarms_tags","asg_group_name","asg_desired_capacity","ecs_cluster_tags","ecs_services","tz"],
                                    )


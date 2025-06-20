from flask import request, render_template
from .models import db, Job, JobLog
from .schemas import JobSchema, JobLogSchema
from . import db
from marshmallow import ValidationError

def register_routes(app, api) :
    # Get    : /jobs        | to get all the jobs details               (only master table)
    # Get    : /jobs/:id    | to get jobid = id details                 (master and log table)
    # Post   : /jobs        | to create a new job                       (update master and log table)
    # Post   : /jobs/:id    | to update the job details with jobid = id (update master table)
    @app.route("/jobs",methods=["GET"])
    def view_jobs():
        jobs = Job.query.all()
        return jobs
    
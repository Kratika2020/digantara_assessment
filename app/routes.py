from flask.views import MethodView
from flask import request, render_template
from flask_smorest import Blueprint
from .models import db, Job, JobLog
from .schemas import JobSchema, JobLogSchema
from . import db
from marshmallow import ValidationError

blp = Blueprint("Jobs", "jobs", url_prefix="/jobs", description="Operations on Jobs")

@blp.route("/")
class JobsList(MethodView) :
    @blp.response(200, JobSchema(many=True))
    def get(self):
        jobs = Job.query.all()
        return jobs
    

    # Get    : /jobs        | to get all the jobs details               (only master table)
    # Get    : /jobs/:id    | to get jobid = id details                 (master and log table)
    # Post   : /jobs        | to create a new job                       (update master and log table)
    # Post   : /jobs/:id    | to update the job details with jobid = id (update master table)
    

from flask.views import MethodView
from flask import request, render_template
from flask_smorest import Blueprint
from .models import db, Job, JobLog
from .schemas import JobSchema, JobLogSchema
from . import db
from marshmallow import ValidationError
from datetime import datetime

blp = Blueprint("Jobs", "jobs", url_prefix="/jobs", description="Operations on Jobs")

@blp.route("/")
class JobsList(MethodView) :
    @blp.response(200, JobSchema(many=True))
    def get(self):
        jobs = Job.query.all()
        return jobs
    
    @blp.arguments(JobSchema)
    @blp.response(201, JobSchema)
    def post(self, job_data):
        new_job = Job(**job_data)
        db.session.add(new_job)
        db.session.flush()

        nxt_run_ts = datetime.combine(new_job.startdate, new_job.starttime)
        new_log = JobLog(
                    jobid = new_job.jobid, 
                    lastrun = None,
                    nextrun = nxt_run_ts,
                    status = "pending")
        db.session.add(new_log)
        db.session.commit()

        
        return new_job
    

    

    # Get    : /jobs        | to get all the jobs details               (only master table)
    # Get    : /jobs/:id    | to get jobid = id details                 (master and log table)
    # Post   : /jobs        | to create a new job                       (update master and log table)
    # Post   : /jobs/:id    | to update the job details with jobid = id (update master table)
    

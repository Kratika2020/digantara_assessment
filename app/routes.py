from flask.views import MethodView
from flask import request, render_template, redirect, url_for
from flask_smorest import Blueprint
from .models import db, Job, JobLog
from .schemas import JobSchema, JobLogSchema, JobDetailSchema
from . import db
from marshmallow import ValidationError
from datetime import datetime

blp = Blueprint("Jobs", "jobs", url_prefix="/jobs", description="Operations on Jobs")

@blp.route("/")
class JobsList(MethodView) :
    def get(self):
        # loads form for posting new job
        if request.args.get("form") == "true":
            return render_template("job_form.html", form={}, errors={})

        # shows list of all jobs created
        jobs = Job.query.all()

        # for Swagger, API response
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return JobSchema(many=True).dump(jobs)
        
        return render_template("jobs.html", jobs=jobs)
        
    # to create a job
    def post(self):
        schema = JobSchema()
        if request.is_json:
            try:
                job_data = schema.load(request.get_json())
            except ValidationError as err:
                return {"errors": err.messages}, 400
        else:
            try:
                form = request.form.to_dict()
                form["repeat"] = "repeat" in request.form
                form["interval"] = form.get("interval") or None
                form["active"] = "active" in request.form
                job_data = schema.load(form)
            except ValidationError as err:
                print(err.messages)
                return render_template("job_form.html", errors=err.messages, form=form), 400
            
        # Create entry in Master Table
        new_job = Job(**job_data)
        db.session.add(new_job)
        db.session.commit()

        # create entry in Log table
        if new_job.active == True :
            nxt_run_ts = datetime.combine(new_job.startdate, new_job.starttime)
            new_log = JobLog(
                        jobid = new_job.jobid, 
                        lastrun = None,
                        nextrun = nxt_run_ts,
                        status = "pending")
            db.session.add(new_log)
            db.session.commit()
        

        if request.is_json:
            return {
                "message": "Job created",
                "job": JobSchema().dump(new_job)
            }, 201
        else:
            return redirect("/jobs")

    
# to fetch details of a particular job
@blp.route("/<int:id>")
class JobDetail(MethodView) :
    def get(self, id):
        job = Job.query.get_or_404(id)
        logs = JobLog.query.filter_by(jobid = job.jobid).all()

        # for Swagger, API response
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            job_schema = JobSchema()
            log_schema = JobLogSchema(many=True)
            return {
                "job": job_schema.dump(job),
                "logs": log_schema.dump(logs)
            }
        
        return render_template("job_detail.html", job=job, logs=logs)

    

    

    # Get    : /jobs        | to get all the jobs details               (only master table)
    # Get    : /jobs/:id    | to get jobid = id details                 (master and log table)
    # Post   : /jobs        | to create a new job                       (update master and log table)

    # function for Executing the jobs
    

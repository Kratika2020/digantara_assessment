from flask.views import MethodView
from flask import request, render_template, redirect
from flask_smorest import Blueprint
from .models import Job, JobLog
from .schemas import JobSchema, JobLogSchema
from . import db, ist_tz
from marshmallow import ValidationError
from datetime import datetime, timedelta

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
    @blp.doc(
        requestBody={
            "required": True,
            "content": {
                "application/json": {
                    "schema": JobSchema
                }
            }
        }
    )
    def post(self):
        # for input validation
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
        print(job_data)
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


@blp.route("/run")
class JobRun(MethodView):
    # Assumption : This endpoint executes Jobs on their scheduled Time.
    def post(self) :
        # fetch all the jobs where active = True 
        # fetch latest logs for all jobs where status = pending and nextrun < currentT.S.
        # now = datetime.now(tz = ist_tz)
        now = datetime.now()
        print(now)

        # Fetch logs where job is active, next run time has arrived and status is pending
        logs = db.session.query(JobLog).join(Job).filter(
            Job.active == True,
            JobLog.nextrun <= now,
            JobLog.status == 'pending'
            ).all()
        # if True : 
        #     job_log = JobLogSchema() 
        #     # return {"message": "Not fetched", "now": now, "logs":job_log.dump(logs)}, 200

        print(logs)
        for log in logs:
            print(f"JobID: {log.jobid}, Status: {log.status}, NextRun: {log.nextrun}")
            job = log.job  # Access the related Job instance
            exec_timestamp = log.nextrun  # Store current nextrun before update
            print("exec time",exec_timestamp)

            if not job.repeat:
                # One-time job: mark as finished and deactivate
                log.lastrun = exec_timestamp
                log.nextrun = None
                log.status = 'finished'
                job.active = False
            else:
                # Repeating job: finish current, create new JobLog with updated times
                log.status = 'finished'
                new_nextrun = exec_timestamp + timedelta(seconds = job.interval)

                new_log = JobLog(
                    jobid=job.jobid,
                    lastrun=exec_timestamp,
                    nextrun= new_nextrun,
                    status='pending'
                )
                db.session.add(new_log)

        db.session.commit()
        return {"message": "Pending job logs processed successfully."}, 200

    

    

    # Get    : /jobs                  | to get all the jobs details               (only master table)
    # Get    : /jobs/:id              | to get jobid = id details                 (master and log table)
    # Get    : /jobs?form=true        | to create job form                        (only master table and log table)
    # Post   : /jobs                  | to create a new job                       (update master and log table)

    # function for Executing the jobs
    

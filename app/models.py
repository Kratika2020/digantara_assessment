from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from datetime import datetime
from . import db


# Master Table : Job
class Job(db.Model):
    __tablename__ = "job"

    jobid = db.Column(db.Integer, primary_key = True)
    jobname = db.Column(db.String(100), nullable = False)
    startdate = db.Column(db.Date, nullable = False, default = datetime.utcnow().date)
    starttime = db.Column(db.Time, nullable = False, default = datetime.utcnow().time)
    repeat = db.Column(db.Boolean, default = False)
    interval = db.Column(db.Interval, nullable = True)
    active = db.Column(db.Boolean, default = True)

    # Relationship between Job and Joblog tables
    job_logs = db.relationship("JobLog", backref = "job", lazy = True)

    # adding check constraint on repeat-flag and interval column
    __table_args__ = (CheckConstraint("NOT repeat or interval IS NOT NULL", name = "chk_repeat_requires_interval"),)

# Log Table : JobLog
class JobLog(db.Model):
    __tablename__ = "joblog"

    logid = db.Column(db.Integer, primary_key = True)
    jobid = db.Column(db.Integer, db.ForeignKey('job.jobid'))
    lastrun = db.Column(db.DateTime)
    nextrun = db.Column(db.DateTime)
    status = db.Column(db.String(50), default = "pending")

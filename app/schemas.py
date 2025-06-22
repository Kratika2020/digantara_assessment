from marshmallow import Schema, fields, validates, ValidationError, validates_schema
from datetime import datetime, timezone

# Schema for Model: Job
class JobSchema(Schema):
    jobid = fields.Integer(dump_only = True)
    jobname = fields.String(required = True)
    startdate = fields.Date(allow_none = False)
    starttime = fields.Time(allow_none = False)
    repeat = fields.Boolean(missing = False)
    interval = fields.Integer(allow_none = True)
    active = fields.Boolean(missing = True)

    # validation of link between Repeat flag and Interval column
    @validates_schema
    def validate_interval_if_repeat(self, data, **kwargs):
        if data.get("repeat") and not data.get("interval"):
            raise ValidationError("Interval is required when Repeat flag is set.", field_name = "interval")
        if not data.get("repeat") and data.get("interval"):
            raise ValidationError("Interval should not be set when Repeat flag is not set.", field_name = "interval")
    
    @validates("jobname")
    def validate_jobname(self, value):
        if len(value.strip()) < 3 :
            raise ValidationError("Job Name must be at least of 3 characters.")
        
    @validates_schema
    def validate_start_date_time(self, data, **kwargs):
        timestamp = datetime.combine(data["startdate"], data["starttime"])
        if timestamp < datetime.now():
            raise ValidationError("Job start datetime must be in future.", field_name = "startdate")

# Schema for Model: JobLog       
class JobLogSchema(Schema):
    logid = fields.Integer(dump_only = True)
    jobid = fields.Integer(required = True)
    lastrun = fields.DateTime(dump_only = True)
    nextrun = fields.DateTime(dump_only = True)
    status = fields.String(required = True)

    # validation of allowed values in column: status
    @validates("status")
    def validate_status(self, value):
        allowed = {"pending", "finished", "failed"}
        if value.lower() not in allowed :
            raise ValidationError(f"Status must be one of {allowed}")
        
class JobDetailSchema(Schema):
    job = fields.Nested(JobSchema)
    logs = fields.List(fields.Nested(JobLogSchema))
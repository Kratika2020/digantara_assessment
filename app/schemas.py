from marshmallow import Schema, fields, validates, ValidationError, validates_schema
from datetime import datetime

# Schema for Model: Job
class JobSchema(Schema):
    jobid = fields.Int(dump_only = True)
    jobname = fields.String(required = True)
    startdate = fields.Date(allow_none = False)
    starttime = fields.Time(allow_none = False)
    repeat = fields.Boolean(missing = False)
    interval = fields.TimeDelta(precision = 'seconds', allow_none = True)
    active = fields.Boolean(missing = True)

    # validation of link between Repeat flag and Interval column
    @validates_schema
    def validate_interval_if_repeat(self, data, **kwargs):
        if data.get("repeat") and not data.get("interval"):
            raise ValidationError("Interval is required when Repeat flag is set.", field_name = "interval")

# Schema for Model: JobLog       
class JobLogSchema(Schema):
    logid = fields.Int(dump_only = True)
    jobid = fields.Int(required = True)
    lastrun = fields.DateTime(dump_only = True)
    nextrun = fields.DateTime(dump_only = True)
    status = fields.String(required = True)

    # validation of allowed values in column: status
    @validates("status")
    def validate_status(self, value):
        allowed = {"pending", "finished", "failed"}
        if value.lower() not in allowed :
            raise ValidationError(f"Status must be one of {allowed}")
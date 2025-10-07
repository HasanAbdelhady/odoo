from odoo import models, fields, api
from datetime import datetime, date
from odoo.exceptions import ValidationError
import pytz


class Session(models.Model):
    _name = "gym.session"
    _description = "Session"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    coach_id = fields.Many2one(comodel_name="gym.coach", string="Coach Name")
    trainee_id = fields.Many2one(comodel_name="gym.trainee", string="Trainee Name")

    coach_name = fields.Char(related="coach_id.name", string="Coach name")
    coach_image = fields.Binary(
        related="coach_id.coach_image", string="Coach Photo", readonly=True
    )
    coach_phone = fields.Char(
        related="coach_id.phone_number", string="Coach Phone", readonly=True
    )
    session_start_time = fields.Datetime(
        string="Session Start Time", required=True, tracking=True
    )
    session_end_time = fields.Datetime(
        string="Session End Time", required=True, tracking=True
    )
    # Related fields for trainee
    trainee_name = fields.Char(
        related="trainee_id.name",
        string="Trainee Name",
    )
    trainee_image = fields.Binary(
        related="trainee_id.trainee_image", string="Trainee Photo", readonly=True
    )
    trainee_phone = fields.Char(
        related="trainee_id.phone_number", string="Trainee Phone", readonly=True
    )

    membership_id = fields.Many2one(comodel_name="gym.membership", String="Membership")

    session_title = fields.Char(
        String="Title", compute="_set_session_title", readonly=True
    )

    # will compute it using the time of the session later
    session_cost = fields.Float(
        string="Session Cost",
        compute="_compute_session_cost",
        store=True,
        readonly=True,
    )
    in_time = fields.Boolean(
        string="In time?", compute="_compute_session_cost", store=True
    )
    out_time = fields.Boolean(
        string="Overtime?", compute="_compute_session_cost", store=True
    )
    is_attended_by_coach = fields.Boolean(string="Did the coach attend?")
    is_attended_by_trainee = fields.Boolean(string="Did the trainee attend?")
    coach_cost_per_hour_normal = fields.Float(
        related="coach_id.coach_cost_per_hour_normal",
        string="Coach Cost Per Hour (in time)",
    )
    coach_cost_per_hour_overtime = fields.Float(
        related="coach_id.coach_cost_per_hour_overtime",
        string="Coach Cost Per Hour (Overtime)",
    )

    @api.depends("coach_name", "trainee_name", "trainee_phone")
    def _set_session_title(self):
        for record in self:
            if record.coach_name and record.trainee_name and record.trainee_phone:
                record.session_title = f"""Trainee: {record.trainee_name} - Phone: {record.trainee_phone} -
                Coach: {record.coach_name}
                """
            else:
                self.session_title = ""

    @api.depends(
        "session_start_time",
        "session_end_time",
        "coach_id",
        "coach_id.schedule_ids",
        "coach_cost_per_hour_normal",
        "coach_cost_per_hour_overtime",
    )
    def _compute_session_cost(self):
        for record in self:
            # Default values
            record.session_cost = 0.0
            record.in_time = False
            record.out_time = False

            if not (
                record.session_start_time
                and record.session_end_time
                and record.coach_id
            ):
                continue

            # Convert UTC times to user's local timezone (coach schedule is in local time)
            user_tz = pytz.timezone(self.env.user.tz or "Africa/Cairo")
            session_start_local = pytz.utc.localize(
                record.session_start_time
            ).astimezone(user_tz)
            session_end_local = pytz.utc.localize(record.session_end_time).astimezone(
                user_tz
            )

            # Get session info in local time
            session_start_hour = (
                session_start_local.hour + session_start_local.minute / 60.0
            )
            session_end_hour = session_end_local.hour + session_end_local.minute / 60.0
            session_duration = (
                record.session_end_time - record.session_start_time
            ).total_seconds() / 3600.0

            # Get day of week (in local time)
            # Python weekday(): Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
            # We want: Sat=0, Sun=1, Mon=2, Tue=3, Wed=4, Thu=5, Fri=6
            # So we shift: (weekday + 2) % 7
            day_names = [
                "saturday",
                "sunday",
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
            ]
            session_day_index = (session_start_local.weekday() + 2) % 7
            session_day_name = day_names[session_day_index]

            # Find coach's schedule for this day
            schedule = record.coach_id.schedule_ids.filtered(
                lambda s: s.day_of_week == session_day_name
            )

            if schedule:
                schedule = schedule[0]
                # Calculate overlap
                overlap_start = max(session_start_hour, schedule.time_from)
                overlap_end = min(session_end_hour, schedule.time_to)
                normal_hours = max(0, overlap_end - overlap_start)
                overtime_hours = session_duration - normal_hours

                record.in_time = normal_hours > 0
                record.out_time = overtime_hours > 0
            else:
                # No schedule = all overtime
                normal_hours = 0
                overtime_hours = session_duration
                record.out_time = True

            # Calculate cost
            record.session_cost = (
                normal_hours * record.coach_cost_per_hour_normal
                + overtime_hours * record.coach_cost_per_hour_overtime
            )

    @api.constrains("session_time")
    def _check_session_time_validity(self):
        for record in self:
            if record.session_time < datetime.combine(
                date.today(), datetime.min.time()
            ):
                raise ValidationError("Session time cannot be in the Past")

    @api.constrains("session_start_time", "session_end_time")
    def _check_time_validity(self):
        for record in self:
            if record.session_start_time >= record.session_end_time:
                raise ValidationError("End time must be after start time!")

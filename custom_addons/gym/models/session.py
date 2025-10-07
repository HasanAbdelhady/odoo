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
    session_cost = fields.Float(string="Session Cost", compute="_compute_session_cost", store=True, readonly=True)
    in_time = fields.Boolean(string="In time?", compute="_compute_session_cost", store=True)
    out_time = fields.Boolean(string="Overtime?", compute="_compute_session_cost", store=True)
    is_attended_by_coach = fields.Boolean(string="Did the coach attend?")
    is_attended_by_trainee = fields.Boolean(string="Did the trainee attend?")
    coach_cost_per_hour_normal = fields.Float(related="coach_id.coach_cost_per_hour_normal", string="Coach Cost Per Hour (in time)")
    coach_cost_per_hour_overtime = fields.Float(related="coach_id.coach_cost_per_hour_overtime", string="Coach Cost Per Hour (Overtime)")

    @api.depends("coach_name", "trainee_name", "trainee_phone")
    def _set_session_title(self):
        for record in self:
            if record.coach_name and record.trainee_name and record.trainee_phone:
                record.session_title = f"""Trainee: {record.trainee_name} - Phone: {record.trainee_phone} -
                Coach: {record.coach_name}
                """
            else:
                self.session_title = ""

    @api.depends("session_start_time", "session_end_time", "coach_id", "coach_id.schedule_ids", "coach_cost_per_hour_normal", "coach_cost_per_hour_overtime")
    def _compute_session_cost(self):
        for record in self:
            if not record.session_start_time or not record.session_end_time or not record.coach_id:
                record.session_cost = 0.0
                record.in_time = False
                record.out_time = False
                continue

            # Get user's timezone (or default to UTC)
            user_tz = pytz.timezone(self.env.user.tz or 'UTC')
            
            # Convert session times from UTC to user's local timezone
            # Odoo stores datetime in UTC, but schedules are in local time
            session_start_local = pytz.utc.localize(record.session_start_time).astimezone(user_tz)
            session_end_local = pytz.utc.localize(record.session_end_time).astimezone(user_tz)
            
            # Get session day of week (Monday = 0, Sunday = 6)
            session_day = session_start_local.weekday()
            day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            session_day_name = day_names[session_day]

            # Convert session times to float hours (0-24) in LOCAL timezone
            # Example: 14:30 becomes 14.5 (14 hours + 30/60 minutes)
            session_start_hour = session_start_local.hour + session_start_local.minute / 60.0
            session_end_hour = session_end_local.hour + session_end_local.minute / 60.0

            # Calculate total session duration in hours
            session_duration = (record.session_end_time - record.session_start_time).total_seconds() / 3600.0

            # Find the coach's schedule for this specific day
            # We use filtered() to pick the schedule that matches the session day
            coach_schedule = record.coach_id.schedule_ids.filtered(
                lambda schedule: schedule.day_of_week == session_day_name
            )

            normal_hours = 0.0
            overtime_hours = 0.0

            # Take the first schedule if one exists for this day
            if coach_schedule:
                coach_schedule = coach_schedule[0]  # Get the first schedule
                # Check if session falls within coach's scheduled time
                schedule_start = coach_schedule.time_from
                schedule_end = coach_schedule.time_to

                # Calculate the overlap between session time and schedule time
                # Example: Session 8-10, Schedule 9-17 → overlap is 9-10 (1 hour)
                overlap_start = max(session_start_hour, schedule_start)
                overlap_end = min(session_end_hour, schedule_end)

                if overlap_start < overlap_end:
                    # There is overlap - this is normal time
                    normal_hours = overlap_end - overlap_start

                # Calculate overtime (parts of session outside the schedule)
                
                # Part 1: Session starts before the schedule
                # Example: Session 8-10, Schedule 9-17 → 8-9 is overtime (1 hour)
                if session_start_hour < schedule_start:
                    overtime_hours += min(session_end_hour, schedule_start) - session_start_hour

                # Part 2: Session ends after the schedule
                # Example: Session 16-18, Schedule 9-17 → 17-18 is overtime (1 hour)
                if session_end_hour > schedule_end:
                    overtime_hours += session_end_hour - max(session_start_hour, schedule_end)

                # Set flags to indicate if there's normal time or overtime
                record.in_time = normal_hours > 0
                record.out_time = overtime_hours > 0
            else:
                # No schedule found for this day - all time is overtime
                # Example: Coach doesn't work on Sundays, but session is on Sunday
                overtime_hours = session_duration
                record.in_time = False
                record.out_time = True

            # Calculate total cost: normal hours + overtime hours
            # Example: 2 hours normal ($200/hr) + 1 hour overtime ($250/hr) = $650
            normal_cost = normal_hours * record.coach_cost_per_hour_normal
            overtime_cost = overtime_hours * record.coach_cost_per_hour_overtime
            record.session_cost = normal_cost + overtime_cost

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

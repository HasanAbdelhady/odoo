from odoo import models, fields, api
from datetime import datetime, date
from odoo.exceptions import ValidationError
import pytz


class Session(models.Model):
    _name = "gym.session"
    _description = "Session"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "session_title"

    membership_id = fields.Many2one(
        comodel_name="gym.membership", string="Membership", default=None
    )

    # Coach Fields
    coach_id = fields.Many2one(related="membership_id.coach_id", string="Coach Name")
    coach_name = fields.Char(
        string="Coach name", related="membership_id.coach_id.name", readonly=True
    )
    coach_image = fields.Binary(
        string="Coach Photo", readonly=True, compute="_set_membership_data"
    )
    coach_phone = fields.Char(
        string="Coach Phone", readonly=True, compute="_set_membership_data"
    )

    # Trainee Fields
    trainee_id = fields.Many2one(comodel_name="gym.trainee", string="Trainee Name")
    trainee_name = fields.Char(
        string="Trainee Name", compute="_set_membership_data", readonly=True
    )
    trainee_image = fields.Binary(
        string="Trainee Photo", readonly=True, compute="_set_membership_data"
    )
    trainee_phone = fields.Char(
        string="Trainee Phone", readonly=True, compute="_set_membership_data"
    )

    session_start_time = fields.Datetime(
        string="Session Start Time", required=True, tracking=True
    )

    session_title = fields.Char(
        String="Title", compute="_set_session_title", readonly=True, store=True
    )

    session_price = fields.Float(
        related="membership_id.session_price",
        string="Session Cost",
        store=True,
        readonly=True,
    )
    is_attended_by_coach = fields.Boolean(string="Did the coach attend?")
    is_attended_by_trainee = fields.Boolean(string="Did the trainee attend?")
    session_duration = fields.Float(
        related="membership_id.product_id.session_duration",
        string="Session Duration",
        store=True,
    )
    is_overtime = fields.Boolean(string="In overtime?", compute="_is_overtime")

    coach_share = fields.Float(string="Coach's Share", compute="_compute_coach_share")
    coach_schedule = fields.One2many(
        related="membership_id.coach_id.schedule_ids", string="Coach's Schedule"
    )

    @api.depends("is_overtime")
    def _compute_coach_share(self):
        for record in self:
            if record.is_overtime:
                record.coach_share = record.session_price * 0.4
            else:
                record.coach_share = record.session_price * 0.3

    @api.onchange("session_start_time", "coach_id")
    def _debug_coach_schedule(self):
        """Debug method to check coach schedule access"""
        if not self.coach_id or not self.session_start_time:
            return

        # Convert UTC to local time for debugging
        user_tz_name = self.env.user.tz or "UTC"
        user_tz = pytz.timezone(user_tz_name)
        session_utc = pytz.utc.localize(self.session_start_time)
        session_local = session_utc.astimezone(user_tz)

        print(f"Coach: {self.coach_id.name}")
        print(f"User timezone: {user_tz_name}")
        print(f"Session time (UTC): {self.session_start_time}")
        print(f"Session time (Local): {session_local}")
        print(f"Local hour: {session_local.hour + session_local.minute / 60.0}")
        print(f"UTC offset: {session_local.strftime('%z')}")

        schedule = self.coach_id.schedule_ids
        if schedule:
            for day in schedule:
                print(f"  {day.day_of_week}: {day.time_from} - {day.time_to}")
        else:
            print("No schedule found")

    @api.depends("session_start_time", "coach_id", "coach_id.schedule_ids")
    def _is_overtime(self):
        for record in self:
            record.is_overtime = False

            if not record.coach_id or not record.session_start_time:
                continue

            # Convert UTC time to user's local timezone
            # Temporary fix: hardcode GMT+2 timezone
            user_tz = pytz.timezone("Africa/Cairo")  # GMT+2 timezone
            # user_tz = pytz.timezone(self.env.user.tz or "UTC")
            session_datetime_utc = pytz.utc.localize(record.session_start_time)
            session_datetime_local = session_datetime_utc.astimezone(user_tz)

            # Get session day and time in local timezone
            session_weekday = session_datetime_local.weekday()  # 0=Monday, 6=Sunday
            session_hour = (
                session_datetime_local.hour + session_datetime_local.minute / 60.0
            )

            # Convert Python weekday to our day names
            day_names = [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]
            session_day = day_names[session_weekday]

            # Find coach's schedule for this day
            coach_schedule = record.coach_id.schedule_ids.filtered(
                lambda s: s.day_of_week == session_day
            )

            if not coach_schedule:
                record.is_overtime = True  # No schedule for this day = overtime
            else:
                # Check if session time is within coach's working hours
                schedule = coach_schedule[0]  # Take first matching schedule
                if session_hour < schedule.time_from or session_hour > schedule.time_to:
                    record.is_overtime = True

    @api.depends("membership_id")
    def _set_membership_data(self):
        for record in self:
            if record.membership_id:
                record.coach_image = record.membership_id.coach_id.coach_image
                record.coach_phone = record.membership_id.coach_id.phone_number
                record.trainee_name = record.membership_id.trainee_id.name
                record.trainee_image = record.membership_id.trainee_id.trainee_image
                record.trainee_phone = record.membership_id.trainee_id.phone_number
            else:
                # Set default values when no membership
                record.coach_image = False
                record.coach_phone = ""
                record.trainee_name = ""
                record.trainee_image = False
                record.trainee_phone = ""

    @api.depends("membership_id")
    def _set_session_title(self):
        for record in self:
            if record.membership_id:
                record.session_title = record.membership_id.name
            else:
                record.session_title = ""

    # @api.depends(
    #     "session_start_time",
    #     "session_end_time",
    #     "coach_id",
    #     "coach_id.schedule_ids",
    # )
    # def _compute_session_cost(self):
    #     for record in self:
    #         # Default values
    #         record.session_cost = 0.0
    #         record.in_time = False
    #         record.out_time = False
    #
    #         if not (
    #             record.session_start_time
    #             and record.session_end_time
    #             and record.coach_id
    #         ):
    #             continue
    #
    #         # Convert UTC times to user's local timezone (coach schedule is in local time)
    #         user_tz = pytz.timezone(self.env.user.tz)
    #         session_start = pytz.utc.localize(record.session_start_time).astimezone(
    #             user_tz
    #         )
    #         session_end = pytz.utc.localize(record.session_end_time).astimezone(user_tz)
    #
    #         # Get session info in local time
    #         session_start_hour = session_start.hour + session_start.minute / 60.0
    #         session_end_hour = session_end.hour + session_end.minute / 60.0
    #         session_duration = session_end_hour - session_start_hour
    #         # Get day of week (in local time)
    #         # Python weekday(): Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
    #         # We want: Sat=0, Sun=1, Mon=2, Tue=3, Wed=4, Thu=5, Fri=6
    #         # So we shift: (weekday + 2) % 7
    #         day_names = [
    #             "saturday",
    #             "sunday",
    #             "monday",
    #             "tuesday",
    #             "wednesday",
    #             "thursday",
    #             "friday",
    #         ]
    #         session_day_index = (session_start.weekday() + 2) % 7
    #         session_day_name = day_names[session_day_index]
    #
    #         # Find coach's schedule for this day
    #         # schedule = record.coach_id.schedule_ids.filtered(
    #         #     lambda s: s.day_of_week == session_day_name
    #         # )
    #         schedule = [
    #             day
    #             for day in record.coach_id.schedule_ids
    #             if session_day_name == day.day_of_week
    #         ]
    #
    #         if schedule:
    #             schedule = schedule[0]
    #             # Calculate overlap
    #             overlap_start = max(session_start_hour, schedule.time_from)
    #             overlap_end = min(session_end_hour, schedule.time_to)
    #             normal_hours = max(0, overlap_end - overlap_start)
    #             overtime_hours = session_duration - normal_hours
    #
    #             record.in_time = normal_hours > 0
    #             record.out_time = overtime_hours > 0
    #         else:
    #             # No schedule = all overtime
    #             normal_hours = 0
    #             overtime_hours = session_duration
    #             record.out_time = True

    @api.constrains("session_start_time")
    def _check_session_time_validity(self):
        for record in self:
            if record.session_start_time < datetime.combine(
                date.today(), datetime.min.time()
            ):
                raise ValidationError("Session time cannot be in the Past")

    @api.constrains("session_start_time")
    def _check_time_validity(self):
        for record in self:
            if record.session_start_time < fields.Datetime.now():
                raise ValidationError("Session Cannot Start In The Past!")

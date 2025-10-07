from odoo import models, fields, api
from datetime import datetime, date
from odoo.exceptions import ValidationError


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
    session_cost = fields.Float(string="Session Cost")
    in_time = fields.Boolean(string="In time?")
    out_time = fields.Boolean(string="Overtime?")
    is_attended_by_coach = fields.Boolean(string="Did the coach attend?")
    is_attended_by_trainee = fields.Boolean(string="Did the trainee attend?")
    coach_cost_per_hour_normal = fields.Float(string="Coach Cost Per Hour (in time)")
    coach_cost_per_hour_overtime = fields.Float(string="Coach Cost Per Hour (Overtime)")

    @api.depends("coach_name", "trainee_name", "trainee_phone")
    def _set_session_title(self):
        for record in self:
            if record.coach_name and record.trainee_name and record.trainee_phone:
                record.session_title = f"""Trainee: {record.trainee_name} - Phone: {record.trainee_phone} -
                Coach: {record.coach_name}
                """
            else:
                self.session_title = ""

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

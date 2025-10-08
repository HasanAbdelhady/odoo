from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CoachSchedule(models.Model):
    _name = "gym.coach.schedule"
    _description = "Coach Schedule"
    _order = "day_of_week, time_from"

    coach_id = fields.Many2one(
        comodel_name="gym.coach", string="Coach", required=True, ondelete="cascade"
    )
    day_of_week = fields.Selection(
        [
            ("saturday", "Saturday"),
            ("sunday", "Sunday"),
            ("monday", "Monday"),
            ("tuesday", "Tuesday"),
            ("wednesday", "Wednesday"),
            ("thursday", "Thursday"),
            ("friday", "Friday"),
        ],
        string="Day of Week",
        required=True,
    )
    time_from = fields.Float(string="From", required=True, help="Start time")
    time_to = fields.Float(string="To", required=True, help="End time")

    time_display = fields.Char(
        string="Time", compute="_compute_time_display", store=True
    )

    @api.depends("time_from", "time_to")
    def _compute_time_display(self):
        for record in self:
            if record.time_from and record.time_to:
                from_hour = int(record.time_from)
                from_min = int((record.time_from % 1) * 60)
                to_hour = int(record.time_to)
                to_min = int((record.time_to % 1) * 60)
                record.time_display = f"{from_hour:02d}:{from_min:02d} - {to_hour:02d}:{to_min:02d} ({record.time_to - record.time_from} Hours)"
            else:
                record.time_display = ""

    # Validation: time_to must be after time_from
    @api.constrains("time_from", "time_to")
    def _check_time_validity(self):
        for record in self:
            if record.time_from >= record.time_to:
                raise ValidationError("End time must be after start time!")
            if record.time_from < 0 or record.time_from > 24:
                raise ValidationError("Start time must be between 0 and 24!")
            if record.time_to < 0 or record.time_to > 24:
                raise ValidationError("End time must be between 0 and 24!")


class Coach(models.Model):
    _name = "gym.coach"
    _description = "coach"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="coach Name", required=True)
    coach_image = fields.Binary("Photo", attachment=True)
    coach_id = fields.Integer(string="coach ID", required=True, tracking=True)
    phone_number = fields.Char(string="Phone Number", required=True, unique=True)

    schedule_ids = fields.One2many(
        comodel_name="gym.coach.schedule",
        inverse_name="coach_id",
        string="Weekly Schedule",
    )

    coach_cost_per_hour_normal = fields.Float(
        string="Coach Cost Per Hour (in time)", default=200
    )
    coach_cost_per_hour_overtime = fields.Float(
        string="Coach Cost Per Hour (Overtime)", default=250
    )

    trainee_ids = fields.Many2many(comodel_name="gym.trainee", string="Trainees")
    _sql_constraints = [
        ("unique_coach_id", "unique(coach_id)", "The coach ID must be unique!"),
        (
            "unique_phone_number",
            "unique(phone_number)",
            "The coach's phone number must be unique!",
        ),
    ]

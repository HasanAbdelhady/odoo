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
    coach_id = fields.Char(string="Coach ID", readonly=True, tracking=True)
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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("coach_id"):
                coach_id = self.env["ir.sequence"].next_by_code("gym.coach")
                print(f"🔥 DEBUG: Generated coach_id: {coach_id}")
                vals["coach_id"] = coach_id
        print(f"🔥 DEBUG: Final vals_list: {vals_list}")
        return super().create(vals_list)

    def write(self, vals):
        # Only generate coach_id if the record doesn't have one AND it's not being set in vals
        if not self.coach_id and "coach_id" not in vals:
            vals["coach_id"] = self.env["ir.sequence"].next_by_code("gym.coach")
        return super().write(vals)

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        if not default:
            default = {}
        if not default.get("phone_number"):
            default["phone_number"] = f"{self.phone_number} (copy)"
        # Clear coach_id so a new one gets generated
        default["coach_id"] = False
        return super().copy(default)

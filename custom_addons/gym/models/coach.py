from odoo import models, fields, api


class coach(models.Model):
    _name = "gym.coach"
    _description = "coach"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="coach Name", required=True)
    coach_image = fields.Binary("Photo", attachment=True)
    coach_id = fields.Integer(string="coach ID", required=True, tracking=True)
    phone_number = fields.Char(string="Phone Number", required=True, unique=True)

    # trainee_ids = fields.One2many(
    #     comodel_name="gym.trainee", inverse_name="coach_name", string="Trainees"
    # )
    #
    # trainee_count = fields.Integer(
    #     string="Number of Trainees", compute="_compute_trainee_count"
    # )

    _sql_constraints = [
        ("unique_coach_id", "unique(coach_id)", "The coach ID must be unique!"),
        (
            "unique_phone_number",
            "unique(phone_number)",
            "The coach's phone number must be unique!",
        ),
    ]

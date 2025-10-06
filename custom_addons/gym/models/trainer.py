from odoo import models, fields, api


class trainer(models.Model):
    _name = "gym.trainer"
    _description = "Trainer"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Trainer Name", required=True)
    trainer_image = fields.Binary("Photo", attachment=True)
    trainer_id = fields.Integer(string="Trainer ID", required=True, tracking=True)
    phone_number = fields.Char(string="Phone Number", required=True, unique=True)

    # trainee_ids = fields.One2many(
    #     comodel_name="gym.trainee", inverse_name="trainer_name", string="Trainees"
    # )
    #
    # trainee_count = fields.Integer(
    #     string="Number of Trainees", compute="_compute_trainee_count"
    # )

    _sql_constraints = [
        ("unique_trainer_id", "unique(trainer_id)", "The trainer ID must be unique!"),
        (
            "unique_phone_number",
            "unique(phone_number)",
            "The trainer's phone number must be unique!",
        ),
    ]

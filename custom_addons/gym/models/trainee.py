from odoo import models, fields


class trainee(models.Model):
    _name = "gym.trainee"
    _description = "Trainee"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Trainee Name", required=True)
    trainee_image = fields.Binary("Image")

    trainee_id = fields.Integer(string="Trainee ID", required=True, tracking=True)
    phone_number = fields.Char(string="Phone Number", required=True, unique=True)
    # trainer_name = fields.Many2one(
    #     comodel_name="gym.trainer",
    #     string="Trainer",
    # )

    _sql_constraints = [
        ("unique_trainee_id", "unique(trainee_id)", "The trainee ID must be unique!"),
        (
            "unique_phone_number",
            "unique(phone_number)",
            "The trainee's phone number must be unique!",
        ),
    ]

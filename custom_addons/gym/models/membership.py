from odoo import models, fields


class Membership(models.Model):
    _name = "gym.membership"
    _description = "Membersihps"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    coach_id = fields.Many2one(comodel_name="gym.coach", string="Coach Name")
    trainee_id = fields.Many2one(comodel_name="gym.trainee", string="Trainee Name")

    coach_image = fields.Binary(
        related="coach_id.coach_image", string="Coach Photo", readonly=True
    )
    coach_phone = fields.Char(
        related="coach_id.phone_number", string="Coach Phone", readonly=True
    )

    # Related fields for trainee
    trainee_image = fields.Binary(
        related="trainee_id.trainee_image", string="Trainee Photo", readonly=True
    )
    trainee_phone = fields.Char(
        related="trainee_id.phone_number", string="Trainee Phone", readonly=True
    )

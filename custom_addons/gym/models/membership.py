from odoo import models, fields, api


class Membership(models.Model):
    _name = "gym.membership"
    _description = "Memberships"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="Membership Name", readonly=True, compute="_set_membership_name"
    )
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

    product_id = fields.Many2one(
        "product.product",
        string="Membership Plan",
        domain=[("is_gym_membership", "=", True)],
        required=True,
    )
    purchase_date = fields.Date(default=fields.Date.today)

    expiry_date = fields.Date()

    sessions_purchased = fields.Integer(related="product_id.session_count")
    sessions_used = fields.Integer(compute="_compute_sessions_used")
    sessions_remaining = fields.Integer(compute="_compute_sessions_remaining")

    session_price = fields.Float(
        related="product_id.session_price", string="Session Price"
    )
    membership_price = fields.Float(
        related="product_id.total_memebership_price", string="Membership Price"
    )

    def _set_membership_name(self):
        for record in self:
            if record.product_id and record.trainee_id and record.coach_id:
                record.name = f"Trainee: {record.trainee_id.name} - Coach: {record.coach_id.name} ({record.product_id.name})"
            else:
                record.name = ""

    @api.depends("product_id")  # Add this method
    def _compute_sessions_used(self):
        for record in self:
            # For now, just set to 0 - you can implement session counting later
            record.sessions_used = 0

    @api.depends("sessions_purchased", "sessions_used")  # Add this method
    def _compute_sessions_remaining(self):
        for record in self:
            record.sessions_remaining = record.sessions_purchased - record.sessions_used

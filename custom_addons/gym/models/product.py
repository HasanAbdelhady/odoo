from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_gym_membership = fields.Boolean(string="Is Gym Membership", default=False)

    session_count = fields.Integer(string="Number of Sessions", default=10)
    session_duration = fields.Float(string="Session Duration", default=1.0)

    session_price = fields.Float(
        string="Session Price", compute="_compute_session_price", store=True
    )

    total_memebership_price = fields.Float(
        string="Total Price", compute="_compute_membership_price", store=True
    )

    @api.onchange("is_gym_membership")
    def _onchange_is_gym_membership(self):
        for record in self:
            if record.is_gym_membership:
                record.type = "service"
                record.invoice_policy = "order"

                return {
                    "warning": {
                        "title": "Product Type Changed",
                        "message": 'Product type has been automatically set to "Service" for gym memberships.',
                    }
                }

    @api.depends("session_duration", "list_price")
    def _compute_session_price(self):
        for record in self:
            record.session_price = record.session_duration * record.list_price

    @api.depends("session_count", "session_duration", "list_price")
    def _compute_membership_price(self):
        for record in self:
            record.total_memebership_price = (
                record.session_duration * record.session_count * record.list_price
            )

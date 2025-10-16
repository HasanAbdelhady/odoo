from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_gym_membership = fields.Boolean(string="Is Gym Membership", default=False)

    session_count = fields.Integer(string="Number of Sessions", default=10)
    session_duration = fields.Float(string="Session Duration", default=1.0)

    coach_id = fields.Many2one("gym.coach", string="Coach")

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

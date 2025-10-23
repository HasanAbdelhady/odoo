from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    confirmed_user_id = fields.Many2one("res.users", string="Confirmed User")

    def action_confirm(self):
        super().action_confirm()
        self.confirmed_user_id = self.env.user

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        invoice_vals["so_confirmed_user_id"] = self.confirmed_user_id.id
        return invoice_vals

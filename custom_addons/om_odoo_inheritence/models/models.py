# from odoo import models, fields, api
#
#
# class om_odoo_inheritence(models.Model):
#     _name = "om_odoo_inheritence.om_odoo_inheritence"
#     _description = "om_odoo_inheritence.om_odoo_inheritence"
#
#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends("value")
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

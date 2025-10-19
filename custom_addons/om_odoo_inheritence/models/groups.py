from odoo import models, fields, api


class ResGroups(models.Model):
    _inherit = "res.groups"

    def get_application_groups(self, domain):
        print(f"Domain {domain}")
        return super().get_application(domain)

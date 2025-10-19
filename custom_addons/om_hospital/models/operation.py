from odoo import fields, models, api


class HospitalOperation(models.Model):
    _name = "hospital.operation"
    _rec_name = "name"
    _description = "Hospital Operation"
    _log_access = False

    name = fields.Char(string="Operation Name", ompute="_set_op_name")
    doctor_id = fields.Many2one("res.users", string="Doctor")

    #
    # @api.depends("doctor_id")
    # def _set_op_name(self):
    #     for record in self:
    #         record.name = f"Operation with Doctor {record.doctor_id.name}"
    #     else:
    #         record.name = "Operation (Unassigned Doctor)"
    #
    @api.model
    def name_create(self, name):
        print(f"Entered name {name}")

        new_record = self.create({"name": name})
        return (new_record.id, new_record.display_name)

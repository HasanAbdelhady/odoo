from odoo import fields, models, api


class HospitalOperation(models.Model):
    _name = "hospital.operation"
    _rec_name = "name"
    _description = "Hospital Operation"
    _log_access = False
    _order = "sequence,id"

    name = fields.Char(string="Operation Name", ompute="_set_op_name")
    doctor_id = fields.Many2one("res.users", string="Doctor")
    reference_record = fields.Reference(
        selection=[
            ("hospital.patient", "Patient"),
            ("hopsital.appointment", "Appointment"),
        ],
        string="Record",
    )

    sequence = fields.Integer(string="Sequence", default=10)

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

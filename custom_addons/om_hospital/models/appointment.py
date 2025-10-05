from odoo import models, fields, api


class Appointment(models.Model):
    _name = "hospital.appointment"
    _description = "Appointment"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    patient_id = fields.Many2one(comodel_name="hospital.patient", string="Patient")
    appointment_time = fields.Datetime(
        default=fields.Datetime.now, string="Appointment Time"
    )
    booking_date = fields.Date(default=fields.Date.context_today, string="Booking Date")

    # readonly is True by deafult, it takes its value from gender_id.gender
    gender = fields.Selection(related="patient_id.gender", readonly=True)

    ref = fields.Char(string="Reference")

    @api.onchange("patient_id")
    def on_change(self):
        if self.patient_id:
            self.ref = self.patient_id.ref

from odoo import models, fields


class CancelAppointment(models.TransientModel):
    _name = "cancel.appointment.wizard"
    _description = "Cancel Appointment Wizard"

    appointment_id = fields.Many2many(
        comodel_name="hospital.appointment", string="Appointment"
    )

    reason = fields.Text(string="Reason for Cacellation")

    def action_cancel(self):
        return

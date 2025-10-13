from odoo import models, fields, api
import datetime


class CancelAppointment(models.TransientModel):
    _name = "cancel.appointment.wizard"
    _description = "Cancel Appointment Wizard"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res["cancellation_date"] = datetime.date.today()
        print(f"Fields {res}")
        return res

    appointment_id = fields.Many2many(
        comodel_name="hospital.appointment", string="Appointment"
    )

    reason = fields.Text(string="Reason for Cacellation", default="Dont know lol")
    cancellation_date = fields.Date(string="Cancellation Date")

    def action_cancel(self):
        return

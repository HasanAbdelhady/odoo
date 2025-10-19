from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class CancelAppointment(models.TransientModel):
    _name = "cancel.appointment.wizard"
    _description = "Cancel Appointment Wizard"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res["cancellation_date"] = datetime.date.today()
        res["appointment_id"] = self.env.context.get("active_id")
        return res

    appointment_id = fields.Many2one(
        comodel_name="hospital.appointment",
        string="Appointment",
        required=True,
        # domain=[
        #     ("status", "in", ["draft", "in_consultation"]),
        #     ("priority", "in", ["0", "1", "2", None]),
        # ],
    )

    reason = fields.Text(string="Reason for Cacellation")
    cancellation_date = fields.Date(string="Cancellation Date")

    def action_cancel(self):
        cancel_day = self.env["ir.config_parameter"].get_param(
            "om_hospital.cancel_days"
        )
        print("cancel day", cancel_day)
        allowed_date = self.appointment_id.booking_date - relativedelta(
            days=int(cancel_day)
        )

        if allowed_date < fields.Date.today():
            raise ValidationError("Sorry You can't cancel this appointment now!")
        self.appointment_id.message_post(
            body=f"Appointment cancelled. Reason: {self.reason or 'No reason provided'}"
        )
        if self.appointment_id.booking_date == fields.Date.today():
            raise ValidationError("You cannot cancel an appointment on the dame day!")
        self.appointment_id.status = "cancelled"
        return {"type": "ir.actions.client", "tag": "reload"}

    # def no_canlcellation_on_same_day(self):
    #     for record in self:
    #         if record.appointment_id.booking_date == date.today():
    #             raise ValidationError(
    #                 "You cannot cancel an appointment on the dame day!"
    #             )

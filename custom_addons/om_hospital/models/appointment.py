from odoo import models, fields, api


class Appointment(models.Model):
    _name = "hospital.appointment"
    _description = "Appointment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "patient_id"

    patient_id = fields.Many2one(
        comodel_name="hospital.patient", string="Patient", required=True, tracking=True
    )
    appointment_time = fields.Datetime(
        default=fields.Datetime.now,
        string="Appointment Time",
        required=True,
        tracking=True,
    )
    booking_date = fields.Date(
        default=fields.Date.context_today,
        string="Booking Date",
        required=True,
        tracking=True,
    )

    # readonly is True by deafult, it takes its value from gender_id.gender
    gender = fields.Selection(related="patient_id.gender", readonly=True)

    ref = fields.Char(string="Reference", readonly=True)
    prescription = fields.Html(
        string="prescription",
    )
    priority = fields.Selection(
        [("0", "Normal"), ("1", "Low"), ("2", "Medium"), ("3", "High")],
        string="Priority",
        tracking=True,
    )
    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_consultation", "In Consultation"),
            ("done", "Done"),
            ("canceled", "Canceled"),
        ],
        default="draft",
        required=True,
        tracking=True,
        string="Status",
    )

    @api.onchange("patient_id")
    def on_change(self):
        if self.patient_id:
            self.ref = self.patient_id.ref

    def consultation(self):
        self.status = "in_consultation"

    def done(self):
        self.status = "done"
        return {
            "effect": {
                "fadeout": "slow",
                "message": "Appointment Done!",
                "type": "rainbow_man",
            }
        }

    def cancel_appointment(self):
        self.status = "canceled"

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from urllib.parse import quote
from odoo.exceptions import UserError


class Appointment(models.Model):
    _name = "hospital.appointment"
    _description = "Appointment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "patient_id"

    patient_id = fields.Many2one(
        comodel_name="hospital.patient",
        string="Patient",
        required=True,
        tracking=1,
    )
    # patient_name = fields.Char(
    #     related="patient_id.name",
    #     string="Patient name",
    # )
    appointment_time = fields.Datetime(
        default=fields.Datetime.now,
        string="Appointment Time",
        required=True,
        tracking=2,
    )
    booking_date = fields.Date(
        default=fields.Date.context_today,
        string="Booking Date",
        required=True,
        tracking=3,
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
        tracking=4,
    )
    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_consultation", "In Consultation"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
        string="Status",
    )
    doctor_id = fields.Many2one("res.users", string="Doctor")
    pharmacy_line_ids = fields.One2many(
        comodel_name="appointment.pharmacy.lines",
        inverse_name="appointment_id",
        string="Phramacy Lines",
    )
    hide_sales_price = fields.Boolean(string="Hide sales price")

    operation_id = fields.Many2one("hospital.operation", string="Operation")

    def action_share_whatsapp(self):
        if not self.patient_id.phone:
            raise UserError("This patient has no phone number.")

        phone = self.patient_id.phone.replace("+", "").replace(" ", "")

        msg = (
            f"*Hello {self.patient_id.name}!* 👋\n\n"
            "This is a reminder from *Om Hospital 🏥*.\n"
            "We hope you're doing well!\n\n"
            "_Please contact us if you’d like to confirm or update your appointment._\n\n"
            "💚 Wishing you good health!"
        )

        encoded_msg = quote(msg)
        whatsapp_api_url = f"https://wa.me/{phone}?text={encoded_msg}"
        return {
            "type": "ir.actions.act_url",
            "target": "new",
            "url": whatsapp_api_url,
        }

    # override deletion behaviour
    def unlink(self):
        for record in self:
            if record.status != "draft":
                raise ValidationError("You cannot delete this appointments!")
        return super().unlink()

    @api.onchange("patient_id")
    def on_change(self):
        if self.patient_id:
            self.ref = self.patient_id.ref

    def consultation(self):
        for rec in self:
            if rec.status == "draft":
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
        action = self.env.ref("om_hospital.wizard_cancel_appointment_action").read()[0]
        return action

    def reset_to_draft(self):
        for record in self:
            record.status = "draft"


class AppointmentPharmacyLines(models.Model):
    _name = "appointment.pharmacy.lines"
    _description = "Appointment Pharmacy Lines"

    product_id = fields.Many2one("product.product", required=True)
    unit_price = fields.Float(string="Price", related="product_id.list_price")
    total_price = fields.Float(string="Total", compute="_compute_total_price")
    qty = fields.Integer(string="Quantity", default=1)
    appointment_id = fields.Many2one(
        comodel_name="hospital.appointment", string="Appointment"
    )

    @api.depends("unit_price", "qty")
    def _compute_total_price(self):
        for prod in self:
            prod.total_price = prod.unit_price * prod.qty

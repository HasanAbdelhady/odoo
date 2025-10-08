from odoo import models, fields, api


class Appointment(models.Model):
    _name = "hospital.appointment"
    _description = "Appointment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "patient_id"

    patient_id = fields.Many2one(
        comodel_name="hospital.patient", string="Patient", required=True, tracking=True
    )
    patient_name = fields.Char(
        related="patient_id.name",
        string="Patient name",
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

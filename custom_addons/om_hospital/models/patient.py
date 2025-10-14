from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class Patient(models.Model):
    _name = "hospital.patient"
    _description = "Patient"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", required=True, tracking=True)
    birthday = fields.Date(string="birthday", required=True)
    # age is currently a non-stored computed field
    age = fields.Char(string="Age", compute="_compute_age", tracking=True)
    gender = fields.Selection(
        string="Gender",
        selection=[("male", "Male"), ("female", "Female")],
        default="male",
        tracking=True,
        required=True,
    )
    ref = fields.Char(string="Reference", readonly=True)
    address = fields.Text(string="Address", tracking=True)
    phone = fields.Char(string="Phone", tracking=True)
    email = fields.Char(string="Email", tracking=True)
    state = fields.Selection(
        string="State",
        selection=[
            ("normal", "Normal"),
            ("serious", "Serious"),
            ("critical", "Critical"),
        ],
        default="normal",
        tracking=True,
        required=True,
    )
    active = fields.Boolean(string="Active", default=True)
    appointment_id = fields.Many2one(
        comodel_name="hospital.appointment", string="Appointments"
    )
    image = fields.Binary("Photo", attachment=True)
    display_name = fields.Char(string="Display Name", compute="_compute_display_name")
    appointment_count = fields.Integer(
        string="Number of Appointments", compute="_count_appointments", store=True
    )
    appointment_ids = fields.One2many(
        "hospital.appointment", "patient_id", string="Appointments"
    )

    _sql_constraints = [
        (
            "right_phone_num_len",
            "CHECK (LENGTH(phone) = 11)",
            "Phone number must have 11 digits",
        )
    ]

    @api.depends("appointment_ids")
    def _count_appointments(self):
        for record in self:
            record.appointment_count = self.env["hospital.appointment"].search_count(
                [("patient_id", "=", record.id)]
            )

    @api.depends("name", "ref")
    def _compute_display_name(self):
        for record in self:
            if record.ref:
                record.display_name = f"[{record.ref}] {record.name}"
            else:
                record.display_name = record.name

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["ref"] = self.env["ir.sequence"].next_by_code("hospital.patient")
        return super().create(vals_list)

    def write(self, vals):
        if not self.ref or self.ref[:2] != "HP":
            vals["ref"] = self.env["ir.sequence"].next_by_code("hospital.patient")
        return super().write(vals)

    @api.depends("birthday")
    def _compute_age(self):
        for record in self:
            if record.birthday:
                today = fields.Date.today()
                delta = relativedelta(today, record.birthday)

                years = delta.years
                months = delta.months
                days = delta.days

                # Build a readable string, e.g. "23 years, 4 months, 12 days"
                parts = []
                if years:
                    parts.append(f"{years} year{'s' if years != 1 else ''}")
                if months:
                    parts.append(f"{months} month{'s' if months != 1 else ''}")
                if days:
                    parts.append(f"{days} day{'s' if days != 1 else ''}")

                record.age = ", ".join(parts) if parts else "0 days"
            else:
                record.age = "0 days"

    @api.constrains("birthday")
    def _check_birthday(self):
        print("================================================")
        print(f"Type of Self is {type(self)}")
        print(f"Self is {self.env.context}")
        print("================================================")
        for record in self:
            if record.birthday and record.birthday > fields.Date.today():
                raise ValidationError("Birthday cannot be in the future.")

    def name_get(self):
        return [(record.id, record.display_name) for record in self]

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        # Allow searching by name OR ref
        if name:
            args = (args or []) + [
                "|",
                ("name", operator, name),
                ("ref", operator, name),
            ]
        return super().name_search(name, args, operator, limit)

    # @api.constrains("age_years", "age_months", "age_days")
    # def _check_age_not_zero(self):
    #     for record in self:
    #         if (
    #             record.age_years == 0
    #             and record.age_months == 0
    #             and record.age_days == 0
    #         ):
    #             raise ValidationError("Patient must have some age specified!")

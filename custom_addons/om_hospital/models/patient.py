from datetime import date
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
    ref = fields.Char(string="Reference")
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

    @api.depends("birthday")
    def _compute_age(self):
        for record in self:
            if record.birthday:
                today = date.today()
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
        for record in self:
            if record.birthday and record.birthday > date.today():
                raise ValidationError("Birthday cannot be in the future.")

    # @api.constrains("age_years", "age_months", "age_days")
    # def _check_age_not_zero(self):
    #     for record in self:
    #         if (
    #             record.age_years == 0
    #             and record.age_months == 0
    #             and record.age_days == 0
    #         ):
    #             raise ValidationError("Patient must have some age specified!")

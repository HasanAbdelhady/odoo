from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class Patient(models.Model):
    _name = "hospital.patient"
    _description = "Patient"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", required=True, tracking=True)
    birthday = fields.Date(string="birthday", required=True)
    # age is now an integer field for years with inverse function
    age = fields.Integer(
        string="Age (Years)",
        compute="_compute_age",
        inverse="_inverse_age",
        store=True,
        tracking=True,
    )
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

    # def _search_age(self, operator, value):
    #     date_of_birth = fields.Date.today() - relativedelta(years=value)
    #     return [("date_of_birth", "=", date_of_birth)]

    def action_test(self):
        print("Clicked haha")
        return

    @api.ondelete(at_uninstall=False)
    def _check_appointments(self):
        for rec in self:
            if rec.appointment_id:
                raise ValidationError(
                    "You cannot delete patients that have appointments"
                )

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
                record.age = delta.years
            else:
                record.age = 0

    def _inverse_age(self):
        """Inverse function to calculate birthday from age"""
        for record in self:
            if record.age and record.age > 0:
                today = fields.Date.today()
                # Calculate birthday by subtracting age years from today
                record.birthday = today - relativedelta(years=record.age)
            elif record.age == 0:
                # If age is 0, set birthday to today
                record.birthday = fields.Date.today()

    @api.constrains("birthday")
    def _check_birthday(self):
        print("================================================")
        print(f"Type of Self is {type(self)}")
        print(f"Self is {self.env.context}")
        print("================================================")
        for record in self:
            if record.birthday and record.birthday > fields.Date.today():
                raise ValidationError("Birthday cannot be in the future.")

    @api.constrains("age")
    def _check_age(self):
        for record in self:
            if record.age and (record.age < 0 or record.age > 150):
                raise ValidationError("Age must be between 0 and 150 years.")

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

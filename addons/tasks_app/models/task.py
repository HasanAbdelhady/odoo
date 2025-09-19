from odoo import models, fields

class Task(models.Model):
    _name = "tasks.task"
    _description = "Task"

    name = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")
    is_done = fields.Boolean(string="Done", default=False)

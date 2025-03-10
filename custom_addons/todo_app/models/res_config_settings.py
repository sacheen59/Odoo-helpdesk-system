from odoo import _, api, fields, models

class TodoConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    todo_auto_archive = fields.Boolean(string='Auto Archive', config_parameter = "todo_app.todo_auto_archive", default=False)
    todo_notify_before_deadline = fields.Integer('Notify Before Deadline',config_parameter = "todo_app.todo_notify_before_deadline", default=1)
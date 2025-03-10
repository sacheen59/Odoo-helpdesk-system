from odoo import models,api,fields
from odoo.exceptions import UserError


class TaskMarkCompleteWizard(models.TransientModel):
    _name = 'todo_app.task.mark.complete.wizard'
    _description = 'Task Mark Complete Wizard'

    user_id = fields.Many2one('res.users',string='User')
    task_id = fields.Many2one('todo_app.todo.task',string='Task')
    remarks = fields.Text("Remarks")

    def action_confirm(self):
        """ Mark task as complete """
        self.ensure_one()
        if not self.task_id:
            raise UserError('Please select a task')
        self.task_id.action_mark_complete(remarks = self.remarks)
        return True

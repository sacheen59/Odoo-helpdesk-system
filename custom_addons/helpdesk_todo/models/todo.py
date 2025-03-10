from odoo import api,models,fields

class Todo(models.Model):
    """
    A models for extending the todo models

    This models inherit the todo models and add a field ticket_id for storing the helpdesk ticket created from the todo.
    """

    _inherit = 'todo_app.todo'

    ticket_id = fields.Many2one(
        'helpdesk_app.tickets',
        string='Ticket',
        )
    
    def write(self, vals: dict) -> bool:

        """
        A method for overriding the default write method

        This method ensures that when a todo item's stage is updated to "Completed," 
        the corresponding helpdesk ticket's stage is also updated accordingly.

        :param vals:  A dictionary containing the fields to be updated and their new values.
        :type vals: dict
        :return: The result of the parent class's write method.
        :rtype: bool
        """
        
        res = super().write(vals)
        for rec in self:
            if rec.ticket_id and rec.stage_id == self.env.ref('todo_app.stage_4'):
                rec.ticket_id.stage_id = self.env.ref('helpdesk_app.stage_3')
        return res
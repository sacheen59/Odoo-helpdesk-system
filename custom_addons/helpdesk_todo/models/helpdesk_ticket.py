from odoo import models,api, fields

class HelpdeskTicket(models.Model):
    """
    A models for extending the helpdesk ticket models

    This models inherit the helpdesk ticket models and add a field todo_id for storing the todo  created from the helpdesk ticket.
    """

    _inherit = 'helpdesk_app.tickets'

    todo_id = fields.One2many('todo_app.todo','ticket_id', string="Todo")
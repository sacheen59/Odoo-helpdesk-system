from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError


class HelpdeskTicket(models.Model):
    """
    Inherited model for Helpdesk tickets, extending the functionality to link a CRM lead.

    This model extends the CRM helpdesk_app.tickets model by adding a relationship with the crm lead.
    It allows associating a tickets with a crm lead.
    """

    _inherit = 'helpdesk_app.tickets'

    crm_lead_id = fields.Many2one('crm.lead', string='CRM Lead')
from odoo import _, api, fields, models


class CrmLead(models.Model):

    """
    Inherited model for CRM leads, extending the functionality to link a helpdesk ticket.

    This model extends the CRM lead model by adding a relationship with the helpdesk ticket.
    It allows associating a lead with a helpdesk ticket and updating the ticket's stage based on certain conditions.
    """

    _inherit = "crm.lead"

    ticket_id = fields.Many2one(
        'helpdesk_app.tickets',
        string='Ticket',
        )

    def write(self, vals:dict)-> bool:
        
        """
        Updates the CRM lead and adjusts the associated ticket's stage when conditions are met.

        This method overrides the default write method to update the stage of the associated
        helpdesk ticket when the lead's stage is changed to 'Closed' or when the lead is deactivated.

        If the lead's stage matches the 'stage_lead4' or the lead is inactive, the ticket's 
        stage is automatically set to 'stage_3' in the helpdesk system.

        :param vals: A dictionary of fields to update for the CRM lead.
        :type vals: dict
        :return: The result of the parent class's write method, indicating whether the update was successful.
        :rtype: bool
        """

        res = super().write(vals)
        for rec in self:
            if rec.ticket_id and rec.stage_id == self.env.ref('crm.stage_lead4') or not rec.active:
                rec.ticket_id.stage_id = self.env.ref('helpdesk_app.stage_3')
        return res
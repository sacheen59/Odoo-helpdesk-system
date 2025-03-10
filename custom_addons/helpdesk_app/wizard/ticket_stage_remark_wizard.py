# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo .exceptions import UserError

class TicketStageRemarkWizard(models.TransientModel):
    """
    Wizard for adding remarks when changing a ticket's stage.

    This wizard allows users to provide remarks and attachments when changing 
    the stage of a helpdesk ticket. It stores the old and new stage information 
    along with the remarks and any uploaded files.
    """
    _name = 'ticket_stage.remark.wizard'
    _description = 'Give remark for changing stage'

    
    ticket_id = fields.Many2one('helpdesk_app.tickets', string="Ticket Remarks", required=True )
    remarks = fields.Text("Remarks" , required=True)
    remarks_file = fields.Binary("Attachments")
    old_stage = fields.Char("Old stage")
    new_stage = fields.Char("New Stage")



    def action_confirm(self)-> None:
        
        """
        Confirms the addition of a remark when changing the ticket's stage.

        This method creates a new remark for the ticket, including any provided remarks, 
        attachments, and stage information. It also updates the ticket's stage to the new 
        stage and logs the old and new stages.

        :raises UserError: If no ticket is selected.
        :return: None
        :rtype: None
        """

        if not self.ticket_id:
            raise UserError(("Please select a ticket"))
        old_stage = self._context.get('old_stage')
        new_stage = self._context.get('new_stage','Draft')
        print(old_stage)

        # Create a new remark for the ticket
        self.env['helpdesk_app.ticket.remarks'].create({
            'ticket_id': self.ticket_id.id,
            'remark': self.remarks,
            'remark_file': self.remarks_file,
            'old_stage': old_stage,
            'new_stage': new_stage
        })
        new_stage_id = self.env['helpdesk_app.ticket.stage'].search([('name','=',new_stage)],limit=1)
        self.ticket_id.write({'stage_id': new_stage_id.id})
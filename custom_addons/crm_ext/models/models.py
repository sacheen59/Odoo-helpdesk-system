# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class CRMLead(models.Model):
    _inherit = 'crm.lead'

    is_visible = fields.Boolean(compute='_compute_hide_restore_button')
    old_stage_id = fields.Many2one('crm.stage', string='Old Stage')
    stage_name = fields.Char(related='stage_id.name', string='Stage Name')

    @api.depends('stage_id')
    def _compute_hide_restore_button(self):
        """
        This function is used to hide restore button when lead is in lost stage
        """
        lost_id = self.env.ref('crm_ext.stage_lead5')
        for rec in self:
            if rec.stage_id == lost_id:
                rec.is_visible = False
            else:
                rec.is_visible = True

    # convert to opportunity method 
    def action_custom_convert_to_opportunity(self):
        """ 
        Convert a lead into an opportunity.
    
        This method overrides the existing functionality to convert a lead into an 
        opportunity using the default conversion process.
        """
        return super(CRMLead, self).convert_opportunity(None)
    

    @api.model
    def action_set_lost(self,**addtional_values):
        """
         Mark a lead as lost and update its stage accordingly.

        This method overrides the default `action_set_lost` behavior to:
            - Prevent marking a lead as lost if it is already in the lost stage.
            - Store the current stage before updating it to the lost stage.
            - Call the parent method to ensure standard functionality.
            - Update the `stage_id` to the lost stage and keep the record active.
        """

        lost_stage_id = self.env.ref('crm_ext.stage_lead5' ,raise_if_not_found=False)
        for rec in self:
            if rec.stage_id == lost_stage_id:
                raise UserError('One of the record is already in lost.')
            else:
                rec.old_stage_id = rec.stage_id.id
        res = super(CRMLead, self).action_set_lost(**addtional_values)
        self.write({
            'stage_id': lost_stage_id.id,
            'active': True,
        })
        return res
    
    def action_set_won_rainbowman(self):
        """
        Mark the lead as won and assign a related partner.

        This method performs the following steps:
            - Searches for an existing partner based on the lead's contact name and email.
            - If both name and email are available, it prioritizes finding an exact match.
            - If only an email is available, it searches for a partner by email.
            - If only a name is available, it searches for a partner by name.
            - Assigns the found partner to the lead using `_handle_partner_assignment`.
            - Calls the parent class's `action_set_won_rainbowman` to ensure standard behavior.
        """

        partner_id = None
        if self.contact_name and self.email_from:
            partner_id = self.env['res.partner'].search([('name', '=', self.contact_name),('email', '=', self.email_from)],limit=1)
        if self.email_from:
            partner_id = self.env['res.partner'].search([('email', '=', self.email_from)],limit=1)
        if self.contact_name:
            partner_id = self.env['res.partner'].search([('name', '=', self.contact_name)],limit=1)
        self._handle_partner_assignment(force_partner_id=partner_id.id, create_missing=True)
        return super(CRMLead, self).action_set_won_rainbowman()
    

    def action_restore(self):
        """
        Restore the lead to its previous stage.
        """
        self.write({
            'stage_id': self.old_stage_id.id,
        })


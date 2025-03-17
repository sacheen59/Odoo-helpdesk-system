# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CRMLead(models.Model):
    _inherit = 'crm.lead'

    is_visible = fields.Boolean(compute='_compute_hide_restore_button')
    old_stage_id = fields.Many2one('crm.stage', string='Old Stage')

    @api.depends('stage_id')
    def _compute_hide_restore_button(self):
        lost_id = self.env.ref('crm_ext.stage_lead5')
        for rec in self:
            if rec.stage_id == lost_id:
                rec.is_visible = False
            else:
                rec.is_visible = True

    def action_custom_convert_to_opportunity(self):
        return super(CRMLead, self).convert_opportunity(None)
    

    def action_set_lost(self,**addtional_values):
        res = super(CRMLead, self).action_set_lost(**addtional_values)
        lost_stage_id = self.env.ref('crm_ext.stage_lead5').id
        self.old_stage_id = self.stage_id
        self.write({
            'stage_id': lost_stage_id,
            'active': True,
        })
        return res
    
    def action_set_won_rainbowman(self):
        partner_id = self.env['res.partner'].search([('name', '=', self.contact_name),('email', '=', self.email_from)],limit=1)
        if not partner_id:
            partner_id = self.env['res.partner'].create({
                'name': self.contact_name,
                'email': self.email_from,
            })
        self.partner_id = partner_id.id
        self.convert_opportunity(partner_id)
        return super(CRMLead, self).action_set_won_rainbowman()
    

    def action_restore(self):
        self.write({
            'stage_id': self.old_stage_id.id,
        })


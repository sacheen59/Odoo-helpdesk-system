from odoo import _, api, fields, models

class HelpdeskCrmCreateCrmWizard(models.TransientModel):

    """
    A wizard for creating a CRM lead from a helpdesk ticket.

    This models inherit models.TransientModel and allows creating a CRM lead directly from a helpdesk ticket. 
    The wizard pre-fills the CRM lead details based on the selected ticket and enables 
    users to confirm and create the corresponding CRM lead, while updating the ticket's stage.
    """

    _name = 'helpdesk_crm.create.crm.wizard'
    _description = 'Helpdesk CRM Create CRM Wizard'

    crm_lead_id = fields.Many2one('crm.lead', string='CRM Lead', ondelete='cascade')
    ticket_id = fields.Many2one('helpdesk_app.tickets', string='Ticket', required=True, ondelete='cascade')
    ticket_name = fields.Char(string='Ticket Name')
    contact_name = fields.Char(string='Name', required=True)
    contact_email = fields.Char(string='Email', required=True)
    contact_phone = fields.Char(string='Phone')

    @api.model
    def default_get(self, fields: list) -> dict:

        """
        Retrieves the default values for the wizard fields.

        This method overrides the default_get method to pre-fill the wizard fields 
        with data from the currently active ticket. If the active ticket is found, 
        it will populate fields such as `ticket_id`, `ticket_name`, `contact_email`, 
        `contact_phone`, and `contact_name`.

        :param fields: List of fields for which default values are needed.
        :type fields: list
        :return: A dictionary of default values for the wizard.
        :rtype: dict
        """

        res = super(HelpdeskCrmCreateCrmWizard, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        active_model = self.env.context.get('active_model')

        if active_id and active_model:
            ticket = self.env[active_model].browse(active_id)
            res.update({
                'ticket_id': ticket.id,
                'ticket_name': ticket.title,
                'contact_email': ticket.email,
                'contact_phone': ticket.phone,
                'contact_name': ticket.reported_by.name,

            })
        return res

    def action_confirm(self) -> dict:

        """
        Confirms the creation of a CRM lead from the helpdesk ticket.

        This method is triggered when the user confirms the creation of a CRM lead 
        from the helpdesk ticket. It updates the ticket's stage, creates a new CRM lead 
        with the provided information, and opens the newly created CRM lead in a form view.

        :return: An action dictionary to open the newly created CRM lead.
        :rtype: dict
        """

        self.ticket_id.write({
            'stage_id': self.env.ref('helpdesk_app.stage_2').id,
        })
        crm_lead = self.env['crm.lead'].create({
            'name': self.ticket_name,
            'email_from': self.contact_email,
            'phone': self.contact_phone,
            'contact_name': self.contact_name,

        })

        self.crm_lead_id = crm_lead.id

        return {
            'name': 'CRM Lead',
            'view_mode': 'form',
            'res_model': 'crm.lead',
            'type': 'ir.actions.act_window',
            'res_id': crm_lead.id,
            'target': 'current',
        }
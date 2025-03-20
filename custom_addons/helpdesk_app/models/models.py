from odoo import models, fields, api
from odoo.exceptions import UserError
from random import randint


class HelpDeskTicketsCategory(models.Model):
    """
    A model for managing helpdesk ticket categories.

    :param models: Odoo model for helpdesk ticket categories
    :type models: models.Model
    """

    _name = 'helpdesk_app.tickets.category'
    _description = 'Helpdesk Tickets Category'
    _rec_name = 'name'

    
    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')

class HelpdeskTickets(models.Model):

    """
    A model for managing helpdesk tickets.

    :param models: Odoo model for helpdesk tickets
    :type models: models.Model

    """

    _name = 'helpdesk_app.tickets'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Helpdesk Tickets'
    _rec_name = 'name'
    
    name = fields.Char(string="Ticket Reference", required=True, copy = False, readonly=False,index = "trigram",default=lambda self: ('New'))
    title = fields.Char(string='Title', required=True, tracking=True)
    email = fields.Char(string="Email", required=True, tracking=True)
    phone = fields.Char(string="Phone", required=True, tracking=True)
    query = fields.Text(string='Query', required=True,tracking=True)
    description = fields.Text(string='Description',tracking=True)
    category_id = fields.Many2one('helpdesk_app.tickets.category',string="Category",ondelete='set null',tracking=True)
    priority = fields.Selection([('0', 'Low'), ('1', 'Medium'), ('2', 'High'),('3', 'Very High')], string='Priority', default='0',tracking=True)
    reported_by = fields.Many2one('res.partner', string='Reported By')
    reported_date = fields.Date(string='Reported Date',tracking=True)
    assigned_team = fields.Many2one('helpdesk_app.helpdesk.team',string="Assigned Team",ondelete='set null',tracking=True)
    assigned_team_ids = fields.Many2many('res.users', 'helpdesk_app_helpdesk_team_res_users_rel', 'ticket_id', 'user_id',string='Assigned To',tracking=True, compute='_compute_assigned_team_ids')
    assigned_team_id = fields.Many2one('res.users',string="Team Member",domain='[("id", "in", assigned_team_ids)]' )
    remarks_ids = fields.One2many('helpdesk_app.ticket.remarks', 'ticket_id', string='Remarks')
    type = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External'),
    ], string="Type", default='internal',tracking=True)
    stage_id = fields.Many2one('helpdesk_app.ticket.stage',string="Stage", group_expand='_read_group_stage_id',ondelete='set null',tracking=True,default = lambda self: self._default_stage())
    stage_name = fields.Char(related='stage_id.name',readonly=True)
    tag_ids = fields.Many2many(
        'helpdesk_app.tickets.tag', 'helpdesk_app_tickets_tag_rel' , column1='ticket_id',column2='tag_id',string='Tags',tracking=True)
    
    def _read_group_stage_id(self, stages, domain: list[(tuple)], order:str = None):
        """
            Retrieves all the stages from the database.

            This method is used to fetch the available stages by querying the 'stages' model, 
            without applying any filters from the provided domain. It returns all stages 
            regardless of the domain or ordering parameters.

            :param stages: The model or recordset containing the stages to be queried.
            :type stages: recordset
            :param domain: The domain (filter conditions) to apply when querying the stages.
            :type domain: list of tuples
            :param order: The ordering criteria for the returned stages, defaults to None.
            :type order: str, optional
            :return: The recordset containing all stages from the database.
            :rtype: recordset
        """
        return stages.search([])
    
    def _default_stage(self):

        """
        Retrieves the first stage from the 'helpdesk_app.ticket.stage' model.

        This method queries the 'helpdesk_app.ticket.stage' model to retrieve the first stage 
        based on the ascending order of their sequence. It returns the ID of the first stage.

        :return: The ID of the first stage based on the sequence order.
        :rtype: int
        """

        return self.env['helpdesk_app.ticket.stage'].search([],order="sequence asc", limit=1).id
    
    def action_restore(self):
        """
        Restores the ticket to the 'Draft' stage.
        """

        self.write({
            'stage_id': self.env.ref('helpdesk_app.stage_1').id,
        })

    # function to openn the remark wizard
    def action_open_ticket_stage_remark_wizard(self)-> dict:

        """
        Opens a wizard to add remarks when changing the ticket stage.

        This method checks if the ticket is transitioning from the 'Draft' stage to the 'Progress' stage. 
        If no team or team member is assigned to the ticket, it raises a `UserError`. 
        Otherwise, it opens a wizard for the user to add remarks about the stage change.

        :raises UserError: If no team or team member is assigned when changing the stage from 'Draft' to 'Progress'.
        :return: A dictionary containing the action to open the 'ticket_stage.remark.wizard'.
        :rtype: dict
        """


        new_stage = self._context.get('new_stage_id')
        old_stage = self.stage_id
        # validate if team or team member is not assigned in the ticket 
        if old_stage.name == 'Draft' and new_stage == 'Progress' and (not self.assigned_team or not self.assigned_team_id):
            raise UserError('Please assign a team or a team member to the ticket')
        else:
            return {
                'name': 'Ticket Stage Remark',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'ticket_stage.remark.wizard',
                'target': 'new',
                'context': {
                    'default_ticket_id': self.id,
                    'new_stage': new_stage,
                    'old_stage': old_stage.name,
                }
            }
        
    @api.depends('assigned_team')
    def _compute_assigned_team_ids(self):

        """
            Computes the list of team members associated with the ticket's assigned team.
        """

        for record in self:
            if record.assigned_team:
                record.assigned_team_ids = record.assigned_team.team_members
            else:
                record.assigned_team_ids = self.env['res.users'].search([])

    @api.onchange('reported_by')
    def change_email_and_phone(self):
        """
        Updates the email and phone fields based on the reported_by field.
        """
        for record in self:
            if record.reported_by:
                record.email = record.reported_by.email
                record.phone = record.reported_by.phone
    

    # notify team member start 
    # send notification to team leader and team member when ticket is created
    @api._model_create_multi
    def create(self, vals_list:list[dict])-> api.Self:

        """
        Creates multiple records and notifies the assigned team after creation.

        This method overrides the default create method to allow creating multiple records at once.
        After the records are created, it calls the `_notify_team()` method to notify the team 
        about the newly created ticket.

        :param vals_list: A list of dictionaries containing the values for the records to be created.
        :type vals_list: list of dict
        :return: The created ticket records.
        :rtype: recordset
        """
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('helpdesk_app.tickets') or ('New')

        ticket =  super().create(vals_list)
        
        if ticket.type == 'external':
            ticket._notify_manager()
        
        ticket._notify_team()

        
        return ticket

    # send notification assigned team is updated
    def write(self, vals:dict)-> bool:

        """
        Updates the record and notifies the team if the assigned team or team member changes.

        This method overrides the default write method to update the record with new values.
        It checks if the `assigned_team` or `assigned_team_id` fields are changed. If either 
        of these fields is updated, the method triggers a team notification.

        :param vals: A dictionary containing the fields to be updated and their new values.
        :type vals: dict
        :return: The result of the parent class's write method, indicating whether the update was successful.
        :rtype: bool
        """
        res = super().write(vals)
        assigned_team_changed = vals.get('assigned_team') != self.assigned_team.id
        assigned_team_member_changed = vals.get('assigned_team_id') != self.assigned_team_id.id
        if assigned_team_changed or assigned_team_member_changed:
            self._notify_team()
        return res

    def _notify_team(self)->None:

        """
        Sends a notification to the assigned team and team leader when a ticket is assigned.

        This method checks if the ticket has an assigned team leader and team member.
        If either is assigned, a message is posted to notify them about the new ticket.
        The message includes a subject and body, and is sent to the partner IDs of the team leader
        and team member.

        :return: None
        :rtype: None
        """
        
        for rec in self:
            team_leader = rec.assigned_team.team_leader
            team_member = rec.assigned_team_id

            receipents = []

            if team_leader:
                receipents.append(team_leader.partner_id.id)
            
            if team_member:
                receipents.append(team_member.partner_id.id)
            
            if receipents:
                rec.message_post(
                    subject='New Ticket Assigned',
                    body='You have been assigned a new ticket. Please complete the ticket as soon as possible.',
                    partner_ids=receipents
                )


    def _notify_manager(self):
        """
        Notify the managers of the helpdesk when ever ticket is created.
        """
        managers = self.env['res.users'].search([('groups_id', 'in', self.env.ref('helpdesk_app.group_helpdesk_manager').id)])
        if not managers:
            return
        message_body = "New Query from external user. Please try to resolve it as soon as possible."
        self.message_post(
            body = message_body,
            subject='New External Ticket Created',
            message_type = 'notification',
            partner_ids=managers.mapped('partner_id').ids
        )

    # notify team member end 

class TicketsTag(models.Model):

    """
    Model for managing tags associated with helpdesk tickets.
    """

    _name = 'helpdesk_app.tickets.tag'
    _description = 'Helpdesk Tickets Tag'
    _rec_name = 'name'

    def _get_default_color(self)-> int:

        """
        Generates a random color for the tag.

        :return: A random integer between 1 and 11.
        :rtype: int
        """
        return randint(1, 11)

    name = fields.Char('Tag Name', required=True, translate=True)
    color = fields.Integer('Color', default=_get_default_color)

    _sql_constraints = [
        (
            'name_uniq',
            'unique(name)',
            'Tag name already exists'
        ),
    ]

class TicketRemarks(models.Model):

    """
    Model for managing remarks associated with helpdesk tickets.

    This model stores the remarks made by users regarding the status or progress 
    of a helpdesk ticket. It also allows attaching files to the remarks and tracks 
    the old and new stages of the ticket when a remark is added.

    :param models: Base model class for all Odoo models.
    :type models: models.Model
    """
    
    _name = 'helpdesk_app.ticket.remarks'
    _description = 'Helpdesk Ticket Remarks'
    _rec_name = 'remark'

    ticket_id = fields.Many2one('helpdesk_app.tickets', string='Ticket', ondelete='cascade')
    remark = fields.Text(string='Remark')
    remark_file = fields.Binary(string='Attachment')
    old_stage = fields.Char(string='Old Stage')
    new_stage = fields.Char(string='New Stage')
    remark_file_filename = fields.Char(string="Attachment Name")



class HelpdeskTeam(models.Model):

    """
    Model for managing helpdesk teams.

    This model represents a helpdesk team, which includes the team name, the team leader, 
    and the list of team members. The team leader is automatically added as a team member 
    and will be removed from the team if not listed among the team members.
    """

    _name = 'helpdesk_app.helpdesk.team'
    _description = 'Helpdesk Team'
    _rec_name = 'name'

    name = fields.Char(string='Team Name', required=True)
    team_leader = fields.Many2one('res.users', string='Team Leader',ondelete = "cascade")
    team_members = fields.Many2many('res.users', 'helpdesk_app_team_members_rel', column1='team_id', column2='user_id', string='Team Members')

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        if res.team_leader:
            res.assign_helpdesk_leader_role(res.team_leader)
        return res
    
    def write(self,vals):
        previous_team_leader = {record.id: record.team_leader for record in self}
        res = super().write(vals)
        for record in self:
            new_team_leader = record.team_leader
            previous_team_leader = previous_team_leader.get(record.id)
            if new_team_leader:
                record.assign_helpdesk_leader_role(new_team_leader)
            
            if previous_team_leader and previous_team_leader != new_team_leader:
                record.remove_helpdesk_leader_role(previous_team_leader)
        return res
    
    def assign_helpdesk_leader_role(self,user):
        """
        Assign the 'Hepdesk Leader' role to a specified user.

        This method checks if the user exists and then assigns them to the 'Helpdesk Leader' group.
        """

        if user:
            helpdesk_leader_group = self.env.ref('helpdesk_app.group_helpdesk_team_leader',raise_if_not_found=False)
            if helpdesk_leader_group:
                user.write({'groups_id': [(4, helpdesk_leader_group.id)]})

    def remove_helpdesk_leader_role(self,user):
        """
        Remove the 'Helpdesk Leader' role from a specified user.

        This method checks if the user exists and then removes them from the 'Helpdesk Leader' and Todo leader group.
        """

        if user:
            helpdesk_leader_group = self.env.ref('helpdesk_app.group_helpdesk_team_leader',raise_if_not_found=False)
            todo_leader_role = self.env.ref('todo_app.group_hepdesk_todo_leader',raise_if_not_found=False)
            if helpdesk_leader_group:
                user.write({'groups_id': [(3, helpdesk_leader_group.id)]})
                user.write({'groups_id': [(3, todo_leader_role.id)]})

    @api.onchange('team_leader')
    def _onchange_team_leader(self):

        """
        Automatically adds the team leader to the team members list when a team leader is set.

        This method ensures that when a team leader is selected, they are automatically 
        added to the team members list, if not already present.
        """

        if self.team_leader:
            self.team_members = [(4, self.team_leader.id)]

    @api.onchange('team_members')
    def _onchange_team_members(self):

        """
        Removes the team leader from the team if they are removed from the team members list.

        This method ensures that if the team leader is removed from the team members list, 
        they are also removed as the team leader.
        """
        
        if self.team_leader and self.team_leader.id not in self.team_members.ids:
            self.team_leader = False



class HelpdeskTicketStage(models.Model):
    
    """
    Model for managing stages of helpdesk tickets.
    """

    _name = 'helpdesk_app.ticket.stage'
    _description = 'Helpdesk Ticket Stage'
    _rec_name = "name"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer("Sequence",default=lambda self: self.search_count([]) + 1)
    is_prepopulated = fields.Boolean("Prepopulated",default=False)


    def unlink(self)->bool:
        """
        Deletes records, with a check to prevent the deletion of prepopulated stages.

        This method overrides the default unlink method to prevent the deletion of stages 
        that are marked as prepopulated. If any of the records to be deleted are prepopulated, 
        a UserError is raised.

        :raises UserError: If any of the records to be deleted are prepopulated, preventing deletion.
        :return: The result of the parent class's unlink method, which removes the records.
        :rtype: bool
        """
        if self.search_count([('id','in',self.ids),('is_prepopulated','=',True)]):
            raise UserError('You cannot delete prepopulated stages.')
        return super().unlink()


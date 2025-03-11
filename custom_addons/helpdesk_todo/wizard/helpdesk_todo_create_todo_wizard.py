from odoo import _, api, fields, models

class HelpdeskTodoCreateTodoWizard(models.TransientModel):
    """
    A wizard for creating a Todo for helpdesk ticket

    This model allows the Helpdesk manager to convert an internal 
    helpdesk ticket into a to-do task.
    """

    _name = 'helpdesk_todo.create.todo.wizard'
    _description = 'Helpdesk Todo Create Todo Wizard'

    user_id = fields.Many2one('res.users', string='User')
    ticket_id = fields.Many2one(
        'helpdesk_app.tickets',
        string='Helpdesk Ticket',
        required=True
        )
    todo_id = fields.Many2one('todo_app.todo',string='Todo')
    ticket_name = fields.Char("Title")
    ticket_query = fields.Text('Query')
    ticket_description = fields.Text('Description')
    tags_ids = fields.Many2many('helpdesk_app.tickets.tag', string='Tags')
    leader_id = fields.Many2one('res.users', string="Leader" ,tracking=True)



    @api.model_create_multi
    def create(self, vals_list: list[dict]):

        """
        Create a new record and assign the 'To-Do Manager' role to the leader if specified.

        This method overrides the default `create` method to ensure that whenever a new 
        record is created and a leader is assigned (`leader_id`), the leader is granted 
        the 'To-Do Manager' role.

        """
        record =  super().create(vals_list)
        if record.leader_id:
            record.assign_todo_manager_role(record.leader_id)
        return record
    
    def write(self,vals):

        """
        Update an existing record and assign the 'To-Do Manager' role if the leader is changed.

        This method overrides the default `write` method to check if the `leader_id` field is updated.
        If a new leader is assigned, the method ensures that they receive the 'To-Do Manager' role.
        """

        res = super().write(vals)

        leader_id = vals.get('leader_id')
        if leader_id:
            for record in self:
                record.assign_todo_manager_role(record.leader_id)
        return res


    def assign_todo_manager_role(self,user):
        """
        Assign the 'To-Do Manager' role to a specified user.

        This method checks if the user exists and then assigns them to the 'To-Do Manager' group.
        """

        if user:
            todo_manager_group = self.env.ref('todo_app.group_todo_manager',raise_if_not_found=False)
            if todo_manager_group:
                user.write({'groups_id': [(4, todo_manager_group.id)]})


    @api.model
    def default_get(self, fields: list) -> dict:
        """
        Overrides the default_get method to pre-fill form fields based on the active helpdesk ticket.
        
        This methods retrieves the active helpdesk ticket details from the context and set them as a default value for the wizard.

        :param fields: A list of field name that needs the default values.
        :type fields: list
        :return: A dictionary of default values for the fields.
        :rtype: dict
        """

        res = super(HelpdeskTodoCreateTodoWizard, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        active_model = self.env.context.get('active_model')

        if active_id and active_model:
            ticket = self.env[active_model].browse(active_id)
            res.update({
                'ticket_id': ticket.id,
                'ticket_name': ticket.title,
                'ticket_query': ticket.query,
                'ticket_description': ticket.description,
                'user_id': ticket.assigned_team_id.id,
                'leader_id': ticket.assigned_team.team_leader.id,

            })
        return res

    def action_confirm(self) -> dict:
        
        """
        Creates a new Todo from the helpdesk ticket.

        This method creates a new Todo record with the details of the helpdesk ticket and redirects the user to the Todo form.

        :return: A dictionary containing the action to open the Todo form.
        :rtype: dict
        """

        self.ticket_id.write({
            'stage_id': self.env.ref('helpdesk_app.stage_2').id,
        })
        todo = self.env['todo_app.todo'].create({
            'name': self.ticket_name,
            'description': self.ticket_query,
            'full_description': self.ticket_description,
            'stage_id': self.env.ref('todo_app.stage_1').id,
            'user_id': self.user_id.id

        })

        self.todo_id = todo.id

        return {
            'name': 'Todo',
            'view_mode': 'form',
            'res_model': 'todo_app.todo',
            'type': 'ir.actions.act_window',
            'res_id': todo.id,
            'target': 'current',
        }
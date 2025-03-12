from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError
import random

# todo cateogry model
class TodoCategory(models.Model):

    """
    Models for Todo Category
    """

    _name = 'todo_app.todo.category'
    _description = 'Todo Category'
    _rec_name = "title"

    title = fields.Char(string="Title", required=True)
    description = fields.Text("Description")

class Todo(models.Model):
    """
    Models for actual Todo

    This is the Todo model which have different table field and their methods
    """

    _name = 'todo_app.todo'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Todo Management'
    _order= "sequence asc, id desc"

    sequence = fields.Integer("Sequence",default=1, help="Gives the sequence order when displaying a list of todos.")
    name = fields.Char(string="Name", required=True,tracking=True)
    description = fields.Text("Brief Description",tracking=True)
    full_description = fields.Html("Full Description")
    date_deadline = fields.Date("Deadline",tracking=True)
    active = fields.Boolean("Active",default=True,tracking=True)
    category_id = fields.Many2one("todo_app.todo.category",string="Category",tracking=True,ondelete="set null")
    is_complete = fields.Boolean("Completed",default=False,tracking=True,compute="_compute_is_complete")
    progress = fields.Float("Progress",compute="_compute_is_complete",default = 0.0)
    stage_id = fields.Many2one('todo_app.todo.stage', string='Stages', group_expand='_read_group_stage_id',default = lambda self: self._default_stage(), tracking=True)
    stage_name = fields.Char(related='stage_id.name', string='Stage Name', readonly=True)
    user_id = fields.Many2one("res.users",string="Assigned To",tracking=True)
    leader_id = fields.Many2one("res.users",string="Leader")
    task_ids = fields.One2many("todo_app.todo.task","todo_id",string="Tasks",tracking=True)
    tag_ids = fields.Many2many("todo_app.todo.tag",string="Tags",tracking=True)

    def _default_stage(self):
        return self.env['todo_app.todo.stage'].search([],order="sequence asc", limit=1).id

    def _read_group_stage_id(self, stages, domain, order = None):
        return stages.search([])

    def action_assigned(self):
        self.write({
            'stage_id': self.env.ref('todo_app.stage_2').id,
        })

    def action_in_progress(self):
        self.write({
            'stage_id': self.env.ref('todo_app.stage_3').id,
        })

    def action_completed(self):
        self.write({
            'stage_id': self.env.ref('todo_app.stage_4').id,
        })

    def action_cancelled(self):
        self.write({
            'stage_id': self.env.ref('todo_app.stage_5').id,
        })
    
    def action_restore(self):
        self.write({
            'stage_id': self.env.ref('todo_app.stage_1').id,
        })


    @api.depends('task_ids','task_ids.is_compeleted')
    def _compute_is_complete(self):
        for record in self:
            if record.task_ids:
                record.is_complete = all(record.task_ids.mapped('is_compeleted'))
                record.progress = len(record.task_ids.filtered('is_compeleted')) / len(record.task_ids) * 100
            else:
                record.is_complete = False
                record.progress = 0.0

    @api.onchange('progress')
    def onchange_progress(self):
        complete_stage_id = self.env.ref('todo_app.stage_4').id
        if self.progress == 100:
            self.write({
                'stage_id': complete_stage_id,
            })

    @api.onchange('date_deadline')
    def onchange_date_deadline(self):
        today = fields.Date.today()
        if self.date_deadline and self.date_deadline < today:
            raise UserError('Date Deadline must not be in past')
        

    @api.model
    def notify_before_dead_dateline(self):
        print("Notifying user about date deadline ======>")
        date_today = fields.Date.today()
        notify_days_before = int(self.env['ir.config_parameter'].sudo().get_param('todo_app.todo_notify_before_deadline'))
        date_after_days = date_today + timedelta(days=notify_days_before)
        todos = self.search([('date_deadline', '<=', date_after_days), ('date_deadline', '>=', date_today)])
        for rec in todos:
            rec.message_post(
                body=f'Todo {rec.name} is about to expire.',
                partner_ids=rec.user_id.partner_id.ids
            )

        
    
    @api.model
    def auto_archive(self):
        is_archived = self.env['ir.config_parameter'].sudo().get_param('todo_app.todo_auto_archive') == "True" #True
        print("is Archived ====> ",is_archived)
        is_complete_stage = self.env.ref('todo_app.stage_4').id
        todos = self.search([('active','=',True)])
        if is_archived:
            for rec in todos:
                if rec.stage_id.id == is_complete_stage:
                    rec.write({
                    'active': False,
                    })

    # @api.model
    # def _notify_date_deadline(self):
    #     print("Notifying user about date deadline ======>")
    #     todos = self.search([])
    #     for rec in todos:
            rec.message_post(body=f"Reminder: Deadline for {rec.name} is approaching.",partner_ids = rec.user_id.partner_id.ids)


class TodoTask(models.Model):
    _name = 'todo_app.todo.task'
    _description = 'Todo Task'
    _rec_name = "name"
    _order = "id desc"

    name = fields.Char(string="Name", required=True)
    description = fields.Text("Description")
    todo_id = fields.Many2one("todo_app.todo",string="Todo",tracking=True,ondelete="cascade")
    is_compeleted = fields.Boolean("Completed",default=False,tracking=True)
    user_id = fields.Many2one("res.users",string="Assigned To",tracking=True)
    remarks = fields.Text("Remarks")

    def action_mark_complete(self,remarks):
        self.is_compeleted = True
        self.remarks = remarks


class TodoTag(models.Model):
    _name = 'todo_app.todo.tag'
    _description = 'Todo Tag'
    _rec_name = "name"


    def _get_default_color(self):
        return random.randint(1,11)

    name = fields.Char(string="Name", required=True)
    color = fields.Integer("Color Index",default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]


# classes for todo stage
class TodoStage(models.Model):
    _name = 'todo_app.todo.stage'
    _description = 'Todo Stage'
    _rec_name = "name"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer("Sequence",default=lambda self: self.search_count([]) + 1)
    is_prepopulated = fields.Boolean("Prepopulated",default=False)


    def unlink(self):
        if self.search_count([('id','in',self.ids),('is_prepopulated','=',True)]):
            raise UserError('You cannot delete prepopulated stages.')
        return super().unlink()

from odoo import api,fields,models
from odoo.exceptions import UserError
from functools import wraps

SALE_ORDER_STATE = [
    ('draft', "Quotation"),
    ('send_to_approve', 'Send to Approve'),
    ('approved', 'Approved'),
    ('sent', "Quotation Sent"),
    ('sale', "Sales Order"),
    ('cancel', "Cancelled"),
]

def check_orderline_presence(func):
        @wraps(func)
        def wrapper(self,*args,**kwargs):
            if not self.order_line:
                raise UserError("Your Orderlines are empty. Please add some products for proceed.")
            return func(self,*args,**kwargs)
        return wrapper


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    states = fields.Selection(
        selection=SALE_ORDER_STATE,
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft'
    )
    remarks_ids = fields.One2many('sale.order.approve.remark.wizard', 'sale_order_id', string='Remarks')
    is_visible = fields.Boolean("Is visible", compute="_compute_is_visible")

    


    @api.depends('order_line.price_unit', 'order_line.product_id.list_price', 'states')
    def _compute_is_visible(self):
        for rec in self:
            if not rec.order_line:
                rec.is_visible = False
            else:
                rec.is_visible = any(
                    line.price_unit < line.product_id.list_price and rec.states == 'draft'
                    for line in rec.order_line
                )



    def action_send_to_approve(self):
        sales_admin = self.env.ref('sales_team.group_sale_manager').users
        receipents = [admin.partner_id.id for admin in sales_admin]
        self.message_post(
            subject='New Quotation For Approval',
            body='A new ticket is pending for approval. Please Approve or Reject it.',
            partner_ids=receipents
        )
        self.write({'states': 'send_to_approve'})
        return True
    

    def _confirmation_error_message(self):
        super(SaleOrder, self)._confirmation_error_message()
        if self.states not in {'draft','sent','approved'}:
            return "Not allow to confirm"
        
        return False
    
    
    @check_orderline_presence
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.write({'states': 'sale'})
        return res
            

    def action_open_ticket_stage_remark_wizard(self):
        status = self._context.get('status')
        return {
            'name': 'Sale Order Approve Remark',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.order.approve.remark.wizard',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
                'status': status
            }
        }
    
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        res = super(SaleOrder, self).message_post(**kwargs)
        if self.env.context.get('mark_so_as_sent'):
            self.filtered(lambda o: o.states == 'draft' or o.states == 'approved').with_context(tracking_disable=True).write({'states': 'sent'})
        return res
    
    
    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        self.write({'states': 'cancel'})
        return res
    

    def action_draft(self):
        self.write({'states': 'draft'})
        return super(SaleOrder, self).action_draft()
    
    def action_quotation_sent(self):
        res = super(SaleOrder, self).action_quotation_sent()
        self.write({'states': 'sent'})
        return res
    
    @check_orderline_presence
    def action_quotation_send(self):
        return super(SaleOrder, self).action_quotation_send()
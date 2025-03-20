from odoo import api, fields, models

class TicketStageRemarkWizard(models.TransientModel):
    
    _name = 'sale.order.approve.remark.wizard'
    _description = 'Give remark for approve and reject of sale order'

    
    sale_order_id = fields.Many2one('sale.order', string="Sale Order Approve Remarks", required=True )
    remarks = fields.Text("Remarks" , required=True)
    remarks_file = fields.Binary("Attachments")
    status = fields.Char("Status")


    def _notification_of_approval(self,message):
        self.sale_order_id.message_post(
            subject = "Approval of Sale Order",
            body=message,
            partner_ids = [self.sale_order_id.user_id.partner_id.id]
        )


    def action_confirm(self):
        status = self._context.get('status')
        self.write({
            'status': status,
        })

        if status == 'Approved':
            self.sale_order_id.write({
                'states': 'approved'
            })
            self._notification_of_approval(message="Your order has been Approved. Go for further process")

        elif status == 'Rejected':
            self.sale_order_id.write({
                'states': 'draft'
            })
            self._notification_of_approval(message="Your order has been Rejected. Please contact to admin or recheck your order line.")


    

from odoo import models, api

class HelpdeskTicketReport(models.AbstractModel):
    _name = 'report.helpdesk_app.helpdesk_ticket_report_template'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        tickets = self.env['helpdesk_app.tickets'].browse(data.get('tickets'))
        stage_counts = {}
        for ticket in tickets:
            stage_name = ticket.stage_name  
            if stage_name not in stage_counts:
                stage_counts[stage_name] = 0
            stage_counts[stage_name] += 1


        stage_data = [{'stage_name': stage, 'ticket_count': count} for stage, count in stage_counts.items()]

        return {
            'doc_ids': docids,
            'doc_model': 'helpdesk_app.tickets',
            'docs': tickets,
            'start_date': data.get('start_date'),
            'end_date': data.get('end_date'),
            'total_ticket_count': len(tickets),
            'stage_counts': stage_data,
        }
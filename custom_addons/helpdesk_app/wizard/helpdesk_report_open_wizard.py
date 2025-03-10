from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class HelpdeskReportOpenWizard(models.TransientModel):

    """
    A wizard for generating helpdesk reports based on a date range.

    This model allows users to input a start and end date to generate a report 
    of tickets within the selected date range.
    """

    _name = 'helpdesk_app.report.open.wizard'
    _description = 'Helpdesk Report Open Wizard'

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)

    @api.constrains('start_date','end_date')
    def _check_dates(self):

        """
        Constraint to ensure that:
        - The start date is before or equal to the end date.
        - The end date is not in the future.

        :raises ValidationError: If the date conditions are not met.
        """

        if self.start_date > self.end_date or self.end_date > fields.Date.today():
            raise ValidationError('End date must be greater than start date and must be less than today date')
        

    def action_generate_report(self):

        """
        Generates a helpdesk report for tickets within the specified date range.

        - Fetches all tickets where the reported date falls within the given start and end dates.
        - Passes the data to the report action for rendering.

        :return: A report action for the helpdesk ticket report.
        :rtype: dict
        """

        start_date = self.start_date
        end_date = self.end_date
        tickets = self.env['helpdesk_app.tickets'].search([
            ('reported_date', '>=', start_date),
            ('reported_date', '<=', end_date)]
            )
        tickets = tickets.ids
        data = {
            'start_date': start_date,
            'end_date': end_date,
            'tickets': tickets
        }
        return self.env.ref('helpdesk_app.helpdesk_ticket_report_action').report_action(self, data=data)
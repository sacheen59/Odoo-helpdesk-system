# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class PortalHelpdesk(http.Controller):
    """
    Controller for handling customer support requests through the website.

    This class provides routes for displaying the support request form and submitting 
    helpdesk tickets from the website. It ensures that user queries are properly recorded 
    and associated with the correct customer
    """


    @http.route('/support', type='http', auth='public', website=True)
    def portal_support_form(self, **post: dict) -> http.Response:
        """
        Renders the support form page for users.

        This method serves the support form where users can enter their details 
        and submit a query.
        :param post: Dictionary of posted form data
        :type post: dict
        """

        return request.render('helpdesk_app.portal_support_form_template', {})

    @http.route('/submit_ticket', type='http', auth='public',methods=['POST'], website=True)
    def portal_support_form_submit(self, **post: dict)-> http.Response:

        """
        Handles the submission of the support form and creates a helpdesk ticket.

        This method captures user details from the submitted form, finds or creates 
        a customer record (partner), and generates a helpdesk ticket.

        :param post: Dictionary containing submitted form data including:
                     - username (str): The user's name.
                     - email (str): The user's email address.
                     - phone (str): The user's phone number.
                     - address (str): The user's address.
                     - query (str): The user's query.

        :type post: dict

        :return: Rendered template confirming ticket submission.
        :rtype: http.Response
        """

        
        name = post.get('username')
        email = post.get('email')
        phone = post.get('phone')
        address = post.get('address')
        query = post.get('query')
        
        # find or create a partner based on email 
        partner = request.env['res.partner'].sudo().search([('email','=',email)],limit=1)
        if not partner:
            partner = request.env['res.partner'].sudo().create({
                'name':name,
                'email':email,
                'phone':phone,
            })
        
        # create a helpdesk ticket
        ticket = request.env['helpdesk_app.tickets'].sudo().create({
            'title':f"Ticket from {name}",
            'email':email,
            'phone':phone,
            'reported_by': partner.id,
            'query': query,
            'type': 'external',
        })

        return request.render('helpdesk_app.portal_support_form_received_template',{})
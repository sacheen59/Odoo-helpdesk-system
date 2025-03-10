# -*- coding: utf-8 -*-
# from odoo import http


# class HelpdeskCrm(http.Controller):
#     @http.route('/helpdesk_crm/helpdesk_crm', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/helpdesk_crm/helpdesk_crm/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('helpdesk_crm.listing', {
#             'root': '/helpdesk_crm/helpdesk_crm',
#             'objects': http.request.env['helpdesk_crm.helpdesk_crm'].search([]),
#         })

#     @http.route('/helpdesk_crm/helpdesk_crm/objects/<model("helpdesk_crm.helpdesk_crm"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('helpdesk_crm.object', {
#             'object': obj
#         })


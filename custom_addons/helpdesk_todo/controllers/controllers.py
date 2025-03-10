# -*- coding: utf-8 -*-
# from odoo import http


# class HelpdeskTodo(http.Controller):
#     @http.route('/helpdesk_todo/helpdesk_todo', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/helpdesk_todo/helpdesk_todo/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('helpdesk_todo.listing', {
#             'root': '/helpdesk_todo/helpdesk_todo',
#             'objects': http.request.env['helpdesk_todo.helpdesk_todo'].search([]),
#         })

#     @http.route('/helpdesk_todo/helpdesk_todo/objects/<model("helpdesk_todo.helpdesk_todo"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('helpdesk_todo.object', {
#             'object': obj
#         })


# -*- coding: utf-8 -*-
# from odoo import http


# class TodoApp(http.Controller):
#     @http.route('/todo_app/todo_app', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/todo_app/todo_app/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('todo_app.listing', {
#             'root': '/todo_app/todo_app',
#             'objects': http.request.env['todo_app.todo_app'].search([]),
#         })

#     @http.route('/todo_app/todo_app/objects/<model("todo_app.todo_app"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('todo_app.object', {
#             'object': obj
#         })


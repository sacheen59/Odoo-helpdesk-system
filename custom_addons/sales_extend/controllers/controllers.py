# -*- coding: utf-8 -*-
# from odoo import http


# class SalesExtend(http.Controller):
#     @http.route('/sales_extend/sales_extend', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sales_extend/sales_extend/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sales_extend.listing', {
#             'root': '/sales_extend/sales_extend',
#             'objects': http.request.env['sales_extend.sales_extend'].search([]),
#         })

#     @http.route('/sales_extend/sales_extend/objects/<model("sales_extend.sales_extend"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sales_extend.object', {
#             'object': obj
#         })


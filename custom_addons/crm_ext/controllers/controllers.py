# -*- coding: utf-8 -*-
# from odoo import http


# class CrmExt(http.Controller):
#     @http.route('/crm_ext/crm_ext', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/crm_ext/crm_ext/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('crm_ext.listing', {
#             'root': '/crm_ext/crm_ext',
#             'objects': http.request.env['crm_ext.crm_ext'].search([]),
#         })

#     @http.route('/crm_ext/crm_ext/objects/<model("crm_ext.crm_ext"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('crm_ext.object', {
#             'object': obj
#         })


# -*- coding: utf-8 -*-
# from odoo import http


# class LcAmmendmentJournal(http.Controller):
#     @http.route('/lc_ammendment_journal/lc_ammendment_journal/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/lc_ammendment_journal/lc_ammendment_journal/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('lc_ammendment_journal.listing', {
#             'root': '/lc_ammendment_journal/lc_ammendment_journal',
#             'objects': http.request.env['lc_ammendment_journal.lc_ammendment_journal'].search([]),
#         })

#     @http.route('/lc_ammendment_journal/lc_ammendment_journal/objects/<model("lc_ammendment_journal.lc_ammendment_journal"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('lc_ammendment_journal.object', {
#             'object': obj
#         })

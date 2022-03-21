# -*- coding: utf-8 -*-
# from odoo import http


# class LcFundReqJournal(http.Controller):
#     @http.route('/lc_fund_req_journal/lc_fund_req_journal/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/lc_fund_req_journal/lc_fund_req_journal/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('lc_fund_req_journal.listing', {
#             'root': '/lc_fund_req_journal/lc_fund_req_journal',
#             'objects': http.request.env['lc_fund_req_journal.lc_fund_req_journal'].search([]),
#         })

#     @http.route('/lc_fund_req_journal/lc_fund_req_journal/objects/<model("lc_fund_req_journal.lc_fund_req_journal"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('lc_fund_req_journal.object', {
#             'object': obj
#         })

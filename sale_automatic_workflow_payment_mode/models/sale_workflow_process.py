# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields, api


class SaleWorkflowProcess(models.Model):
    _inherit = "sale.workflow.process"

    payment_filter_id = fields.Many2one(
        'ir.filters',
        string='Payment Filter',
        default=lambda self: self.env.ref(
            'sale_automatic_workflow_payment_mode.'
            'automatic_workflow_payment_filter')
    )
    register_payment = fields.Boolean(string='Register Payment')
    payment_filter_domain = fields.Char(
        string='Payment Filter Domain',
        default="[('state', '=', 'open')]"
    )

    @api.onchange('payment_filter_id')
    def onchange_payment_filter_id(self):
        if self.payment_filter_id:
            self.payment_filter_domain = self.payment_filter_id.domain

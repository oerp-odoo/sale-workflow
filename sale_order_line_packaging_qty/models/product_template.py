# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"


    only_sell_by_pack = fields.Boolean(
        string="Only sell by packaging",
        default=False,
    )

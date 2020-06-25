# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _which_pack_multiple(self, qty):
        self.ensure_one()
        pack_multiple = False
        if qty:
            for pack in self.packaging_ids.sorted("qty", reverse=True):
                if pack.packaging_type_id.can_be_sold and pack.qty:
                    if (qty % pack.qty) == 0:
                        pack_multiple = pack
                        break
        return pack_multiple

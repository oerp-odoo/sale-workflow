# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    @api.constrains(
        "product_id", "product_packaging", "product_id.sell_only_by_packaging"
    )
    def _check_product_packaging(self):
        for line in self:
            if line.product_id.sell_only_by_packaging and not line.product_packaging:
                raise ValidationError(
                    _(
                        "Product %s can only be sold with a packaging."
                        % line.product_id.name
                    )
                )

    @api.onchange("product_id")
    def product_id_change(self):
        res = super().product_id_change()
        if self.product_id.sell_only_by_packaging:
            first_packaging = fields.first(self.product_id.packaging_ids)
            self.update(
                {
                    "product_packaging": first_packaging.id,
                    "product_uom_qty": first_packaging.qty,
                }
            )
        return res

    @api.onchange("product_uom_qty")
    def _onchange_product_uom_qty(self):
        res = super()._onchange_product_uom_qty()
        if not res:
            res = self._check_qty_is_pack_multiple()
        return res

    def _check_qty_is_pack_multiple(self):
        """ Check only for product with sell_only_by_packaging
        """
        # and we dont want to have this warning when we had the product
        if self.product_id.sell_only_by_packaging:
            if not self._is_pack_multiple():
                warning_msg = {
                    "title": _("Product quantity can not be packed"),
                    "message": _(
                        "For the product {prod}\n"
                        "The {qty} is not the multiple of any pack.\n"
                        "Please add a package"
                    ).format(prod=self.product_id.name, qty=self.product_uom_qty),
                }
                return {"warning": warning_msg}
        return {}

    def _is_pack_multiple(self):
        # TODO Consider UOM
        return bool(self.product_id._which_pack_multiple(self.product_uom_qty))

    def write(self, vals):
        # Fill the packaging if they are empty and the quantity is a multiple
        for line in self:
            product_uom_qty = vals.get("product_uom_qty")
            product_packaging = vals.get("product_packaging")
            if line.product_id.sell_only_by_packaging and (
                not line.product_packaging
                or ("product_packaging" in vals and not product_packaging)
            ):
                pack_multiple = line.product_id._which_pack_multiple(product_uom_qty)
                if pack_multiple:
                    vals.update({"product_packaging": pack_multiple.id})
        return super().write(vals)

    @api.model
    def create(self, vals):

        # Fill the packaging if they are empty and the quantity is a multiple
        product = self.env["product.product"].browse(vals.get("product_id"))
        product_uom_qty = vals.get("product_uom_qty")
        # TODO Consider UOM
        product_packaging = vals.get("product_packaging")

        if product and product.sell_only_by_packaging and not product_packaging:
            pack_multiple = product._which_pack_multiple(product_uom_qty)
            if pack_multiple:
                vals.update({"product_packaging": pack_multiple.id})
        return super().create(vals)

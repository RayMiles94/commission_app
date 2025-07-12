from odoo import models


class accountmove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        """
        This is a multi-line comment or docstring.
        Technically, it's a string literal that is ignored if not assigned or used.
        Often used for docstrings for functions/classes/modules.
        """
        for move in self:
            sale_orders = move.invoice_line_ids.mapped("sale_line_ids.order_id")
            sale_orders = sale_orders.filtered(lambda so: so.state != "cancel")
            if sale_orders:
                for order in sale_orders:
                    commission_model = self.env["app.commission.line"].sudo()
                    for x in commission_model.search([("sale_id", "=", order.id)]):
                        x.write({"state": "invoiced", "move_id": move.id})
        super().action_post()

from odoo import models


class saleorder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        """
        Override the default sale order confirmation to create commission lines.
        For each confirmed order:
        - Find active individual commissions linked to the salesperson.
        - Find active splitting commissions linked to the sales team.
        - Generate commission lines using commission_factory for both cases.
        """
        res = super().action_confirm()
        line_model = self.env["app.commission.line"].sudo()
        app_com = self.env["app.commission"].sudo()
        for order in self:
            salesperson = order.user_id
            if not salesperson:
                continue
            commission_id = app_com.search(
                [
                    ("saleperson", "=", salesperson.id),
                    ("commission_category", "=", "individual"),
                    ("state", "=", "active"),
                ]
            )
            self.commission_factory(commission_id, line_model, order, salesperson)
            team_id = order.team_id
            if not team_id:
                continue
            commission_id = app_com.search(
                [
                    ("sale_team", "=", team_id.id),
                    ("commission_category", "=", "splitting"),
                    ("state", "=", "active"),
                ]
            )
            self.commission_factory(commission_id, line_model, order, salesperson)
        return res

    def _migrate_to_compute_commissions(self):
        """
        Legacy method to compute commissions on all confirmed sales orders.
        Searches all sale orders in 'sale' state and generates commission lines
        for both individual and splitting commission categories as in action_confirm.
        """

        line_model = self.env["app.commission.line"].sudo()
        app_com = self.env["app.commission"].sudo()
        self = self.sudo()
        for order in self.search([("state", "=", "sale")]):
            salesperson = order.user_id
            if not salesperson:
                continue
            commission_id = app_com.search(
                [
                    ("saleperson", "=", salesperson.id),
                    ("commission_category", "=", "individual"),
                    ("state", "=", "active"),
                ]
            )
            self.commission_factory(commission_id, line_model, order, salesperson)
            team_id = order.team_id
            if not team_id:
                continue
            commission_id = app_com.search(
                [
                    ("sale_team", "=", team_id.id),
                    ("commission_category", "=", "splitting"),
                    ("state", "=", "active"),
                ]
            )
            self.commission_factory(commission_id, line_model, order, salesperson)

    def commission_factory(self, commission_id, line_model, order, salesperson):
        """
        Helper method to create commission lines for a given commission record.
        Handles parent commission chains recursively if active.
        """

        if len(commission_id) > 0:
            self.create_commission_enitity(
                line_model, commission_id, order, salesperson
            )
            parent = commission_id.parent
            while parent and parent.state == "active":
                self.create_commission_enitity(line_model, parent, order, salesperson)
                parent = parent.parent

    def create_commission_enitity(self, com_model, commission_id, order, salesperson):
        """
        Creates a commission line entity if it does not already exist.
        Determines commission amount and rate based on commission category.
        """

        crm_team = self.env["crm.team"].sudo()
        if len(commission_id) > 1:
            return
        exist = com_model.search(
            [
                ("commission_id", "=", commission_id.id),
                ("commission_user_id", "=", salesperson.id),
                ("sale_id", "=", order.id),
            ]
        )
        commission = 0
        rate = 0
        if len(exist) == 0:
            category = commission_id.commission_category
            object = {}
            if category == "individual":
                commission, rate = self.individual_factory(
                     commission_id, object, order, salesperson
                )
            elif commission_id.commission_category == "leader":
                commission, rate = self.leader_factory(
                    com_model, commission_id, object
                )
            elif commission_id.commission_category == "regional":
                commission, rate = self.regional_factory(
                    com_model, commission_id, crm_team, object
                )
            elif commission_id.commission_category == "splitting":
                return self.splitting_factory(
                    com_model, commission_id, exist, object, order
                )
            object["commission_id"] = commission_id.id
            object["sale_id"] = order.id
            object["commission_amount"] = commission
            object["commission_rate"] = rate
            exist = com_model.create(object)
        return exist

    def splitting_factory(self, com_model, commission_id, exist, object, order):
        """
        Creates commission lines for all members of the sales team for splitting commissions.
        Each member gets a commission based on the fixed percentage defined.
        """

        team = commission_id.sale_team
        for child in team.member_ids:
            object["commission_id"] = commission_id.id
            object["commission_user_id"] = child.id
            object["sale_id"] = order.id
            object["commission_amount"] = order.amount_total * (
                commission_id.fix_qty / 100
            )
            object["commission_rate"] = commission_id.fix_qty
            object["reason"] = "splitting"
            exist = com_model.create(object)
        return exist

    def regional_factory(
        self, com_model, commission_id, crm_team, object
    ):
        """
        Computes the regional manager's commission based on total commissions
        of all teams managed by that regional manager, multiplied by the fixed rate.
        """

        teams = crm_team.search(
            [("regional_manager", "=", commission_id.regional_manager.id)]
        )
        totals = [
            c.commission_amount
            for t in teams
            for c in com_model.search([("commission_user_id", "=", t.user_id.id)])
        ]
        commission = sum(totals) * (commission_id.fix_qty / 100)
        rate = commission_id.fix_qty
        object["commission_user_id"] = commission_id.regional_manager.id
        object["reason"] = "regional"
        return commission, rate

    def leader_factory(self, com_model, commission_id, object):
        """
        Calculates team leader's commission as the sum of commissions
        of all team members multiplied by the fixed commission rate.
        """

        totals = [
            sum(
                line.commission_amount
                for line in com_model.search([("commission_user_id", "=", child.id)])
            )
            for child in commission_id.sale_team.member_ids
        ]
        commission = sum(totals) * (commission_id.fix_qty / 100)
        rate = commission_id.fix_qty
        object["commission_user_id"] = commission_id.sale_manager.id
        object["reason"] = "leader"
        object["sale_team"] = (
            commission_id.sale_team.id if commission_id.sale_team else False
        )
        return commission, rate

    def individual_factory(
        self, commission_id, object, order, salesperson
    ):
        """
        Calculates individual commission based on either a fixed percentage
        of total order amount or a quantity-based rate per product in the order.
        """

        if commission_id.commission_paying_type == "fixed":
            commission = order.amount_total * (commission_id.fix_qty / 100)
        else:
            commission = sum(
                (line.product_uom_qty * line.price_unit)
                * (commission_id.unit_qty / 100)
                for line in order.order_line
            )
        rate = commission_id.fix_qty
        object["commission_user_id"] = salesperson.id
        object["reason"] = "individual"
        object["sale_team"] = (
            commission_id.sale_team.id if commission_id.sale_team else False
        )
        return commission, rate

from datetime import datetime

from odoo import models


class dashboard(models.AbstractModel):
    _name = "app.commission.dashboard"
    _description = "Commission Dashboard"

    def get_euro_display(self, amount):
        """
        Formats the given amount to Euro currency format with 2 decimal places.
        """
        return format(self.env.ref("base.EUR").round(amount), ".2f")

    def get_comission_line(self):
        """
        Returns the 'app.commission.line' model with sudo access.
        """
        return self.env["app.commission.line"].sudo()

    def load_data(self):
        """
        Loads initial data for the commission dashboard including teams, team leaders,
        regions, total sales count, total commissions, revenue, and chart data.
        """
        crm_tam = self.env["crm.team"].sudo()
        user_model = self.env["res.users"].sudo()
        json_teams = [{"id": t.id, "name": t.name} for t in crm_tam.search([])]
        seen = set()
        json_team_leader = []
        for t in crm_tam.search([]):
            item = {"id": t.user_id.id, "name": t.user_id.name}
            key = (item["id"], item["name"])
            if key not in seen:
                seen.add(key)
                json_team_leader.append(item)
        region_domain = [("is_sales_regional_manager", "=", True)]
        json_regions = [
            {"id": u.id, "name": u.name} for u in user_model.search(region_domain)
        ]
        total_sales = self.env["sale.order"].sudo().search_count([])
        total_commissions = self.get_comission_line().search([])
        revenue = sum(com.commission_amount for com in total_commissions)

        results = self.env["app.commission.line"].read_group(
            domain=[],
            fields=["commission_user_id", "commission_amount:sum"],
            groupby=["commission_user_id"],
        )

        user_names = []
        amounts = []

        for r in results:
            user_name = (
                r["commission_user_id"][1] if r["commission_user_id"] else "Unknown"
            )
            amount = round(r["commission_amount"] or 0.0, 2)
            user_names.append(user_name)
            amounts.append(amount)
        return {
            "teams": json_teams,
            "team_leaders": json_team_leader,
            "regions": json_regions,
            "total_sales_count": total_sales,
            "total_commissions": len(total_commissions),
            "revenue": self.get_euro_display(revenue),
            "chart": {"user_names": user_names, "amounts": amounts},
        }

    def filter_data(self, data):
        """
        Filters dashboard data based on filter criteria like start/end dates, role type,
        and data type. Returns filtered sales, commissions, revenue and chart data.
        """
        if "start" not in data:
            return {"error": "Missing attribute: start"}
        if "end" not in data:
            return {"error": "Missing attribute: start"}
        if "role_type" not in data:
            return {"error": "Missing attribute: start"}
        if "data_type" not in data:
            return {"error": "Missing attribute: start"}

        if data["role_type"] == "Teams":
            return self.filter_data_teams(data)
        elif data["role_type"] == "Team Leader":
            return self.filter_team_lead(data)
        elif data["role_type"] == "Regions":
            total_commission_domain = []
            if data["data_type"] == "All":
                regional = [
                    u.id
                    for u in self.env["res.users"]
                    .sudo()
                    .search([("is_sales_regional_manager", "=", True)])
                ]
                total_commission_domain.append(("commission_user_id", "in", regional))
            else:
                total_commission_domain.append(
                    ("commission_user_id", "=", int(data["data_type"]))
                )
            if data["start"] and data["end"]:
                start_date = datetime.strptime(data["start"], "%Y-%m-%d").date()
                end_date = datetime.strptime(data["end"], "%Y-%m-%d").date()
                total_commission_domain.append(("create_date", ">=", start_date))
                total_commission_domain.append(("create_date", "<=", end_date))
            results = self.commission_read_group(total_commission_domain)
            user_names = []
            amounts = []
            for r in results:
                user_name = (
                    r["commission_user_id"][1] if r["commission_user_id"] else "Unknown"
                )
                amount = round(r["commission_amount"] or 0.0, 2)
                user_names.append(user_name)
                amounts.append(amount)
            total_commissions = self.get_comission_line().search(
                total_commission_domain
            )
            revenue = sum(com.commission_amount for com in total_commissions)
            return {
                "total_sales_count": len(total_commissions),
                "total_commissions": len(total_commissions),
                "revenue": self.get_euro_display(revenue),
                "chart_data": {"user_names": user_names, "amounts": amounts},
            }
        return None

    def filter_team_lead(self, data):
        """
        Filters commission data for team leaders based on given criteria.
        """
        total_commission_domain = []
        if data["data_type"] == "All":
            leaders = [u.user_id.id for u in self.env["crm.team"].sudo().search([])]
            total_commission_domain.append(("commission_user_id", "in", leaders))
        else:
            total_commission_domain.append(
                ("commission_user_id", "=", int(data["data_type"]))
            )
        if data["start"] and data["end"]:
            start_date = datetime.strptime(data["start"], "%Y-%m-%d").date()
            end_date = datetime.strptime(data["end"], "%Y-%m-%d").date()
            total_commission_domain.append(("create_date", ">=", start_date))
            total_commission_domain.append(("create_date", "<=", end_date))
        results = self.commission_read_group(total_commission_domain)
        user_names = []
        amounts = []
        for r in results:
            user_name = (
                r["commission_user_id"][1] if r["commission_user_id"] else "Unknown"
            )
            amount = round(r["commission_amount"] or 0.0, 2)
            user_names.append(user_name)
            amounts.append(amount)
        total_commissions = self.get_comission_line().search(total_commission_domain)
        revenue = sum(com.commission_amount for com in total_commissions)
        return {
            "total_sales_count": len(total_commissions),
            "total_commissions": len(total_commissions),
            "revenue": self.get_euro_display(revenue),
            "chart_data": {"user_names": user_names, "amounts": amounts},
        }

    def filter_data_teams(self, data):
        """
        Filters commission and sales data for teams based on given criteria.
        """
        sales_domain = []
        total_commission_domain = []
        if data["data_type"] == "All":
            sales_domain = []
            total_commission_domain = []
        else:
            sales_domain.append(("team_id", "=", int(data["data_type"])))
            total_commission_domain.append(("sale_team", "=", int(data["data_type"])))
        if data["start"] and data["end"]:
            start_date = datetime.strptime(data["start"], "%Y-%m-%d").date()
            end_date = datetime.strptime(data["end"], "%Y-%m-%d").date()
            sales_domain.append(("date_order", ">=", start_date))
            sales_domain.append(("date_order", "<=", end_date))
            total_commission_domain.append(("create_date", ">=", start_date))
            total_commission_domain.append(("create_date", "<=", end_date))
        results = self.commission_read_group(total_commission_domain)
        user_names = []
        amounts = []
        for r in results:
            user_name = (
                r["commission_user_id"][1] if r["commission_user_id"] else "Unknown"
            )
            amount = round(r["commission_amount"] or 0.0, 2)
            user_names.append(user_name)
            amounts.append(amount)
        total_sales = self.env["sale.order"].sudo().search_count(sales_domain)
        total_commissions = self.get_comission_line().search(total_commission_domain)
        revenue = sum(com.commission_amount for com in total_commissions)
        return {
            "total_sales_count": total_sales,
            "total_commissions": len(total_commissions),
            "revenue": self.get_euro_display(revenue),
            "chart_data": {"user_names": user_names, "amounts": amounts},
        }

    def commission_read_group(self, total_commission_domain):
        """
        Helper method to perform read_group operation on app.commission.line
        with given domain, grouped by commission_user_id.
        """
        results = self.env["app.commission.line"].read_group(
            domain=[t for t in total_commission_domain],
            fields=["commission_user_id", "commission_amount:sum"],
            groupby=["commission_user_id"],
        )
        return results

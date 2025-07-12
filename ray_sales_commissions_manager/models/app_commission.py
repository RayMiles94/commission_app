from odoo import fields, models


class app_commission(models.Model):
    _name = "app.commission"
    _description = "Commission"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", required=True)
    state = fields.Selection(
        name="State",
        selection=[("draft", "Draft"), ("active", "Active"), ("done", "Done")],
        default="draft",
    )
    commission_category = fields.Selection(
        string="Category",
        selection=[
            ("individual", "individual"),
            ("splitting", "Splitting commissions"),
            ("leader", "Team Leader"),
            ("regional", "Regional manager"),
        ],
        default="individual",
    )
    commission_type = fields.Many2one(
        string="Commission type", comodel_name="app.commission.type"
    )
    commission_paying_type = fields.Selection(
        selection=[("fixed", "Fixed percentage"), ("products", "By products qty")],
        string="Type",
        required=True,
        default="fixed",
    )
    fix_qty = fields.Float(string="Percentage rate", default=10)
    unit_qty = fields.Float(string="percentage per qty", default=0.1)
    sale_team = fields.Many2one(string="Sale team", comodel_name="crm.team")
    saleperson = fields.Many2one(string="Sale person", comodel_name="res.users")
    sale_manager = fields.Many2one(string="team leader", comodel_name="res.users")
    regional_manager = fields.Many2one(
        string="Regional manager", comodel_name="res.users"
    )
    parent = fields.Many2one(string="Parent", comodel_name="app.commission")
    commission_lines = fields.One2many(
        comodel_name="app.commission.line", inverse_name="commission_id"
    )

    def action_confirm(self):
        """
        Activates the commission by changing its state to 'active'.
        """
        self.write({"state": "active"})

    def action_done(self):
        """
        Marks the commission as completed by setting the state to 'done'.
        """
        self.write({"state": "done"})

    def action_reset(self):
        """
        Resets the commission state back to 'draft' for re-editing or reuse.
        """
        self.write({"state": "draft"})


class CommissionLine(models.Model):
    _name = "app.commission.line"
    _description = "Sales Commission Line"

    commission_id = fields.Many2one(string="Commission", comodel_name="app.commission")
    commission_user_id = fields.Many2one(
        comodel_name="res.users", string="beneficiary", required=True
    )
    sale_id = fields.Many2one("sale.order", string="Sale", required=True)
    commission_amount = fields.Float(string="Amount")
    commission_rate = fields.Float(string="Rate (%)", default=5.0)
    sale_team = fields.Many2one(string="Sale team", comodel_name="crm.team")
    state = fields.Selection(
        string="State",
        selection=[("sale", "Sale Order"), ("invoiced", "Invoiced"), ("done", "Done")],
        default="sale",
    )
    reason = fields.Char(string="Reason")
    move_id = fields.Many2one(comodel_name="account.move")


class app_commission_type(models.Model):
    _name = "app.commission.type"
    _description = "Commission"

    name = fields.Char(string="Type", required=True)

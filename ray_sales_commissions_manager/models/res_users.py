from odoo import fields, models


class res_users(models.Model):
    """
    Extends the res.users model to add sales-related boolean flags
    to identify if a user is a sales regional manager or a team lead.
    """

    _inherit = "res.users"

    is_sales_regional_manager = fields.Boolean(string="Sales Regional manager")
    is_team_lead = fields.Boolean(string="Team lead")

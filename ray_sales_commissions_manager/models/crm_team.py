from odoo import fields, models


class crm_team(models.Model):
    _inherit = "crm.team"

    # Add a reference to a regional manager user on the sales team
    regional_manager = fields.Many2one(
        string="Regional manager", comodel_name="res.users"
    )

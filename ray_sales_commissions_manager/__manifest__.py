{
    "name": "Sales commissions manager",
    "summary": "Sales commissions manager",
    "description": """
        Sales commissions manager
    """,
    "author": "Raouf jabri",
    "website": "https://github.com/RayMiles94/commission_app",
    "category": "Sales",
    "version": "1.0",
    "depends": ["sale_management"],
    "data": [
        # Data
        "data/ir_cron.xml",
        # security
        "security/group.xml",
        "security/ir.model.access.csv",
        # views
        "views/res_users.xml",
        "views/crm_team.xml",
        "views/app_commission.xml",
        "views/commission_dashboard.xml",
        # menu
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ray_sales_commissions_manager/static/src/commission_dashboard/*.xml",
            "ray_sales_commissions_manager/static/src/commission_dashboard/*.css",
            "ray_sales_commissions_manager/static/src/commission_dashboard/*.js",
        ],
    },
    "application": True,
    "auto_install": False,
}

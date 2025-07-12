from odoo.tests.common import TransactionCase


class TestCommission(TransactionCase):
    def setUp(self):
        super().setUp()
        # Create a dummy commission type
        self.commission_type = self.env["app.commission.type"].create(
            {"name": "Test Type"}
        )

        # Get demo users and team
        self.user = self.env.ref("base.user_demo")
        self.team = self.env["crm.team"].create({"name": "Test Sales Team"})

        # Create commission
        self.commission = self.env["app.commission"].create(
            {
                "name": "Test Commission",
                "commission_type": self.commission_type.id,
                "saleperson": self.user.id,
                "sale_team": self.team.id,
            }
        )

    def test_commission_initial_state(self):
        self.assertEqual(
            self.commission.state, "draft", "Initial state should be draft"
        )

    def test_commission_confirm(self):
        self.commission.action_confirm()
        self.assertEqual(
            self.commission.state, "active", "State should change to active"
        )

    def test_commission_done(self):
        self.commission.action_confirm()
        self.commission.action_done()
        self.assertEqual(self.commission.state, "done", "State should change to done")

    def test_commission_reset(self):
        self.commission.action_confirm()
        self.commission.action_reset()
        self.assertEqual(self.commission.state, "draft", "State should reset to draft")

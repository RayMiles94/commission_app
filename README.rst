Sales Commissions Manager
=========================

This Odoo module provides a comprehensive system to manage sales commissions for salespersons, managers, and regional leaders. It includes flexible configuration options for fixed and quantity-based commissions, and detailed tracking of commission lines associated with sales orders.

Features
--------

- Define commission structures with fixed rate or product quantity-based payments.
- Assign commissions to individual salespeople or split among team members.
- Track commission lines linked to sales orders and invoices.
- Manage the commission state lifecycle: Draft → Active → Done.
- Supports different roles: Salesperson, Team Leader, Regional Manager.
- Integrated with Odoo Sales, CRM Teams, and Accounting.

Installation
------------

1. Clone this module into your custom addons directory:

   .. code-block:: bash

      git clone https://github.com/RayMiles94/commission_app

2. Update your Odoo configuration to include the custom addons path.

3. Restart Odoo and install the module via the Apps interface.

Usage
-----

1. You need to have the **Manager** access rights enabled under your User Settings to use this feature.

2. Navigate to **Commissions App**, click on settings then commission.

3. Create a new commission structure, assign team members, and set rates.

4. Confirm the commission to activate it.

5. Commission lines will be automatically linked to sales orders where applicable.

Scheduled Migration of Old Sales Orders
--------------------------------------

After configuring your commission rules and user access, the system provides an automatic scheduled action that helps you migrate historical sales orders. This ensures commissions are computed based on the new configuration for legacy records.

- Runs automatically or can be triggered manually via the scheduled actions menu.
- Filters old sales orders that have no associated commission lines.
- Applies your current commission rules to each applicable order.

**Note:** Ensure all configurations and user permissions are correctly set before running the migration.

Commission Ledger
-----------------

The ledger displays a comprehensive list of all commission lines recorded in the system. It includes detailed information such as:

- **Beneficiary:** The user who receives the commission.
- **Sale Reference:** The related sale order linked to the commission.
- **Commission Amount:** The monetary value of the commission.
- **Commission Rate:** The percentage rate applied to calculate the commission.
- **Sales Team:** The team associated with the sale.
- **Status:** The current state of the commission line (e.g., Sale Order, Invoiced, Done).
- **Reason:** Optional notes or reasons for the commission.

This ledger provides full visibility of commissions to ensure transparency and accurate tracking for payroll and management purposes.

Dashboard Overview
------------------

The app provides a dedicated dashboard that gives users a clear overview of sales performance and commissions. Once the necessary configurations are complete, the dashboard offers the following insights:

- **Sales Order Count:** Displays the total number of confirmed sales orders.
- **Commission Count:** Shows the total number of calculated commission records.
- **Total Revenue:** Summarizes the combined revenue associated with the commissions.
- **Visual Analytics:**
  - A **line chart** showing revenue trends over time.
  - A **bar chart** displaying commissions distributed by salesperson or team.

The dashboard helps sales managers and finance teams track key metrics and analyze commission data at a glance.

Migration Step (v1.1 → v1.2)
------------------------

- The field ``fix_qty`` was renamed to ``fix_rate``.
- Use the provided migration script in ``migrations/1.2/post-migration.py`` to transform legacy data.


To migrate existing sales data before using the commission manager app:

1. Switch to the correct version tag:

   .. code-block:: bash

      git checkout 18.1.2

2. Restart the Odoo server with module upgrade:

   .. code-block:: bash

      ./odoo-bin -u ray_sales_commissions_manager -d your_database_name

This ensures the app is correctly initialized and any existing sales are processed for commission tracking.

Testing
-------

Run unit tests using:

.. code-block:: bash

   odoo-bin --test-enable --init ray_sales_commissions_manager --stop-after-init

Author
------

Developed by **Raouf jabri**
Contact: <raouf_jb@yahoo.fr>

# -*- coding: utf-8 -*-

{
    "name": "Customer Invoice Billing",
    "version": "19.0.1.0.0",
    "summary": "Print temporary invoice billing reports from customer invoices",
    "description": """
        Adds a Billing action on customer invoices.
        Users can review billing details in a wizard and print a temporary
        Invoice Billing PDF for one or more customer invoices.
    """,
    "author": "Thein Htoo Aung",
    "category": "Accounting",
    "license": "LGPL-3",
    "depends": [
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/customer_invoice_billing_wizard_views.xml",
        "views/account_move_views.xml",
        "data/ir_actions_report.xml",
        "reports/customer_invoice_billing_report.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}

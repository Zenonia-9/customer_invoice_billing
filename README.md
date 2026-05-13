# Customer Invoice Billing

![Odoo 19](https://img.shields.io/badge/Odoo-19.0-875A7B?style=flat-square)
![License](https://img.shields.io/badge/License-LGPL--3-blue?style=flat-square)
![Category](https://img.shields.io/badge/Category-Accounting-4ECDC4?style=flat-square)

Print customer invoice billing documents from posted customer invoices in Odoo 19.

This addon introduces a billing wizard that prepares a temporary invoice billing PDF for one or more customer invoices. It is built for practical billing operations: same-customer validation, same-currency validation, editable bank information, contact details, approval fields, and separate A4/A5 report outputs.

## Highlights

- Adds a billing action on `account.move` for **customer invoices**.
- Validates that all selected invoices are:
  - posted
  - customer invoices
  - for the same customer
  - in the same currency
- Supports **multi-invoice billing** in one print flow.
- Includes configurable **billing date**, **period range**, **remark**, and **sequence number** fields.
- Preloads a set of **bank account lines** inside the wizard.
- Remembers common user inputs such as contact and approval fields.
- Includes **Studio-safe preview handling** by tolerating empty preview contexts.
- Ships with dedicated **A4** and **A5** billing reports.

## Workflow

1. Select one or more posted customer invoices.
2. Launch the **Invoice Billing** wizard.
3. Review billing period, contact information, approver/preparer details, and bank lines.
4. Choose A4 or A5 output.
5. Print the invoice billing PDF.

## Technical Notes

- `models/account_move.py`
  Adds the billing action and validates invoice selection before the wizard opens.
- `wizards/customer_invoice_billing_wizard.py`
  Drives the full billing workflow, including defaults, remembered inputs, bank lines, remarks, and report dispatching.
- `reports/customer_invoice_billing_report.py`
  Builds report data for both normal printing and preview/studio contexts.
- `data/ir_actions_report.xml`
  Declares separate report actions for the supported output formats.

## Module Layout

```text
customer_invoice_billing/
|-- data/
|-- models/
|-- reports/
|-- security/
|-- views/
|-- wizards/
`-- __manifest__.py
```

## Dependencies

- `account`

## Installation

1. Place the module in your custom addons path.
2. Update the Apps list in Odoo.
3. Install **Customer Invoice Billing**.

## License

This module is licensed under `LGPL-3`.

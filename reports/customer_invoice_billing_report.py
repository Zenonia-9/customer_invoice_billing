from odoo import api, models


class CustomerInvoiceBillingReport(models.AbstractModel):
    _name = "report.customer_invoice_billing.report_invoice_billing_document"
    _description = "Customer Invoice Billing Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        data = data or {}
        wizard_id = data.get("wizard_id")
        wizard = self.env["customer.invoice.billing.wizard"]
        if wizard_id:
            wizard = wizard.browse(wizard_id).exists()

        if not wizard:
            active_ids = data.get("active_ids") or docids or self.env.context.get("active_ids") or []
            if not active_ids and self.env.context.get("active_id"):
                active_ids = [self.env.context["active_id"]]
            active_ids = [active_id for active_id in active_ids if active_id]

            wizard = self.env["customer.invoice.billing.wizard"].with_context(
                active_model="account.move",
                active_ids=active_ids,
                studio=data.get("studio"),
                customer_invoice_billing_allow_empty=data.get("studio"),
            ).create({})

        return {
            "doc_ids": wizard.ids,
            "doc_model": "customer.invoice.billing.wizard",
            "docs": wizard,
            "data": data,
        }


class CustomerInvoiceBillingReportA5(models.AbstractModel):
    _name = "report.customer_invoice_billing.invoice_billing_doc_a5"
    _description = "Customer Invoice Billing Report A5"
    _inherit = "report.customer_invoice_billing.report_invoice_billing_document"

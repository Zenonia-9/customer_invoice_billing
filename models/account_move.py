from odoo import _, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _validate_customer_invoice_billing_selection(self):
        invoices = self.exists()

        if not invoices:
            raise UserError(_("No customer invoices selected."))

        if any(invoice.state != 'posted' for invoice in invoices):
            raise UserError(_("You can only print billing for posted invoices."))

        if any(
            invoice.move_type not in ("out_invoice", "out_refund")
            for invoice in invoices
        ):
            raise UserError(
                _("Billing can only be printed for customer invoices and credit notes.")
            )

        partner = invoices[0].partner_id
        if not partner or any(invoice.partner_id != partner for invoice in invoices):
            raise UserError(_("All selected invoices must have the same customer."))

        currency = invoices[0].currency_id
        if not currency or any(invoice.currency_id != currency for invoice in invoices):
            raise UserError(_("All selected invoices must use the same currency."))

        return invoices

    def action_open_customer_invoice_billing(self):
        invoices = self._validate_customer_invoice_billing_selection()

        return {
            "type": "ir.actions.act_window",
            "name": _("Invoice Billing"),
            "res_model": "customer.invoice.billing.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_ids": invoices.ids,
                "active_model": "account.move",
            },
        }

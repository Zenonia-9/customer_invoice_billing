from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CustomerInvoiceBillingBankLine(models.TransientModel):
    _name = "customer.invoice.billing.bank.line"
    _description = "Customer Invoice Billing Bank Line"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    wizard_id = fields.Many2one(
        "customer.invoice.billing.wizard",
        required=True,
        ondelete="cascade",
    )
    account_number = fields.Char(string="Account Number", required=True)
    account_name = fields.Char(string="Account Name", required=True)
    bank_name = fields.Char(string="Bank Name", required=True)
    currency_name = fields.Char(string="Currency", required=True)


class CustomerInvoiceBillingWizard(models.TransientModel):
    _name = "customer.invoice.billing.wizard"
    _description = "Customer Invoice Billing Wizard"

    DEFAULT_BANK_LINES = (
        {
            "sequence": 10,
            "account_number": "000-501-020-000-1214",
            "account_name": "Victoria Hospital",
            "bank_name": "A Bank",
            "currency_name": "Kyats",
        },
        {
            "sequence": 20,
            "account_number": "200-005-955-84",
            "account_name": "Victoria Hospital",
            "bank_name": "AYA Bank",
            "currency_name": "Kyats",
        },
        {
            "sequence": 30,
            "account_number": "3181-0331-8002-57501",
            "account_name": "Victoria Hospital",
            "bank_name": "KBZ Bank",
            "currency_name": "Kyats",
        },
        {
            "sequence": 40,
            "account_number": "0010-1005-0002-2233",
            "account_name": "Victoria Hospital",
            "bank_name": "CB Bank",
            "currency_name": "Kyats",
        },
    )

    # paper_size = fields.Selection(
    #     selection=[
    #         ("a4", "A4"),
    #         ("a5", "A5"),
    #     ],
    #     string="Paper Size",
    #     required=True,
    #     default="a4",
    # )
    billing_date = fields.Date(
        string="Billing Date",
        required=True,
        default=fields.Date.context_today,
    )
    sequence_no = fields.Char(string="Sq. No.")
    remark = fields.Selection(
        selection=[
            ("one_week", "One Week"),
            ("one_month", "One Month"),
            ("two_months", "Two Months"),
            ("other", "Other"),
        ],
        default="one_month",
        string="Remark",
    )
    custom_remark = fields.Text(string="Other Remark")
    total_amount = fields.Monetary(
        string="Total Amount",
        currency_field="currency_id",
        readonly=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        readonly=True,
    )
    invoice_ids = fields.Many2many(
        "account.move",
        string="Invoices",
        readonly=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        readonly=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        readonly=True,
    )

    bill_to_partner_id = fields.Many2one(
        "res.partner",
        string="Bill To Partner",
        readonly=True,
    )
    bill_to_text = fields.Text(string="Bill To")
    from_text = fields.Text(string="From")

    contact_name = fields.Char(string="Contact Name")
    contact_phone = fields.Char(string="Contact Phone")
    contact_email = fields.Char(string="Contact Email")

    approved_by_name = fields.Char(string="Approved By Name")
    approved_by_position = fields.Char(string="Approved By Position")
    prepared_by_name = fields.Char(string="Prepared By Name")
    prepared_by_position = fields.Char(string="Prepared By Position")

    bank_line_ids = fields.One2many(
        "customer.invoice.billing.bank.line",
        "wizard_id",
        string="Bank Information",
    )

    @api.model
    def _last_input_key(self, field_name, partner=None):
        key = f"customer_invoice_billing.last.user_{self.env.uid}.{field_name}"
        if partner:
            key = f"customer_invoice_billing.last.user_{self.env.uid}.partner_{partner.id}.{field_name}"
        return key

    @api.model
    def _get_last_input(self, field_name, fallback="", partner=None):
        value = self.env["ir.config_parameter"].sudo().get_param(
            self._last_input_key(field_name, partner=partner)
        )
        return value if value not in (False, None) else fallback

    @api.model
    def _validate_invoices(self, invoices):
        invoices = invoices.exists()

        if not invoices:
            raise UserError(_("No customer invoices selected."))

        if any(invoice.move_type != "out_invoice" for invoice in invoices):
            raise UserError(_("All selected records must be customer invoices."))

        partner = invoices[0].partner_id
        if not partner or any(invoice.partner_id != partner for invoice in invoices):
            raise UserError(_("Selected invoices must have the same customer."))

        currency = invoices[0].currency_id
        if not currency or any(invoice.currency_id != currency for invoice in invoices):
            raise UserError(_("Selected invoices must have the same currency."))

        return invoices

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        active_ids = self.env.context.get("active_ids") or []
        active_id = self.env.context.get("active_id")
        if not active_ids and active_id:
            active_ids = [active_id]

        if self.env.context.get("active_model") and self.env.context.get("active_model") != "account.move":
            raise UserError(_("Invoice Billing must be opened from customer invoices."))

        invoices = self.env["account.move"].browse(active_ids)
        invoices = self._validate_invoices(invoices)

        partner = invoices[0].partner_id
        currency = invoices[0].currency_id
        company = self.env.company

        res.update(
            {
                # "paper_size": res.get("paper_size") or "a4",
                "invoice_ids": [(6, 0, invoices.ids)],
                "partner_id": partner.id,
                # "bill_to_partner_id": partner.id,
                "bill_to_text": partner.display_name or partner.name or "",
                "from_text": company.name or "Victoria Hospital",
                "currency_id": currency.id,
                "company_id": company.id,
                "total_amount": sum(invoices.mapped("amount_total")),
                "contact_name": self._get_last_input(
                    "contact_name",
                    fallback=partner.name or "",
                    partner=partner,
                ),
                "contact_phone": self._get_last_input(
                    "contact_phone",
                    fallback=partner.phone or "",
                    partner=partner,
                ),
                "contact_email": self._get_last_input(
                    "contact_email",
                    fallback=partner.email or "",
                    partner=partner,
                ),
                "approved_by_name": self._get_last_input("approved_by_name"),
                "approved_by_position": self._get_last_input("approved_by_position"),
                "prepared_by_name": self._get_last_input("prepared_by_name"),
                "prepared_by_position": self._get_last_input("prepared_by_position"),
                "bank_line_ids": [
                    (0, 0, dict(line_values))
                    for line_values in self.DEFAULT_BANK_LINES
                ],
            }
        )

        return res

    def _save_last_inputs(self):
        self.ensure_one()
        config = self.env["ir.config_parameter"].sudo()

        partner_fields = ("contact_name", "contact_phone", "contact_email")
        for field_name in partner_fields:
            if self.partner_id:
                config.set_param(
                    self._last_input_key(field_name, partner=self.partner_id),
                    self[field_name] or "",
                )

        global_fields = (
            "approved_by_name",
            "approved_by_position",
            "prepared_by_name",
            "prepared_by_position",
        )
        for field_name in global_fields:
            config.set_param(self._last_input_key(field_name), self[field_name] or "")

    def _get_invoice_vendor_ref(self, invoice):
        self.ensure_one()
        if "vendor_ref" not in invoice._fields:
            return ""
        return invoice.vendor_ref or ""

    def _get_invoice_anzer_id(self, invoice):
        self.ensure_one()
        if "anzer_id" not in invoice._fields:
            return ""
        return invoice.anzer_id or ""

    def _get_invoice_cpi(self, invoice):
        self.ensure_one()
        vendor_ref = self._get_invoice_vendor_ref(invoice)
        digits = "".join(char for char in vendor_ref if char.isdigit())
        return digits[-6:] if digits else ""

    def _get_remark_text(self):
        self.ensure_one()
        remark_map = {
            "one_week": _("Please kindly pay this invoice within one week."),
            "one_month": _("Please kindly pay this invoice within one month."),
            "two_months": _("Please kindly pay this invoice within two months."),
        }
        if self.remark == "other":
            return self.custom_remark or ""
        return remark_map.get(self.remark, "")

    # def _get_paper_size_label(self):
    #     self.ensure_one()
    #     return dict(self._fields["paper_size"].selection).get(self.paper_size, "")

    def action_print_billing(self):
        self.ensure_one()
        self._validate_invoices(self.invoice_ids)
        self._save_last_inputs()

        return self.env.ref(
            "customer_invoice_billing.action_report_customer_invoice_billing"
        ).report_action(self)

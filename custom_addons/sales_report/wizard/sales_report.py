from odoo import models, fields, api
from collections import defaultdict


class SalesReportWizard(models.TransientModel):
    _name = "sales.report.wizard"
    _description = "Sales Report Wizard"

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)

    def action_show(self):
        self.ensure_one()
        return self.env.ref("sales_report.action_sales_report_pdf").report_action(self)

    def get_most_sold_products(self):
        self.ensure_one()

        # Find confirmed sale orders in date range
        orders = self.env["sale.order"].search(
            [
                ("date_order", ">=", self.start_date),
                ("date_order", "<=", self.end_date),
                ("state", "in", ["sale", "done"]),
            ]
        )

        # Aggregate quantities by product
        product_quantities = defaultdict(float)
        for order in orders:
            for line in order.order_line:
                if line.product_id:
                    product_quantities[line.product_id] += line.product_uom_qty

        # Sort and get top 5
        sorted_products = sorted(
            product_quantities.items(), key=lambda x: x[1], reverse=True
        )

        return [
            {"product": product.display_name, "quantity": qty}
            for product, qty in sorted_products
        ]

    def get_least_sold_products(self):
        self.ensure_one()

        orders = self.env["sale.order"].search(
            [
                ("date_order", ">=", self.start_date),
                ("date_order", "<=", self.end_date),
                ("state", "in", ["sale", "done"]),
            ]
        )

        product_quantities = defaultdict(float)
        for order in orders:
            for line in order.order_line:
                if line.product_id:
                    product_quantities[line.product_id] += line.product_uom_qty

        # Sort ascending and get bottom 5
        sorted_products = sorted(product_quantities.items(), key=lambda x: x[1])

        return [
            {"product": product.display_name, "quantity": qty}
            for product, qty in sorted_products
        ]

    def get_top_salespeople(self):
        self.ensure_one()

        orders = self.env["sale.order"].search(
            [
                ("date_order", ">=", self.start_date),
                ("date_order", "<=", self.end_date),
                ("state", "in", ["sale", "done"]),
            ]
        )

        # Aggregate totals by salesperson
        user_totals = defaultdict(float)
        for order in orders:
            if order.user_id:
                user_totals[order.user_id] += order.amount_total

        # Sort and get top 5
        sorted_users = sorted(user_totals.items(), key=lambda x: x[1], reverse=True)

        return [{"user": user.name, "total": total} for user, total in sorted_users]

    def get_most_buying_customers(self):
        self.ensure_one()

        orders = self.env["sale.order"].search(
            [
                ("date_order", ">=", self.start_date),
                ("date_order", "<=", self.end_date),
                ("state", "in", ["sale", "done"]),
            ]
        )

        customer_purchases = defaultdict(int)

        for order in orders:
            customer_purchases[order.partner_id.display_name] += 1

        # Sort ascending and get bottom 5
        sorted_customer_purchases = sorted(
            customer_purchases.items(), key=lambda x: x[1], reverse=True
        )

        return [
            {"customer": customer, "num_of_orders": num_of_orders}
            for customer, num_of_orders in sorted_customer_purchases
        ]

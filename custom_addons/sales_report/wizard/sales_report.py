from odoo import models, fields, api


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
        lang = self.env.context.get("lang") or "en_US"
        query = """
            SELECT COALESCE(p.name->>%s, p.name->>'en_US') AS product_name,
                   SUM(sol.product_uom_qty) AS quantity
            FROM sale_order_line sol
            JOIN sale_order so ON sol.order_id = so.id
            JOIN product_product pp ON sol.product_id = pp.id
            JOIN product_template p ON pp.product_tmpl_id = p.id
            WHERE so.date_order::date BETWEEN %s AND %s
              AND so.state IN ('sale', 'done')
            GROUP BY p.id, p.name
            ORDER BY quantity DESC
            LIMIT 5
        """
        self.env.cr.execute(query, (lang, self.start_date, self.end_date))
        return [{"product": r[0], "quantity": r[1]} for r in self.env.cr.fetchall()]

    def get_least_sold_products(self):
        self.ensure_one()
        lang = self.env.context.get("lang") or "en_US"
        query = """
            SELECT COALESCE(p.name->>%s, p.name->>'en_US') AS product_name,
                   SUM(sol.product_uom_qty) AS quantity
            FROM sale_order_line sol
            JOIN sale_order so ON sol.order_id = so.id
            JOIN product_product pp ON sol.product_id = pp.id
            JOIN product_template p ON pp.product_tmpl_id = p.id
            WHERE so.date_order::date BETWEEN %s AND %s
              AND so.state IN ('sale', 'done')
            GROUP BY p.id, p.name
            ORDER BY quantity ASC
            LIMIT 5
        """
        self.env.cr.execute(query, (lang, self.start_date, self.end_date))
        return [{"product": r[0], "quantity": r[1]} for r in self.env.cr.fetchall()]

    def get_top_salespeople(self):
        self.ensure_one()
        query = """
            SELECT rp.name AS user_name,
                   SUM(so.amount_total) AS total
            FROM sale_order so
            JOIN res_users u ON so.user_id = u.id
            JOIN res_partner rp ON u.partner_id = rp.id
            WHERE so.date_order::date BETWEEN %s AND %s
              AND so.state IN ('sale', 'done')
            GROUP BY rp.id, rp.name
            ORDER BY total DESC
            LIMIT 5
        """
        self.env.cr.execute(query, (self.start_date, self.end_date))
        return [{"user": r[0], "total": r[1]} for r in self.env.cr.fetchall()]

from odoo import fields, models


class SimpleProductionBom(models.Model):
    _name = 'simple.production.bom'
    _rec_name = 'bom_product_id'

    bom_product_id = fields.Many2one('product.product', string="Product")
    bom_quantity = fields.Integer(string='Quantity', default=1)
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user,
                                 string="Company")
    user_id = fields.Many2one('res.users',
                              default=lambda self: self.env.company,
                              string="Responsible Person")

    production_line_ids = fields.One2many("components.order.line",
                                          "bom_line_id")

from odoo import fields, models


class ComponentsOrderLine(models.Model):
    _name = 'components.order.line'

    components_id = fields.Many2one('product.product', string='Components')
    consumed_qty = fields.Integer(String="To Consume")

    production_id = fields.Many2one("simple.production")
    bom_line_id = fields.Many2one("simple.production.bom")

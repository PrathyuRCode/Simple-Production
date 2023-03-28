from odoo import fields, models, api


class SimpleProduction(models.Model):
    _name = 'simple.production'
    _inherit = 'mail.thread'
    _rec_name = 'product_id'

    reference_no = fields.Char(readonly=True)
    product_id = fields.Many2one('product.product', string="Product")
    quantity = fields.Integer(string="Quantity", default=1)
    user_id = fields.Many2one('res.users', string="Responsible Person",
                              default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env.company)
    request_date = fields.Date(String="Request Date",
                               default=fields.Datetime.now)
    bom_id = fields.Many2one('simple.production.bom', string="BOM")
    order_move_ids = fields.Many2many('stock.move')

    production_line_ids = fields.One2many("components.order.line",
                                          "production_id")

    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('confirmed', 'confirmed'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Canceled'),
    ], string='Status', required=True, readonly=True, copy=False,
        tracking=True, default='draft')

    @api.model
    def create(self, vals):
        if vals.get('reference_no', 'New') == 'New':
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'simple.production') or 'New'
        res = super(SimpleProduction, self).create(vals)
        return res

    @api.onchange('bom_id')
    def _onchange_bom(self):
        #     print(self,"ssss")
        for i in self.bom_id.production_line_ids:
            #         print(i)
            vals = {
                'components_id': i.components_id,
                'consumed_qty': i.consumed_qty
            }
            self.write({
                'production_line_ids': [(0, 0, vals)],
                'product_id': self.bom_id.bom_product_id.id,
                'quantity': self.bom_id.bom_quantity
            })

    def button_immediate_confirm(self):
        self.state = 'confirmed'

    def button_immediate_progress(self):
        self.state = 'in_progress'

    def button_immediate_done(self):
        self.state = 'done'

        product_create = self.product_id
        ref_no = self.reference_no
        source_loc =\
            self.env.ref('simple_production.simple_production_location')
        dest_loc = self.env.ref('stock.stock_location_stock')
        quan = self.quantity

        move = self.env['stock.move'].create({
            'name': 'Simple production',
            'product_id': product_create.id,
            'location_id': source_loc.id,
            'location_dest_id': dest_loc.id,
            'product_uom_qty': quan,
            'origin': ref_no
        })

        self.write({
            'order_move_ids': [(4, move.id)]
        })

        move._action_confirm()
        move.write({
            'state': 'done'
        })
        move.move_line_ids.write({
            'qty_done': quan,
        })

        move._action_done()

        print(move.state)

        for i in self.production_line_ids:
            consumed_pro = i.components_id
            consumed_source_loc = self.env.ref('stock.stock_location_stock')
            consumed_dest_loc =\
                self.env.ref('simple_production.simple_production_location')
            consumed_pro_qty = i.consumed_qty
            ref_no = self.reference_no

            consumed_move = self.env['stock.move'].create({
                'name': 'Simple production',
                'product_id': consumed_pro.id,
                'location_id': consumed_source_loc.id,
                'location_dest_id': consumed_dest_loc.id,
                'product_uom_qty': consumed_pro_qty,
                'origin': ref_no
            })
            print(consumed_move)

            self.write({
                'order_move_ids': [(4, consumed_move.id)]
            })
            consumed_move._action_confirm()
            consumed_move.write({
                'state': 'done'
            })
            consumed_move.move_line_ids.write({
                'qty_done': consumed_pro_qty,
            })
            consumed_move._action_done()

    def button_immediate_cancel(self):
        self.state = 'cancel'

    def simple_product_move(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Product Move',
            'view_mode': 'tree',
            'view_id': self.env.ref('stock.view_move_tree').id,
            'res_model': 'stock.move',
            'domain': [('id', 'in', self.order_move_ids.ids)]
        }

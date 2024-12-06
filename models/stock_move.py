from odoo import models, fields, api
from odoo.exceptions import UserError

class StockMove(models.Model):
    _inherit = 'stock.move'

    peso_promedio = fields.Float(string='Peso Promedio', compute='_compute_peso_promedio')
    rollos_promedio = fields.Float(string='Rollos Promedio', compute='_compute_rollos_promedio')

    @api.depends('product_id')
    def _compute_peso_promedio(self):
        for record in self:
            if record.product_id.product_cosal == 'rollo':
                record.peso_promedio = record.product_id.peso_promedio
            else:
                record.peso_promedio = 0.0 
           

    @api.depends('product_id', 'product_uom_qty')
    def _compute_rollos_promedio(self):
        for record in self:
            if record.product_id.product_cosal == 'rollo':
                try:
                    record.rollos_promedio = record.product_uom_qty / record.product_id.peso_promedio
                except ZeroDivisionError:
                    record.rollos_promedio = 0.0
            else:
                record.rollos_promedio = 0.0

    
from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    peso_promedio = fields.Float(string='Peso Promedio')
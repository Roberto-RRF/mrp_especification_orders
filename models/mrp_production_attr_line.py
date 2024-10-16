# Este modelo no tiene sentido

from odoo import models, fields

class MrpProductionAtrrLine(models.Model):
    _name = 'mrp.production.attr.line'

    production_id = fields.Many2one('mrp.production', string='Production Order')

    familia = fields.Char(string='Familia')
    subfamilia = fields.Char(string='Subfamilia')
    tipo = fields.Char(string='Tipo')
    color = fields.Char(string='Color')
    gramaje = fields.Char(string='Gramaje')
    medida = fields.Char(string='Medida')


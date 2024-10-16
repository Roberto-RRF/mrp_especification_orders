
from odoo import models, fields

class MrpProductionRollCut(models.Model):
    _name = 'mrp.production.roll.cut'

    num = fields.Integer("# Pasada")
    centro = fields.Integer("Centro")
    diametro = fields.Integer("Diametro")
    production_id = fields.Many2one('mrp.production', string='Production Order')
    lines = fields.One2many('mrp.production.roll.cut.line', 'cut_line_ids', string='Lineas de Corte', ondelete='cascade')

class MrpProductionRollCutLine(models.Model):
    _name = 'mrp.production.roll.cut.line'

    cut_line_ids = fields.Many2one('mrp.production.roll.cut')
    pos = fields.Integer("POS")
    medida = fields.Char("medida cm")
    medir_en = fields.Char("Medir en")
    kilos = fields.Integer("Kilos")
    destino = fields.Char("Destino")


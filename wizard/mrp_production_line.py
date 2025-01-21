from odoo import models, fields, api

class MrpProductionLine(models.TransientModel):
    _name = 'mrp.production.line'
    _description = 'Wizard for Printing Work Sheet Line'

    pasada = fields.Char("Pasada")
    centro = fields.Char("Centro")
    diametro = fields.Char("Diametro")

    lines_details = fields.One2many('mrp.production.line.detail', 'line_details', string='Lineas de Corte', ondelete='cascade')
    wizard_id = fields.Many2one('mrp.production.wizard', string="Production Wizard")
    
class MrpProductionLine(models.TransientModel):
    _name = 'mrp.production.line.detail'
    _description = 'Wizard for Printing Work Sheet Line Detail'

    pos = fields.Char("POS")
    medida = fields.Char("Medida (cms)")
    diferencia = fields.Char("Diferencia (cms)")
    medir_en = fields.Char("Medir a")    
    kilos = fields.Char("Kilos")    
    destino = fields.Char("Destino")

    line_details = fields.Many2one('mrp.production.line')
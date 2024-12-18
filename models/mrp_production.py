from odoo import models, fields, api
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # Variables Compartidas
    to_cut_rolls = fields.Integer("Rollos a Cortar", compute="_compute_to_cut_rolls")
    sale_type = fields.Selection([
        ('exact', 'Cantidad Exacta'),
        ('complete', 'Rollo Completo'),
    ], string ="Tipo de Venta", default="complete")
    
    # Variables de Rollo
    to_cut = fields.Integer("Numero de Pasadas")

    # Variables de Hoja
    millares_vendidos = fields.Char("Millares Vendidos")
    medida = fields.Char("Medida (cms)")
    kilos = fields.Char("Kilos")
    destino = fields.Char("Destino")
    empacar_en = fields.Char("Empacar en")
    hojas_por_empaque = fields.Char("Hojas por empaque")
    tarimas = fields.Char("Tarimas")
    
    tarimas_iguales = fields.Boolean("Todas las tarimas son iguales", default=True)
    detalles_tarimas = fields.Many2many(
        'mrp.production.detalles.tarima',
        string="Detalles Tarimas"
    )
    is_roll = fields.Boolean("Es rollo", compute="_compute_is_roll", store=False)

    @api.depends('product_id')
    def _compute_is_roll(self):
        for record in self:
            # Check if the product has the 'rollo' value for product_cosal
            if record.product_id.product_cosal == 'rollo':
                record.is_roll = True
            else:
                record.is_roll = False

    @api.depends('move_raw_ids')
    def _compute_to_cut_rolls(self):
        suma = 0
        for record in self:
            for move in record.move_raw_ids:
                suma+= move.rollos_promedio
            record.to_cut_rolls = suma

    def action_open_work_sheet_wizard(self):
        resultant_products = self.product_id | self.move_finished_ids.mapped('product_id')

        source_products = self.move_raw_ids.mapped('product_id').filtered(
            lambda p: p.product_cosal in ['rollo', 'hoja']
        )
        source_product = source_products[:1]

        centro = resultant_products[0].product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Centro").name
        diametro = resultant_products[0].product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Diametro").name

        source_size = source_product.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Ancho cm").name
        resultant_sizes = []
        for product in resultant_products:
            # Filter the attribute values for "Ancho cm"
            ancho_cm_values = product.product_template_attribute_value_ids.filtered(
                lambda a: a.attribute_id.name == "Ancho cm"
            )
            # Append the names of the filtered values to resultant_sizes
            resultant_sizes.extend(ancho_cm_values.mapped('name'))
        sale_type = {
            'exact': 'Cantidad Exacta',
            'complete': 'Rollo Completo',
        }
        print("\n\n\n")
        print(sale_type[self.sale_type])
        return {    
            'name': 'Imprimir Hoja de Trabajo',
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_production_id': self.id,
                'default_to_cut': self.to_cut,
                'default_to_cut_rolls': self.to_cut_rolls,
                'default_sale_type': sale_type[self.sale_type],
                'default_resultant_products_ids': [(6, 0, resultant_products.ids)], 
                'default_source_product_id': source_product.id,
                'default_is_roll': self.is_roll,
                'default_centro': centro,
                'default_diametro': diametro,
                'default_millares_vendidos': self.millares_vendidos,
                'default_medida': self.medida,
                'default_kilos': self.kilos,
                'default_destino': self.destino,
                'default_empacar_en': self.empacar_en,
                'default_hojas_por_empaque': self.hojas_por_empaque,
                'default_tarimas': self.tarimas,
                
                'source_size':source_size,
                'resultant_sizes':resultant_sizes
            },
        }
    
class DestallesTarima(models.Model):
    _name = 'mrp.production.detalles.tarima'
    _description = 'Detalles Tarimas'

    name = fields.Char(string="Name")
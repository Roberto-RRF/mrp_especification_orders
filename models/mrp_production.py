from odoo import models, fields, api
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'


    to_cut = fields.Integer("Numero de Pasadas")
    to_cut_rolls = fields.Integer("Rollos a Cortar")
    sale_type = fields.Char("Tipo de Venta")

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
                'default_sale_type': self.sale_type,
                'default_resultant_products_ids': [(6, 0, resultant_products.ids)], 
                'default_source_product_id': source_product.id,

                'default_centro': centro,
                'default_diametro': diametro,

                'source_size':source_size,
                'resultant_sizes':resultant_sizes
            },
        }
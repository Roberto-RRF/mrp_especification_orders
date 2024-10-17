from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    attr_line_ids = fields.One2many('mrp.production.attr.line', 'production_id')
    cut_line_ids = fields.One2many('mrp.production.roll.cut', 'production_id')
    to_cut = fields.Integer("Numero de Pasadas")
    @api.model
    def create(self, vals):
        """Override create method to handle move_raw_ids changes on record creation."""
        production = super(MrpProduction, self).create(vals)
        production._compute_attr_lines()
        return production

    def write(self, vals):
        """Override write method to trigger recalculation when move_raw_ids changes."""
        result = super(MrpProduction, self).write(vals)
        if 'move_raw_ids' in vals:
            self._compute_attr_lines()
        return result


    @api.onchange('move_raw_ids')
    def _compute_attr_lines(self):
        """Method to delete related attr lines and recalculate new ones."""
        for production in self:

            production.attr_line_ids.unlink()
            for move in production.move_raw_ids:

                familia = move.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Familia")
                subfamilia = move.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Subfamilia")
                tipo = move.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Tipo")
                color = move.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Color")
                gramaje = move.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Gramos")
                medida = move.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Ancho cm")

                if move.product_id.product_cosal in ('rollo', 'hoja'):
                    new_lines = []
                    if familia:
                        new_line = (0, 0, {
                            'production_id': production.id,
                            'familia': familia.name,
                            'subfamilia': subfamilia.name,
                            'tipo': tipo.name,
                            'color': color.name, 
                            'gramaje': gramaje.name,  
                            'medida': medida.name,

                        })
                        new_lines.append(new_line)

                    production.write({'attr_line_ids': new_lines})
                    break
    
    @api.constrains('to_cut')
    @api.depends('to_cut')
    def _compute_cut_ids(self):
        for production in self:
            production.cut_line_ids.unlink()

            final_product = production.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Ancho cm").name
            centro = production.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Centro").name
            diametro = production.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Diametro").name
            print("Centro: "+centro)
            print("Diametro: "+diametro)
            supply_measure = production.attr_line_ids[0].medida

            division_entera = int(float(supply_measure)//float(final_product))

            for cut_index in range(0, production.to_cut):
                lines = []
                cut_lines = []
                sum_pas = 0
                sum = 0

                pos_ascii = 65
                while sum +(float(supply_measure)%float(final_product)) < float(supply_measure):
                    sum += float(final_product)
                    lines.append((0,0,{
                        'pos':chr(pos_ascii),
                        'medida': str(sum_pas) + ' - ' + str(sum),
                        'dif_medida': str(sum_pas - sum),
                        'medir_en':'cms',
                        'kilos':9999,
                        'destino':'cliente',
                    }))
                    sum_pas = sum
                    pos_ascii += 1
                lines.append((0,0,{
                    'pos':chr(pos_ascii),
                    'medida': str(sum) + ' - ' + str(supply_measure),
                    'dif_medida': str(sum - float(supply_measure)),
                    'medir_en':'cms',
                    'kilos':9999,
                    'destino':'merma',
                }))


                cut_lines.append((0,0,{
                    'production_id': production.id,
                    'num': cut_index +1,
                    'centro': centro, 
                    'diametro': diametro,  
                    'lines':lines
                }))
                production.write({'cut_line_ids': cut_lines})
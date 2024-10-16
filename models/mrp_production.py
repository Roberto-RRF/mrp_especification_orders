from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    attr_line_ids = fields.One2many('mrp.production.attr.line', 'production_id')
    cut_line_ids = fields.One2many('mrp.production.roll.cut', 'production_id')
    to_cut = fields.Integer("Rollos a cortar")
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

            to_produce_measure = production.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Ancho cm").name
            supply_measure = production.attr_line_ids[0].medida

            print("Producto Resultante: "+str(to_produce_measure))
            print("Materia prima: "+str(supply_measure))
            print("Division: "+str(float(supply_measure)/float(to_produce_measure)))
            print("Division entera: "+str(float(supply_measure)//float(to_produce_measure)))

            lines_to_create=[]
            division_entera = int(float(supply_measure)//float(to_produce_measure))
            if division_entera == 0:
                division_entera += 1
            for cut_index in range(0, production.to_cut):
                extra_lines = []
                for i in range(division_entera):
                    print("In cut index LINEE")
                    print("Print #"+str(i))
                    extra_lines.append((0,0,{
                        'pos':i,
                        'medida':float(supply_measure)/float(to_produce_measure),
                        'medir_en':'cms',
                        'kilos':20,
                        'destino':'cliente'
                    }))

                print("Modulo 1: "+str(float(supply_measure)%float(to_produce_measure)))
                print("Modulo 2: "+str(float(to_produce_measure)%float(supply_measure)))
                extra_lines.append((0,0,{
                        'pos':float(to_produce_measure)//float(supply_measure) +1,
                        'medida':str(float(to_produce_measure)%float(supply_measure)),
                        'medir_en':'cms',
                        'kilos':20,
                        'destino':'desperdicio'
                }))
                lines_to_create.append((0,0,{
                    'production_id': production.id,
                    'num': cut_index +1,
                    'centro': 10,  # Assuming you want to keep the same centro
                    'diametro': 5,  # Same measure for each cut
                    #'destino': 'Some destination',  # You can assign a destination here
                    'lines':extra_lines
                }))
            production.write({'cut_line_ids': lines_to_create})
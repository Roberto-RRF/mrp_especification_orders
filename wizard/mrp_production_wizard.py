from odoo import models, fields, api
from odoo.exceptions import UserError

class MrpProductionWizard(models.TransientModel):
    _name = 'mrp.production.wizard'
    _description = 'Wizard for Printing Work Sheet'

    to_cut = fields.Integer("Numero de Pasadas")
    to_cut_rolls = fields.Integer("Rollos a Cortar")
    sale_type = fields.Char("Tipo de Venta")
    centro = fields.Char("Centro")
    diametro = fields.Char("Diametro")
    refil = fields.Float("Refil")


    production_id = fields.Many2one('mrp.production', string='Orden de Producción')
    resultant_products_ids = fields.Many2many('product.product', string="Resultant Products", readonly=True)
    source_product_id = fields.Many2one('product.product', string='Source Product')
    production_line_ids = fields.One2many('mrp.production.line', 'wizard_id', string="Production Lines")
    is_roll = fields.Boolean("Es Rollo")

    # Variables de Hoja
    millares_vendidos = fields.Char("Millares Vendidos")
    medida = fields.Char("Medida (cms)")
    kilos = fields.Char("Kilos")
    destino = fields.Char("Destino")
    empacar_en = fields.Char("Empacar a")
    hojas_por_empaque = fields.Char("Empaque / Separador")
    tarimas = fields.Char("Tarimas")

    @api.model
    def default_get(self, fields):
        # Initialize defaults by calling the parent method
        defaults = super(MrpProductionWizard, self).default_get(fields)

        # Fetch the `to_cut` value to determine the number of production lines
        to_cut = defaults.get('to_cut', 0)

        context = self.env.context

        centro = context.get('default_centro', '')
        diametro = context.get('default_diametro', '')
        peso_promedio = float(context.get('peso_promedio', ''))

        source_size = float(context.get('source_size', ''))
        resultant_sizes = context.get('resultant_sizes', '')

        if isinstance(resultant_sizes, list):
            try:
                resultant_sizes = [float(size) for size in resultant_sizes]
            except ValueError as e:
                raise ValueError(f"Error converting resultant_sizes to floats: {e}")
        else:
            raise TypeError("resultant_sizes is not a list.")



        # Prepare the production lines
        print("To cut: "+str(to_cut))
        print("Resultant Sizes: "+str(resultant_sizes[0]))
        print("Peso Promedio: "+str(peso_promedio))
        peso = round(peso_promedio/(to_cut*resultant_sizes[0]),2)
        production_lines = []
        for i in range(to_cut):
            # Create the base production line
            production_line = {
                'pasada': i + 1,
                'centro': centro,  
                'diametro': diametro,
                'wizard_id': self.id,  
            }
            # Prepare the detail lines for the production line
            line_details = []
            sum = 0
            i = 0
            char_pos = 65
            for i, size in enumerate(resultant_sizes):
                div = int(source_size // size)
                for j in range(0,div):
                    detail = {
                        'pos': chr(char_pos + j),
                        'medida': f'{sum} - {size + sum}',
                        'diferencia': f'{size}',
                        'medir_en': 'cm',
                        'kilos': peso,
                        'destino': 'Cliente',
                    }
                    line_details.append((0, 0, detail))
                    sum += size
            if source_size != sum:
                detail = {
                    'pos': chr(char_pos + len(resultant_sizes)),
                    'medida': f'{sum} - {source_size}',
                    'diferencia': f'{source_size - sum}',
                    'medir_en': 'cm',
                    'kilos': peso,
                    'destino': 'Desperdicio',  # Generating Destino A, Destino B, etc.
                }
                line_details.append((0, 0, detail))
            # Add detail lines to the production line
            production_line['lines_details'] = line_details

            # Append the production line to the list
            production_lines.append((0, 0, production_line))

        # Set the production lines in the defaults
        defaults['production_line_ids'] = production_lines

        return defaults



    def action_confirm(self):
        detalles_tarima = ""
        for i in self.production_id.detalles_tarimas:
            detalles_tarima += i.name+", "
        
        data = {
            'lines':[], 
            'product_comment':self.production_id.product_comment,
            'state': self.production_id.state,
            'warehouse': self.production_id.location_src_id.complete_name,
            'to_cut_rolls': self.production_id.to_cut_rolls,
            'name': self.production_id.name,
            'date': self.production_id.date_start,
            'sale_type': self.sale_type,
            'tarimas':self.tarimas,
            'detalles_tarima': detalles_tarima,
            'to_cut': self.to_cut,
            'client_name':self.production_id.sale_order_client,
        }
        for move in self.production_id.move_raw_ids:
            if move.product_id.product_cosal in ('rollo', 'hoja'):
                data['supply'] = {
                    'family': move.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Familia").name,
                    'subfamily':move.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Subfamilia").name,
                    'type': move.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Tipo").name,
                    'color': move.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Color").name,
                    'weight':move.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Gramos").name,
                    'size': move.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Ancho cm").name,
                    'centro': move.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Centro").name,
                    'diametro': move.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Diametro").name,
                    'certificado': move.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Certificado").name,
                }
                break

        if self.production_id.workorder_ids:
            data['work'] = []
            for work in self.production_id.workorder_ids:
                data['work'].append({
                    'opetacion':work.name,
                    'centro_trabajo':work.workcenter_id.name,
                    'producto':work.product_id.display_name,
                })
            print("\n\n\n")
            print(data['work'])



        if self.is_roll:
            for cut_index in self.production_line_ids:
                cut_lines = []

                for cut_index_details in cut_index.lines_details:
                    cut_lines.append({
                        'pos':cut_index_details.pos,
                        'size': cut_index_details.medida,
                        'diff_size': cut_index_details.diferencia,
                        'measure_in':cut_index_details.medir_en,
                        'kilos':cut_index_details.kilos,
                        'destiny':cut_index_details.destino,
                    })
                data['lines'].append({
                    'num': cut_index.pasada,
                    'center': cut_index.centro, 
                    'diameter': cut_index.diametro,  
                    'cut_lines':cut_lines
                })

            return self.env.ref('mrp_especification_orders.action_worksheet_roll_report').report_action([], data=data)
        else:
        
            
            data['millares_vendidos']= self.millares_vendidos
            data['medida']= self.medida
            data['kilos']= self.kilos
            data['destino']= self.destino
            data['empacar_en']= self.empacar_en
            data['refil'] = self.refil
            data['hojas_por_empaque'] = self.hojas_por_empaque
            return self.env.ref('mrp_especification_orders.action_worksheet_sheet_report').report_action([], data=data)

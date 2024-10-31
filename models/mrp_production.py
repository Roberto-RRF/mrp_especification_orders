from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'


    to_cut = fields.Integer("Numero de Pasadas")
    to_cut_rolls = fields.Integer("Rollos a Cortar")
    sale_type = fields.Char("Tipo de Venta")

    def action_print_work_sheet(self):
        for production in self:
            data = {
                'lines':[], 
                'product_comment':production.product_comment,
                'state':production.state,
                'warehouse': production.location_src_id.complete_name,
                'to_cut_rolls': production.to_cut_rolls,
                'name': production.name,
                'date': production.date_start,
                'sale_type':production.sale_type,

            }
            for move in production.move_raw_ids:

                # Get supply attrs
                if move.product_id.product_cosal in ('rollo', 'hoja'):
                    data['supply'] = {
                        'family': move.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Familia").name,
                        'subfamily':move.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Subfamilia").name,
                        'type': move.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Tipo").name,
                        'color': move.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Color").name,
                        'weight':move.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Gramos").name,
                        'size': move.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Ancho cm").name
                    }
                    break

            # Get output attrs
            if self.product_id:
                data['output'] = {
                    'family': production.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Familia").name,
                    'subfamily':production.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Subfamilia").name,
                    'type': production.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Tipo").name,
                    'color': production.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Color").name,
                    'weight':production.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Gramos").name,
                    'size': production.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Ancho cm").name,
                    'diameter': production.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Diametro").name,
                    'center': production.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Centro").name,
                }
                
            for cut_index in range(0, self.to_cut):
                cut_lines = []
                sum_pas = 0
                sum = 0

                pos_ascii = 65
                while sum +(float(data['supply']['size'])%float(data['output']['size'])) < float(data['supply']['size']):
                    sum += float(data['output']['size'])
                    cut_lines.append({
                        'pos':chr(pos_ascii),
                        'size': str(sum_pas) + ' - ' + str(sum),
                        'diff_size': str(abs(sum_pas - sum)),
                        'measure_in':'cms',
                        'kilos':9999,
                        'destiny':'cliente',
                    })
                    sum_pas = sum
                    pos_ascii += 1
                cut_lines.append({
                    'pos':chr(pos_ascii),
                    'size': str(sum) + ' - ' + str(data['supply']['size']),
                    'diff_size': str(abs(sum - float(data['supply']['size']))),
                    'measure_in':'cms',
                    'kilos':9999,
                    'destiny':'merma',
                })
                data['lines'].append({
                    'num': cut_index +1,
                    'center': data['output']['center'], 
                    'diameter': data['output']['diameter'],  
                    'cut_lines':cut_lines
                })

            return self.env.ref('mrp_especification_orders.action_worksheet_roll_report').report_action([], data=data)


    # @api.depends('raw_material_production_id', 'move_raw_ids')
    # @api.constrains('raw_material_production_id', 'move_raw_ids')
    # def _compute_attr_lines(self):
    #     """Method to delete related attr lines and recalculate new ones."""
    #     for production in self:

    #         production.attr_line_ids.unlink()
    #         for move in production.move_raw_ids:


    #             if move.product_id.product_cosal in ('rollo', 'hoja'):
    #                 new_lines = []
    #                 if familia:
    #                     new_line = (0, 0, {
    #                         'production_id': production.id,
    #                         'familia': familia.name,
    #                         'subfamilia': subfamilia.name,
    #                         'tipo': tipo.name,
    #                         'color': color.name, 
    #                         'gramaje': gramaje.name,  
    #                         'medida': medida.name,

    #                     })
    #                     print(str(new_line))
    #                     new_lines.append(new_line)

    #                 production.write({'attr_line_ids': new_lines})
    #                 break
    
    # @api.constrains('to_cut')
    # @api.depends('to_cut')
    # def _compute_cut_ids(self):
    #     print("Calculando....")
    #     if not self.attr_line_ids:
    #         return
    #     for production in self:
    #         production.cut_line_ids.unlink()

    #         final_product = production.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Ancho cm").name
    #         centro = production.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Centro").name
    #         diametro = production.product_id.product_template_attribute_value_ids.filtered(lambda a: a.attribute_id.name == "Diametro").name
    #         supply_measure = production.attr_line_ids[0].medida



    #         for cut_index in range(0, production.to_cut):
    #             lines = []
    #             cut_lines = []
    #             sum_pas = 0
    #             sum = 0

    #             pos_ascii = 65
    #             while sum +(float(supply_measure)%float(final_product)) < float(supply_measure):
    #                 sum += float(final_product)
    #                 lines.append((0,0,{
    #                     'pos':chr(pos_ascii),
    #                     'medida': str(sum_pas) + ' - ' + str(sum),
    #                     'dif_medida': str(abs(sum_pas - sum)),
    #                     'medir_en':'cms',
    #                     'kilos':9999,
    #                     'destino':'cliente',
    #                 }))
    #                 sum_pas = sum
    #                 pos_ascii += 1
    #             lines.append((0,0,{
    #                 'pos':chr(pos_ascii),
    #                 'medida': str(sum) + ' - ' + str(supply_measure),
    #                 'dif_medida': str(abs(sum - float(supply_measure))),
    #                 'medir_en':'cms',
    #                 'kilos':9999,
    #                 'destino':'merma',
    #             }))


    #             cut_lines.append((0,0,{
    #                 'production_id': production.id,
    #                 'num': cut_index +1,
    #                 'centro': centro, 
    #                 'diametro': diametro,  
    #                 'lines':lines
    #             }))
    #             production.write({'cut_line_ids': cut_lines})
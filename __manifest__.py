{
    'name': 'MRP Especification Orders',
    'version': '1.0',
    'category': 'Manufacturing',
    'summary': 'Agrega una pestaña de especificación en las órdenes de manufactura y agrega las instrucciones de fabricación',
    'description': 'Este módulo agrega una nueva pestaña llamada "Especificación" en las órdenes de manufactura.',
    'depends': [
        'mrp',  # Dependencia del módulo base de manufactura
        'bias_custom_cosal'  # Agregar el módulo personalizado como dependencia
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_production_view.xml',
        'report/work_sheet_roll_report.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
}

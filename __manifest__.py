{
    'name': 'Simple Production',
    'version': '16.0.1.0.0',
    'summary': 'Simple Production',
    'sequence': -6,
    'installable': True,
    'application': True,

    'depends': ['base', 'product', 'mail', 'stock'],
    'data': ['security/ir.model.access.csv',
             'data/simple_production_location.xml',
             'views/simple_production_bom_views.xml',
             'views/simple_production_views.xml'
             ]

}

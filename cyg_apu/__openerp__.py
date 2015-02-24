# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today
#    CyG xxxx
#    @autor: Edison Guachamin <edison.guachamin@gmail.com>
#
##############################################################################
{
    "name": "Analisis de Precios Unitarios",
    "version": "1.0",
    "author": "CyG",
    "website": "http://www.cyg.ec",
    "category": "Construction",
    "sequence": 1,
    "complexity": "expert",
    "description": """
    Módulo para realizar el analisis de precios unitarios
    """,
    "shortdesc": "Precios Unitarios - CyG",
    "depends": [
        'cyg_inmobiliario',
        "mrp",
        "product",
        'account',
        ],
    "init_xml": [
                 'data/ir_sequence.xml',
                 'data/data.xml',
                 'data/data_capitulo.xml',
                 ],
    "demo_xml": [],
    "update_xml": [
        #'security/groups.xml',
        'views/cyg_base_view.xml',
        'views/product_view.xml',
        "wizard/add_product.xml",
        'views/cyg_apu_view.xml',
        'views/cyg_apu_line_view.xml',
        'views/menu_view.xml',
       
        ],
    "application": True,
    "auto_install": False,
}

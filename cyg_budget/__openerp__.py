# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today
#    CyG xxxx
#    @autor: Edison Guachamin <edison.guachamin@gmail.com>
#
##############################################################################
{
    "name": "Presupuestos",
    "version": "1.0",
    "author": "CyG",
    "website": "http://www.cyg.ec",
    "category": "Construction",
    "sequence": 1,
    "complexity": "expert",
    "description": """
    Módulo para realizar presupuestos en base al analisis de precios unitarios
    """,
    "shortdesc": "Presupuestos - CyG",
    "depends": [
        'cyg_inmobiliario',
        'cyg_apu',
        #'account_budget',
        ],
    "init_xml": [
                 'data/ir_sequence.xml',
                 'data/data.xml',
                 ],
    "demo_xml": [],
    "update_xml": [
        #'security/groups.xml',
        "wizard/add_apu.xml",
        'views/cyg_presupuesto_view.xml',
        #'views/cyg_apu_view.xml',
        #'views/cyg_apu_line_view.xml',
        #'views/menu_view.xml',
        #'views/cyg_apu.xml',
        ],
    "application": True,
    "auto_install": False,
}

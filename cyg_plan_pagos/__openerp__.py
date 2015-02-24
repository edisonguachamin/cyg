# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today
#    CyG xxxx
#    @autor: Edison Guachamin <edison.guachamin@gmail.com>
#    @date: 03-06-2014
#    @last_modified: 03-06-2014
#
##############################################################################
#import time
{
    "name": "CyG - Plan de pagos",
    "version": '14-01-2015',
    "author": "CyG",
    "website": "http://www.cyg.ec",
    "category": "Construction",
    "sequence": 1,
    "complexity": "expert",
    "description": """
    Módulo para gestión del plan de pagos
    """,
    "shortdesc": "Plan de Pagos - CyG",
    "depends": [
        "cyg_sale",
        'cyg_inmobiliario',
        ],
    "init_xml": [
                 'data/ir_sequence.xml',
                 'data/data.xml',
                 ],
    "demo_xml": [],
    "update_xml": [
        'security/groups.xml',
        'reportes/report_menu_view.xml',
        'view/cyg_base_view.xml',
        'view/plan_pagos_view.xml',
        'view/sale_order_view.xml',
        'view/cyg_payment_deposit_view.xml',
        'view/cyg_inmueble_cuota_view.xml',
        'view/cyg_payment_devolucion_view.xml',
        ],
    "application": True,
    "auto_install": False,
}

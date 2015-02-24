# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today
#    CyG xxxx
#    @autor: Jonathan Finlay <jfinlay@riseup.net>
#    @date: 03-06-2014
#    @last_modified: 03-06-2014
#
##############################################################################

{
    "name": "CyG - Inmobiliario",
    "version": '14-01-2015',
    "author": "CyG",
    "website": "http://www.cyg.ec",
    "category": "Construction",
    "sequence": 1,
    "complexity": "expert",
    "description": """
    Módulo de gestión de inmobiliarios para ERP de construcciones
    """,
    "shortdesc": "BASE - CyG",
    "depends": [
        'base',
        'cyg_base'
    ],
    "init_xml": ['data/data.xml',],
    "demo_xml": [],
    "update_xml": [
        'security/groups.xml',
        'wizard/genera_inventario_proyecto.xml',
        'wizard/cambio_precios.xml',
        'wizard/importar_actividades.xml',
        'wizard/import_actividades_inmueble.xml',
        'view/base_view.xml',
        'view/proyecto.xml',
        'view/lote.xml',
        'view/transferencia_domino.xml',
        'view/res_partner_menu.xml',
        ],
    "application": True,
    "auto_install": False,
}

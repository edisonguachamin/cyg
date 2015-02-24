# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today Project opene
#    CyG xxxx
#    @autor: Edison Guachamin <edison.guachamin@gmail.com>
#
##############################################################################
{
    "name": "CYG-Project",
    "version": "1.0",
    "author": "CyG",
    "website": "http://www.cyg.ec",
    "category": "Sales",
    "sequence": 1,
    "complexity": "expert",
    "description": """
    Módulo de Seguimientos de Proyectos
    """,
    "shortdesc": "Project - CyG",
    "depends": [
        'base',
        'base_ec_dpa',
        'base_ec_ruc',
        'web_m2x_options',
        #'cyg_security',
        ],
    "init_xml": [
                 'security/ir.model.access.csv',
                 'data/ir_sequence.xml',
                 'data/data.xml',
                 ],
    "demo_xml": [],
    "update_xml": [
        'security/groups.xml',
        'views/cyg_base_view.xml',
        'views/cyg_project_hallazgos_view.xml',
        'views/cyg_project_charter_view.xml',
        'views/menu_view.xml',
        ],
    "application": True,
    "auto_install": False,
}

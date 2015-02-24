# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today
#    CyG xxxx
#    @autor: Edison Guachamin <edison.guachamin@gmail.com>
#
##############################################################################
{
    "name": "CYG-Report",
    "version": "1.0",
    "author": "CyG",
    "website": "http://www.cyg.ec",
    "category": "Sales",
    "sequence": 1,
    "complexity": "expert",
    "description": """
    Link de Reportes
    """,
    "shortdesc": "Reportes - CyG",
    "depends": [
        'base',
        'board',
        ],
    "init_xml": [
                 'security/ir.model.access.csv',
                 #'data/data.xml',
                 ],
    "demo_xml": [],
    "update_xml": [
        #'security/groups.xml',
        'views/base_view.xml',
        #'views/cyg_project_hallazgos_view.xml',
        'wizard/cyg_ftp_view.xml',
        'views/menu_view.xml',
        
        ],
    "application": True,
    "auto_install": False,
}

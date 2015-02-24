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
    "name": "CyG - Base",
    "version": "1.0",
    "author": "CyG",
    "website": "http://www.cyg.ec",
    "category": "Construction",
    "sequence": 1,
    "complexity": "expert",
    "description": """
    Módulo con los catálogos y modelos básicos para el
    ERP de construcciones
    """,
    "shortdesc": "BASE - CyG",
    "depends": [
        'base',
        'base_ec_dpa',
        'base_ec_ruc'
        ],
    "init_xml": [],
    "demo_xml": [],
    "update_xml": [
        'security/groups.xml',
        'view/ir_attachment.xml',
        'view/base.xml',
        'view/res_bank.xml',
        'view/res_partner.xml',
        'view/res_users.xml',
        ],
    "application": True,
    "auto_install": False,
}

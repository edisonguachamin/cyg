# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today Jonathan Finlay <jfinlay@riseup.net>.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "CYG - Seguridad",
    "version": '14-01-2015',
    "description": """Modulo de seguridad
    """,
    "shortdesc": "CYG - Seguridad",
    "author": "CyG",
    "website": "http://www.cyg.ec",
    "category": "Construction",
    "sequence": 1,
    "complexity": "easy",
    "depends": [
        'cyg_base',
        'cyg_inmobiliario',
        'cyg_plan_pagos',
        'cyg_sale',
    ],
    "data": [
        #'security/groups.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml'
    ],
    "init_xml": [],
    "demo_xml": [],
    "update_xml": [],
    "active": False,
    "installable": True,
    "certificate": "",
}

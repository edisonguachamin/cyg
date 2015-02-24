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
    "name": "CYG - Cotización",
    "version": '14-01-2015',
    "description": """Modulo de Preventa
    """,
    "shortdesc": "CYG - Cotización",
    "author": "CyG",
    "website": "http://www.cyg.ec",
    "category": "Sales Management",
    "sequence": 1,
    "complexity": "easy",
    "depends": [
        'sale',
        'sale_stock',
        'cyg_inmobiliario',
        
    ],
    "init_xml": [
                 'data/ir_sequence.xml',
                 'data/data.xml',
                 ],
    "demo_xml": [],
    "update_xml": [
        'security/groups.xml',
        'view/base.xml',
        'reportes/report_menu_view.xml',
        #'data/delete_objects.xml',
        'view/sale_order_view.xml',
        'view/cyg_inmueble_cuota_view.xml',
        'view/cyg_seguimiento_view.xml',
        'view/cyg_comisiones_view.xml',
    ],
    "active": False,
    "installable": True,
    "certificate": "",
}

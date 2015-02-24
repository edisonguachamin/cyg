# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
from report import report_sxw
from osv import osv
import pooler
import tools

__author__ = 'Edison Guachamin'
##Manejo de Fechas
from datetime import datetime
from dateutil import tz

class cyg_statement(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(cyg_statement, self).__init__(cr, uid, name, context=context)
        #print 'context', context
        self.localcontext.update({
            'time': time,
            'total_pagos':self.total_pagos
        })
        self.context = context
        self.valor = 0.00
        
    def total_pagos(self, pagos):
        total = 0.00
        for item in pagos:
            total += item.amount
        return total

report_sxw.report_sxw('report.cyg_statement','sale.order',
                      'addons/cyg_plan_pagos/reportes/report_statement.rml',parser=cyg_statement,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

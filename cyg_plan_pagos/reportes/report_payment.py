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

class cyg_payment(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(cyg_payment, self).__init__(cr, uid, name, context=context)
        #print 'context', context
        self.localcontext.update({
            'time': time,
        })
        self.context = context
        self.valor = 0.00

report_sxw.report_sxw('report.cyg_payment','cyg.payment',
                      'addons/cyg_plan_pagos/reportes/report_payment.rml',parser=cyg_payment,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

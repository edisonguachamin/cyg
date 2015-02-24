# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today
#    CyG xxxx
#    @autor: Edison Guachamin <edison.guachamin@gmail.com>
#
##############################################################################
import datetime

from openerp.osv import fields, osv
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp

def strToDate(dt):
        dt_date=datetime.date(int(dt[0:4]),int(dt[5:7]),int(dt[8:10]))
        return dt_date
    


# class cyg_budget_proyecto_capitulo(osv.osv):
#     _name = 'cyg.budget.proyecto.capitulo' 
#     _columns = {
#                 'name':fields.char('Capitulo', size=5000),
#                 'sequence':fields.integer('Orden'),
#                 
#                }
# cyg_budget_proyecto_capitulo()


# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today
#    CyG xxxx
#    @autor: Edison Guachamin <edison.guachamin@gmail.com>
#
##############################################################################

import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import time

import openerp
from openerp import SUPERUSER_ID
from openerp import pooler, tools
from openerp.osv import fields, osv, expression
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round

import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)
from utils import cambiarTildes

class cyg_report_ftp(osv.osv):
    _name= 'cyg.report.ftp'
    _description = 'Tabla de Administracion'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    
    _columns = {
                'name':fields.char('Url', size=500, help="Por ejemplo ftp://localhost:8021"),
                'modulo_id':fields.many2one('ir.module.module','Modulo'),
                'nombre':fields.char('Nombre del Modulo'),
                'company_id':fields.many2one('res.company','Cliente'),
                'active':fields.boolean('Predeterminado'),
                }
cyg_report_ftp()

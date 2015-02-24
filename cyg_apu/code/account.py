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

class account_account(osv.osv):
    _inherit = 'account.account' 
    #Do not touch _name it must be same as _inherit
    #_name = 'openerpmodel'
    _columns = {
                'mayor_auxiliar':fields.selection([
                    ('mayor','Mayor'),
                    ('auxiliar','Auxiliar'),
                     ],'Mayor / Auxiliar', select=True, readonly=True),
                'codigo_fid':fields.char('Codigo FID', size=100),
                'descripcion_fid':fields.char('Descripcion FID', size=500),
                
               }
account_account()

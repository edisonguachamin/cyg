# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today
#    CyG xxxx
#    @autor: Edison Guachamin <edison.guachamin@gmail.com>
#
##############################################################################
import math
import re

from _common import ceiling

from openerp import tools, SUPERUSER_ID
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import datetime
import openerp.addons.decimal_precision as dp
from openerp.tools import float_round
from utils import cambiarTildes

class cyg_jornada(osv.osv):
    _name = 'cyg.jornada'
    
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    
    _columns = {
                'name':fields.char('Jornada',size=100),
                'hora':fields.integer('H/D'),
                }
    _sql_constraints = [     ('name_uniq', 'unique (name)', 'Ya existe creada una jornada con ese nombre !'),      ]
cyg_jornada()

class cyg_apu_capitulo(osv.osv):
    _name = 'cyg.apu.capitulo'
    
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        name = ''
        for line in self.browse(cr, uid, ids, context=context):
            name = line.name or '/'
            if line.code:
                name ='['+ line.code + '] ' + name
            res.append((line.id, name))
            
        return res
    _columns = {
                'name':fields.char('Capitulo', size=5000),
                'code':fields.char('Code', size=10),
                'sequence':fields.integer('Orden'),
               }
    _defaults = {  
        'sequence': 1,  
        }
    _sql_constraints = [('name_uniq', 'unique (code)', 'El codigo debe ser unico !') ]
cyg_apu_capitulo()
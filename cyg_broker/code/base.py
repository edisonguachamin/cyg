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
class cyg_broker_ramo(osv.osv):
    _name= 'cyg.broker.ramo'
    _description = 'Ramo Broker'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Ramo', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_broker_ramo()

class cyg_broker_grupo_cobertura_adicional(osv.osv):
    _name= 'cyg.broker.grupo.cobertura.adicional'
    _description = 'Grupo Adicional Broker'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    
    _columns = {
                'name':fields.char('Grupo', required=True, size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_broker_grupo_cobertura_adicional()

class cyg_broker_grupo_amparo_adicional(osv.osv):
    _name= 'cyg.broker.grupo.amparo.adicional'
    _description = 'Grupo Amparo Adicional Broker'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    
    _columns = {
                'name':fields.char('Grupo', required=True, size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_broker_grupo_amparo_adicional()

class cyg_broker_tipo(osv.osv):
    _name= 'cyg.broker.tipo'
    _description = 'Tipo Broker'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    
    def _default_ramo(self, cr, uid, context=None):
        print '_default_ramo', context
        if context is None:
            context = {}
        if 'ramo_id' in context and context['ramo_id']:
            return context['ramo_id']
        
    _columns = {
                'name':fields.char('Tipo', size=500),
                'code':fields.char('Código', size=500),
                'ramo_id':fields.many2one('cyg.broker.ramo','Ramo'),
                'descripcion':fields.text('Descripción'),
                
                }
    _defaults = {  
        'ramo_id': _default_ramo
        }
cyg_broker_tipo()

class cyg_broker_uso(osv.osv):
    _name= 'cyg.broker.uso'
    _description = 'Uso Broker'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Uso', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_broker_uso()
class cyg_broker_definiciones(osv.osv):
    _name= 'cyg.broker.definiciones'
    _description = 'Uso Broker'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Definición', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_broker_definiciones()
class cyg_broker_cobertura(osv.osv):
    _name= 'cyg.broker.cobertura'
    _description = 'Cobertura Broker'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Cobertura', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_broker_cobertura()

class cyg_broker_cobertura_adicional(osv.osv):
    _name= 'cyg.broker.cobertura.adicional'
    _description = 'Cobertura Adicional Broker'
    
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    
    def onchange_grupo(self, cr, uid, ids, field):
        res  = {'value':{}}
        grupo_obj = self.pool.get('cyg.broker.grupo.cobertura.adicional')
        if field:
            grupo_info = grupo_obj.browse(cr,uid,field)
            res['value']['name']=grupo_info.name
        return res
    
    def name_get(self,cr,uid,ids, context=None):
        if not context:
            context = {}
        res = []
        for r in self.read(cr,uid,ids,['descripcion'], context):
            name = r['descripcion']
            res.append((r['id'], name))
        return res

    _columns = {
                'name':fields.char('Cobertura', size=500),
                #'grupo_id':fields.many2one('cyg.broker.ramo','Grupo'),
                'grupo_adicional_id':fields.many2one('cyg.broker.grupo.cobertura.adicional','Grupo'),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_broker_cobertura_adicional()

class cyg_broker_amparo_adicional(osv.osv):
    _name= 'cyg.broker.amparo.adicional'
    _description = 'Cobertura Adicional Broker'
    
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    
    def onchange_grupo(self, cr, uid, ids, field):
        res  = {'value':{}}
        grupo_obj = self.pool.get('cyg.broker.grupo.amparo.adicional')
        if field:
            grupo_info = grupo_obj.browse(cr,uid,field)
            res['value']['name']=grupo_info.name
        return res
    
    def name_get(self,cr,uid,ids, context=None):
        if not context:
            context = {}
        res = []
        for r in self.read(cr,uid,ids,['descripcion'], context):
            name = r['descripcion']
            res.append((r['id'], name))
        return res
    
    _columns = {
                'name':fields.char('Amparo', size=500),
                #'grupo_id':fields.many2one('cyg.broker.ramo','Grupo'),
                'grupo_adicional_id':fields.many2one('cyg.broker.grupo.amparo.adicional','Grupo'),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_broker_amparo_adicional()


class cyg_broker_clausula(osv.osv):
    _name= 'cyg.broker.clausula'
    _description = 'Cláusula Broker'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Cláusula', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_broker_clausula()

class cyg_broker_exclusiones(osv.osv):
    _name= 'cyg.broker.exclusiones'
    _description = 'Uso Broker'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Exclusiones', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_broker_exclusiones()


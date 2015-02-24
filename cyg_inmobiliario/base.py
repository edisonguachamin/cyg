# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today
#    CyG xxxx
#    @author: Edison Guachamin <edison.guachamin@gmail.com>
#    @date: 03-06-2014
#    @last_modified: 03-06-2014
#
##############################################################################
from openerp.osv import fields, osv
import time
from utils import cambiarTildes

class cyg_tasa_interes(osv.Model):
    #_name = 'sale.order'
    _name = 'cyg.tasa.interes'
    
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    
    def onchange_anio(self, cr, uid, ids,field_name):
        res = {'value':{}}
        if field_name < 0:
            return {'value':{'anio':0},
                    'warning':{'title': "Error", "message": "El año debe ser mayor de cero"}}
        
    _columns = {
                'name':fields.char('Nombre', size=100),
                #'proyecto_id':fields.many2one('cyg.proyecto','Proyecto'),
                'tasa':fields.float('Valor de Tasa de Interes', help="Escriba el porcentaje de la tasa. Ejemplo: 10% pongale 0.10 es decir 10/100"),
                'anio':fields.integer('Año')
                }
    
    
    _defaults = {  
        'anio': lambda *a: time.strftime('%Y'),
        'name':'Tasa de Interes Anual 2014'
        }
    
    _sql_constraints = [('anio_uniq', 'unique (tasa,anio)', 'No se permite el mismo valor de tasa de interes por anio !'),      ]
cyg_tasa_interes()

class cyg_type_presupuesto(osv.Model):
    #_name = 'sale.order'
    _name = 'cyg.type.presupuesto'
    
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    
    _columns = {
                'name':fields.char('Nombre', size=100),
                'code':fields.char('Code',size=100),
                }
    _defaults = {  
        }
    
    _sql_constraints = [('name_uniq', 'unique (name)', 'Ya existe ese tipo de presupuesto !'),      ]
cyg_type_presupuesto()
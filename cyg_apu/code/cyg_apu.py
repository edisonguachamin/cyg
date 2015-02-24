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


class cyg_base_apu(osv.osv):
    _name = 'cyg.base.apu'
    _description= 'Base General de APU'
    
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    
    def create(self, cr, uid, vals, context={}):
        if vals.get('code','/')=='/':
            vals['code'] = self.pool.get('ir.sequence').get(cr, uid, 'cyg.base.apu') or '/'
        res_id = super(cyg_base_apu, self).create(cr, uid, vals, context)
        return res_id 
    
    _columns = {
                'code':fields.char('Code',size=100),
                'name':fields.char('Nombre',size=900),
                'note':fields.text('Descripcion'),
                'cyg_apu_ids':fields.one2many('cyg.apu','cyg_base_id','APU'),
                }
    _defaults = {  
        'code': lambda obj, cr, uid, context: '/',  
        }
    _sql_constraints = [('name_uniq', 'unique (name)', 'Existe una base con el mismo nombre !'),      ]
    
cyg_base_apu


class cyg_apu(osv.osv):
    _name = "cyg.apu"
    _description = "Analisis de Precios Unitarios"
    
    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        cur_obj = self.pool.get('res.currency')
        for apu in self.browse(cr, uid, ids, context=context):
            nro_decimal = 10 ** -apu.nro_decimal
            #print 'nro_decimal', nro_decimal
            res[apu.id] = {
                'amount_equipo': 0.0,
                'porcentage_equipo':0.0,
                'amount_material': 0.0,
                'amount_transporte': 0.0,
                'amount_obra': 0.0,
                
                'amount_equipo2': 0.0,
                'amount_material2': 0.0,
                'amount_transporte2': 0.0,
                'amount_obra2': 0.0,
                
                'amount_otros':0.00,
                'amount_otros2':0.00

            }
            #float_round(amount, precision_rounding=currency.rounding)
            cur = 7
            #Escenario 1
            for line in apu.equipo_ids:
                res[apu.id]['amount_equipo'] += float_round(line.qty * line.price * line.rendimiento,precision_rounding=nro_decimal)
            for line in apu.materiales_ids:
                res[apu.id]['amount_material'] += float_round(line.qty * line.price,precision_rounding=nro_decimal)
            for line in apu.transporte_ids:
                res[apu.id]['amount_transporte'] += float_round(line.qty * line.price,precision_rounding=nro_decimal)
            for line in apu.mano_obra_ids:
                res[apu.id]['amount_obra'] += float_round(line.qty * line.price * line.rendimiento,precision_rounding=nro_decimal)
            for line in apu.otros_ids:
                res[apu.id]['amount_otros'] += float_round(line.qty * line.price,precision_rounding=nro_decimal)
            #res[apu.id]['amount_total']= res[apu.id]['amount_equipo'] + res[apu.id]['amount_material'] +res[apu.id]['amount_transporte']+res[apu.id]['amount_obra']
            #Escenario 2
            for line in apu.equipo2_ids:
                res[apu.id]['amount_equipo2'] += float_round(line.qty * line.price *line.rendimiento ,precision_rounding=nro_decimal)
            for line in apu.materiales2_ids:
                res[apu.id]['amount_material2'] += float_round(line.qty * line.price,precision_rounding=nro_decimal) 
            for line in apu.transporte2_ids:
                res[apu.id]['amount_transporte2'] += float_round(line.qty * line.price,precision_rounding=nro_decimal)
            for line in apu.mano_obra2_ids:
                res[apu.id]['amount_obra2'] += float_round(line.qty * line.price *line.rendimiento,precision_rounding=nro_decimal)
            for line in apu.otros2_ids:
                res[apu.id]['amount_otros2'] += float_round(line.qty * line.price,precision_rounding=nro_decimal)
              
            #print 'ampount_all', res
        return res
    #Escenario 1
    def _get_equipo_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('cyg.apu.line').browse(cr, uid, ids, context=context):
            result[line.equipo_id.id] = True
        return result.keys()
    
    def _get_material_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('cyg.apu.line').browse(cr, uid, ids, context=context):
            result[line.material_id.id] = True
        return result.keys()
    
    def _get_transporte_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('cyg.apu.line').browse(cr, uid, ids, context=context):
            result[line.transporte_id.id] = True
        return result.keys()

    def _get_obra_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('cyg.apu.line').browse(cr, uid, ids, context=context):
            result[line.mano_id.id] = True
        return result.keys()
    
    #Escenario 2
    def _get_equipo2_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('cyg.apu.line').browse(cr, uid, ids, context=context):
            result[line.equipo2_id.id] = True
        return result.keys()
    
    def _get_material2_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('cyg.apu.line').browse(cr, uid, ids, context=context):
            result[line.material2_id.id] = True
        return result.keys()
    
    def _get_transporte2_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('cyg.apu.line').browse(cr, uid, ids, context=context):
            result[line.transporte2_id.id] = True
        return result.keys()

    def _get_obra2_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('cyg.apu.line').browse(cr, uid, ids, context=context):
            result[line.mano2_id.id] = True
        return result.keys()
    
    def button_validar(self, cr, uid, ids,context=None):
        return self.write(cr, uid, ids, {'state':'done'})
    
    def button_to_draft(self, cr, uid, ids,context=None):
        return self.write(cr, uid, ids, {'state':'draft'})
    
    def button_dummy(self, cr, uid, ids, context=None):
#         total_equipo=total_material= total_transporte=total_obra=0.00
#         for apu in self.browse(cr, uid,ids,context=context):
#             nro_decimal = 10 ** -apu.nro_decimal
#             print 'button_dummy', nro_decimal
#             for line in apu.equipo_ids:
#                 total_equipo += float_round(line.qty * line.price * line.rendimiento,precision_rounding=nro_decimal)
#             for line in apu.materiales_ids:
#                 total_material += float_round(line.qty * line.price,precision_rounding=nro_decimal)
#             for line in apu.transporte_ids:
#                 total_transporte += float_round(line.qty * line.price,precision_rounding=nro_decimal)
#             for line in apu.mano_obra_ids:
#                 total_obra += float_round(line.qty * line.price * line.rendimiento,precision_rounding=nro_decimal)
#             #res[apu.id]['amount_total']= res[apu.id]['amount_equipo'] + res[apu.id]['amount_material'] +res[apu.id]['amount_transporte']+res[apu.id]['amount_obra']
#             #Escenario 2
# #             for line in apu.equipo2_ids:
# #                 total += float_round(line.qty * line.price *line.rendimiento ,precision_rounding=nro_decimal)
# #             for line in apu.materiales2_ids:
# #                 res[apu.id]['amount_material2'] += float_round(line.qty * line.price,precision_rounding=nro_decimal) 
# #             for line in apu.transporte2_ids:
# #                 res[apu.id]['amount_transporte2'] += float_round(line.qty * line.price,precision_rounding=nro_decimal)
# #             for line in apu.mano_obra2_ids:
# #                 res[apu.id]['amount_obra2'] += float_round(line.qty * line.price *line.rendimiento,precision_rounding=nro_decimal)
#         self.write(cr, uid, ids,{'amount_equipo':total_equipo,'amount_material':total_material,'amount_transporte':total_transporte,'amount_obra':total_obra})
        return True
    
    def _total(self, cursor, user, ids, name, args, context=None):
        if not ids:
            return {}
        res ={}
        total = 0.00
        porcentage_equipo = 0.00
        for apu in self.browse(cursor, user, ids, context=context):
            res[apu.id] = {
                'amount_total': 0.0,
                
                'porcentage_equipo':0.0,
                'porcentage_material':0.0,
                'porcentage_mano':0.0,
                'porcentage_transporte':0.0,
                'porcentage_otros':0.0,

            }
            
            total += apu.amount_equipo
            total += apu.amount_material
            total += apu.amount_transporte
            total += apu.amount_obra
            total += apu.amount_otros
#             if apu.equipo_ids:
#                 amount_equipo = reduce(lambda x, y: x + y.price * y.qty * y.rendimiento, apu.equipo_ids, 0.0)
#                 total += amount_equipo 
#                 
#             if apu.equipo_ids:
#                 amount_equipo = reduce(lambda x, y: x + y.price * y.qty, apu.equipo_ids, 0.0)
#                 total += amount_equipo 
#                 
#             if apu.mano_obra_ids:
#                 amount_equipo = reduce(lambda x, y: x + y.price * y.qty * y.rendimiento, apu.mano_obra_ids, 0.0)
#                 total += amount_equipo
#                 
#             if apu.materiales_ids:
#                 amount_material = reduce(lambda x, y: x + y.price * y.qty, apu.materiales_ids, 0.0)
#                 total += amount_material
            res[apu.id]['amount_total'] = total
            if total:
                res[apu.id]['porcentage_equipo'] = round((apu.amount_equipo * 100) / total,2)
                res[apu.id]['porcentage_material'] = round((apu.amount_material * 100) / total,2)
                res[apu.id]['porcentage_mano'] = round((apu.amount_transporte * 100) / total,2)
                res[apu.id]['porcentage_transporte'] = round((apu.amount_obra * 100) / total,2)
                res[apu.id]['porcentage_otros'] = round((apu.amount_otros * 100) / total,2)
        return res
    
    def _total2(self, cursor, user, ids, name, args, context=None):
        if not ids:
            return {}
        res = {}
        total = 0.00
        for apu in self.browse(cursor, user, ids, context=context):
            res[apu.id] = {
                'amount_total2': 0.0,
                'porcentage_equipo2':0.0,
                'porcentage_material2':0.0,
                'porcentage_mano2':0.0,
                'porcentage_transporte2':0.0,
                'porcentage_otros2':0.0,

            }
            
            total += apu.amount_equipo2
            total += apu.amount_material2
            total += apu.amount_transporte2
            total += apu.amount_obra2
            total += apu.amount_otros2
#             if apu.equipo_ids:
#                 amount_equipo = reduce(lambda x, y: x + y.price * y.qty * y.rendimiento, apu.equipo_ids, 0.0)
#                 total += amount_equipo 
#                 
#             if apu.equipo_ids:
#                 amount_equipo = reduce(lambda x, y: x + y.price * y.qty, apu.equipo_ids, 0.0)
#                 total += amount_equipo 
#                 
#             if apu.mano_obra_ids:
#                 amount_equipo = reduce(lambda x, y: x + y.price * y.qty * y.rendimiento, apu.mano_obra_ids, 0.0)
#                 total += amount_equipo
#                 
#             if apu.materiales_ids:
#                 amount_material = reduce(lambda x, y: x + y.price * y.qty, apu.materiales_ids, 0.0)
#                 total += amount_material
            #res[apu.id] = total
            res[apu.id]['amount_total2'] = total
            if total:
                res[apu.id]['porcentage_equipo2'] = round((apu.amount_equipo2 * 100) / total,2)
                res[apu.id]['porcentage_material2'] = round((apu.amount_material2 * 100) / total,2)
                res[apu.id]['porcentage_mano2'] = round((apu.amount_transporte2 * 100) / total,2)
                res[apu.id]['porcentage_transporte2'] = round((apu.amount_obra2 * 100) / total,2)
                res[apu.id]['porcentage_otros2'] = round((apu.amount_otros2 * 100) / total,2)
            
        return res


    def create(self, cr, uid, vals, context={}):
        #print 'context create',context
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cyg.apu') or '/'
            
        res_id = super(cyg_apu, self).create(cr, uid, vals, context)
        return res_id

    def on_change_nro_decimales(self, cr, uid, ids, field_name):
        res = {}
        if field_name < 0:
            return {'value':{'nro_decimal':2},
                    'warning':{'title': "Error", "message": "Nro debe ser mayor de 0"}}
        return {'value':res}
    
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
            name = line.rubro or '/'
            # optional prefixes
            #===================================================================
            # if line.product_id.code:
            #     name = line.product_id.code + ': ' + name
            # if line.picking_id.origin:
            #     name = line.picking_id.origin + '/ ' + name
            res.append((line.id, name))
            
        return res
    
    _columns = {
        'name': fields.char('Ref.', size=64, required=True),
        'code':fields.char('Codigo', size=100),
        'cyg_base_id':fields.many2one('cyg.base.apu','Base Apu'),
        'jornada_id':fields.many2one('cyg.jornada','Jornada'),
        'proyecto_id':fields.many2one('cyg.proyecto','Proyecto'),
        'etapa_id':fields.many2one('cyg.proyecto_etapa','Etapa'),
        'rubro':fields.char('Rubro', size=1000),
        
        'uom_id':fields.many2one('product.uom','Unidad'),
        'nro_decimal':fields.integer('Nro Decimales'),
        'date':fields.date('Fecha'),
        'nro_decimales':fields.integer('Nro de Decimales', help="Nro de decimales para realizar el calculo de los precios unitarios"),
        'note': fields.text('Descripcion'),
        #'capitulo_id':fields.many2one('cyg.apu.capitulo','Capitulo'),
        
        
        #'escenario_ids': fields.one2many('cyg.apu.escenario', 'apu_id', 'Escenarios'),
        #'escenario_dos_ids': fields.one2many('cyg.apu.escenario', 'apu_id2', 'Escenarios'),
        #Escenario Uno
        'equipo_ids':fields.one2many('cyg.apu.line','equipo_id','Equipo y Herramienta'),
        'amount_equipo': fields.function(_amount_all, string="Total", digits=(16,4),type='float',store=False,multi='all'),
        'porcentage_equipo':fields.function(_total, string="%", digits=(16,2),type='float',store=False,multi='escenario1'),
#         'amount_equipo': fields.function(_amount_all,string='Subtotal Equipo',digits=(16,4),
#             store={
#                 'cyg.apu': (lambda self, cr, uid, ids, c={}: ids, ['equipo_ids'], 20),
#                 'cyg.apu.line': (_get_equipo_line, ['price','qty','rendimiento','equipo_id'], 20),
#             },
#             multi='all'),
                
        'materiales_ids':fields.one2many('cyg.apu.line','material_id','Materiales'),
        'amount_material': fields.function(_amount_all, string="Total", digits=(16,4),type='float',store=False,multi='all'),
        'porcentage_material':fields.function(_total, string="%", digits=(16,2),type='float',store=False,multi='escenario1'),
#         'amount_material': fields.function(_amount_all, string='Subtotal Material', digits=(16,4),
#             store={
#                 'cyg.apu': (lambda self, cr, uid, ids, c={}: ids, ['equipo_ids'], 20),
#                 'cyg.apu.line': (_get_material_line, ['price','qty','rendimiento','material_id'], 20),
#             },
#             multi='all'),
        'transporte_ids':fields.one2many('cyg.apu.line','transporte_id','Transporte'),
        'amount_transporte': fields.function(_amount_all, string="Total", digits=(16,4),type='float',store=False,multi='all'),
        'porcentage_transporte':fields.function(_total, string="%", digits=(16,2),type='float',store=False,multi='escenario1'),
#         'amount_transporte': fields.function(_amount_all, string='Subtotal Transporte',digits=(16,4), 
#             store={
#                 'cyg.apu': (lambda self, cr, uid, ids, c={}: ids, ['transporte_ids'], 20),
#                 'cyg.apu.line': (_get_transporte_line, ['price','qty','rendimiento','transporte_id'], 20),
#             },
#             multi='all'),
        'mano_obra_ids':fields.one2many('cyg.apu.line','mano_id','Mano de Obra'),
        'amount_obra': fields.function(_amount_all, string="Total", digits=(16,4),type='float',store=False,multi='all'),
        'porcentage_mano':fields.function(_total, string="%", digits=(16,2),type='float',store=False,multi='escenario1'),
#         'amount_obra': fields.function(_amount_all, string='Subtotal Mano Obra', digits=(16,4),
#             store={
#                 'cyg.apu': (lambda self, cr, uid, ids, c={}: ids, ['mano_obra_ids'], 20),
#                 'cyg.apu.line': (_get_obra_line, ['price','qty','rendimiento','mano_id'], 20),
#             },
#             multi='all'),
        'otros_ids':fields.one2many('cyg.apu.line','otro_id','Otros'),
        'amount_otros': fields.function(_amount_all, string="Total", digits=(16,4),type='float',store=False,multi='all'),
        'porcentage_otros':fields.function(_total, string="%", digits=(16,2),type='float',store=False,multi='escenario1'),
        #Escenario 2
        'equipo2_ids':fields.one2many('cyg.apu.line','equipo2_id','Equipo y Herramienta'),
        'amount_equipo2': fields.function(_amount_all, string="Total", digits=(16,4),type='float',store=False,multi='all'),
        'porcentage_equipo2':fields.function(_total2, string="%", digits=(16,2),type='float',store=False,multi='escenario2'),
#         'amount_equipo2': fields.function(_amount_all, string='Subtotal Equipo', digits=(16,4),
#             store={
#                 'cyg.apu': (lambda self, cr, uid, ids, c={}: ids, ['equipo2_ids'], 20),
#                 'cyg.apu.line': (_get_equipo2_line, ['price','qty','rendimiento','equipo2_id'], 20),
#             },
#             multi='all'),
#                 
        'materiales2_ids':fields.one2many('cyg.apu.line','material2_id','Materiales'),
        'amount_material2': fields.function(_amount_all, string="Total", digits=(16,4),type='float',store=False,multi='all'),
        'porcentage_material2':fields.function(_total2, string="%", digits=(16,2),type='float',store=False,multi='escenario2'),
#         'amount_material2': fields.function(_amount_all, string='Subtotal Material',digits=(16,4),
#             store={
#                 'cyg.apu': (lambda self, cr, uid, ids, c={}: ids, ['materiales2_ids'], 20),
#                 'cyg.apu.line': (_get_material2_line, ['price','qty','rendimiento','material2_id'], 20),
#             },
#             multi='all'),
        'transporte2_ids':fields.one2many('cyg.apu.line','transporte2_id','Transporte'),
        'amount_transporte2': fields.function(_amount_all, string="Total", digits=(16,4),type='float',store=False,multi='all'),
        'porcentage_transporte2':fields.function(_total2, string="%", digits=(16,2),type='float',store=False,multi='escenario2'),
#         'amount_transporte2': fields.function(_amount_all, string='Subtotal Transporte', digits=(16,4),
#             store={
#                 'cyg.apu': (lambda self, cr, uid, ids, c={}: ids, ['transporte2_ids'], 20),
#                 'cyg.apu.line': (_get_transporte2_line, ['price','qty','rendimiento','transporte2_id'], 20),
#             },
#             multi='all'),
        'mano_obra2_ids':fields.one2many('cyg.apu.line','mano2_id','Mano de Obra'),
        'amount_obra2': fields.function(_amount_all, string="Total", digits=(16,4),type='float',store=False,multi='all'),
        'porcentage_mano2':fields.function(_total2, string="%", digits=(16,2),type='float',store=False,multi='escenario2'),
        'otros2_ids':fields.one2many('cyg.apu.line','otro2_id','Otros'),
        'amount_otros2': fields.function(_amount_all, string="Total", digits=(16,4),type='float',store=False,multi='all'),
        'porcentage_otros2':fields.function(_total2, string="%", digits=(16,2),type='float',store=False,multi='escenario2'),
#         'amount_obra2': fields.function(_amount_all, string='Subtotal Mano Obra', digits=(16,4),
#             store={
#                 'cyg.apu': (lambda self, cr, uid, ids, c={}: ids, ['mano_obra2_ids'], 20),
#                 'cyg.apu.line': (_get_obra2_line, ['price','qty','rendimiento','mano2_id'], 20),
#             },
#             multi='all'),
        
        'amount_total': fields.function(_total, string="Total", digits=(16,4),type='float',store=False,multi='escenario1'),
        'amount_total2': fields.function(_total2, string="Total",digits=(16,4), type='float',store=False,multi='escenario2'),
        
        'user_id':fields.many2one('res.users','Usuario'),
        'state':fields.selection([
            ('draft','Borrador'),
            ('done','Valido'),
             ],'Estado', readonly=True),
        #'amount_indirectos'   
        #Categoria que sirve para filtrar
        'category_id':fields.many2one('product.category','Categoria'),
        'costo_directo':fields.float('Costo Directo'),
        'costo_indirecto':fields.float('Costo Indirecto'),
        'precio_total_ofertado':fields.float('Precio Total Ofertado'),
        'precio_total_calculado':fields.float('Precio Total Calculado'),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', required=True, readonly=True, states={'draft': [('readonly', False)], 'done': [('readonly', False)]}, help="Pricelist for current sales order."),
        'pricelist2_id': fields.many2one('product.pricelist', 'Pricelist', required=True, readonly=True, states={'draft': [('readonly', False)], 'done': [('readonly', False)]}, help="Pricelist for current sales order."),
        'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency", string="Currency", readonly=True, required=True),
        
    }
    _defaults = {
        'nro_decimales': 2,
        'state':'draft',
        'name': lambda obj, cr, uid, context: '/',
        'user_id':lambda self, cr, uid, ctx: uid,
        'date':lambda *a: time.strftime('%Y-%m-%d'),
        'category_id':lambda self,cr,uid,c: self.pool.get('product.category').search(cr, uid, [('name','=','EQUIPOS Y HERRAMIENTAS')], context=c)[0],
        #'category_id':lambda self,cr,uid,c: self.pool.get('product.category').search(cr, uid, [('name','=','EQUIPOS Y HERRAMIENTAS')], context=c)[0],
        'currency_id':lambda self,cr,uid,c: self.pool.get('res.currency').search(cr, uid, [('name','=','USD')], context=c)[0],
        'pricelist_id':1,
        'pricelist2_id':1,
        'nro_decimal':2,
        #'jornada_id':1,
        'uom_id':lambda self,cr,uid,c: self.pool.get('product.uom').search(cr, uid, [('name','=','m')], context=c)[0],
    }
    _sql_constraints = [ ('name_uniq', 'unique (code)', 'El codigo del APU es unico!'),      ]
    _order = "name"
    
cyg_apu()

class cyg_apu_line(osv.osv):
    _name = "cyg.apu.line"
    _description = "Linea de Escenarios de Precios Unitarios"
    
    def _amount(self, cursor, user, ids, name, args, context=None):
        #print 'context amount', context
        if not ids:
            return {}
        
        if context is None:
            context = {}
        res = {}
        #nro_decimal = 2
        #nro_decimal = 10 ** -nro_decimal
        #print 'nro_decimal',nro_decimal
        for line in self.browse(cursor, user, ids, context=context):
            res[line.id] = {'subtotal':0.00,
                           'total':0.00}
            res[line.id]['subtotal'] = line.price * line.qty
            #print 'res subtotal',res[line.id]['subtotal'] * line.rendimiento
            if line.product_id.product_tmpl_id.categ_id.name in ('EQUIPOS Y HERRAMIENTAS', 'MANO DE OBRA'):
                #res[line.id]['total'] = float_round(line.price * line.qty * line.rendimiento or 0.00,precision_rounding=nro_decimal)
                res[line.id]['total'] = line.price * line.qty * line.rendimiento or 0.00
            elif line.product_id.product_tmpl_id.categ_id.name in ('MATERIALES','TRANSPORTE'):
                #res[line.id]['total'] = float_round(line.price * line.qty,precision_rounding=nro_decimal)
                res[line.id]['total'] = line.price * line.qty
            else:
                res[line.id]['total'] = line.price * line.qty
        return res
    
    def on_change_product(self, cr, uid, ids, field_name,qty=0):
        res = {}
        #print '##################3',context
        product_obj = self.pool.get('product.product')
#         sql = "select pp.id from product_template pt, product_product pp, product_category pc where pt.id=pp.product_tmpl_id and pc.id=pt.catg_id and pc.name in ("
#         if context.get('categoria')=='EQUIPOS Y HERRAMIENTAS' :
#             categ = " 'EQUIPOS Y HERRAMIENTAS')"
#             sql += categ
#         if context.get('categoria')=='MANO DE OBRA' :
#             categ = " 'MANO DE OBRA')"
#             sql += categ
#         if context.get('categoria')=='MATERIALES' :
#             categ = " 'MATERIALES')"
#             sql += categ
#         if context.get('categoria')=='TRANSPORTE' :
#             categ = " 'TRANSPORTE')"
#             sql += categ
#         #print 'sql', sql
#         cr.execute(sql)
#         res = [aux[0] for aux in cr.fetchall()]
        if field_name:
            product_info = product_obj.browse(cr, uid, field_name)
            res['price'] = product_info.list_price
            res['qty']=1
            res['rendimiento']=product_info.rendimiento
            res['uom_id']=product_info.product_tmpl_id.uom_id and product_info.product_tmpl_id.uom_id.id or False
            res['name']=product_info.name,
        return {'value':res}
    
    _columns = {
                'name':fields.char('Descripcion', size=100),
                'date':fields.date('Fecha'),
                #Escenario 1
                'equipo_id':fields.many2one('cyg.apu','Escenario Equipo',ondelete='cascade'),
                'material_id':fields.many2one('cyg.apu','Escenario Material',ondelete='cascade'),
                'transporte_id':fields.many2one('cyg.apu','Escenario Trasporte',ondelete='cascade'),
                'mano_id':fields.many2one('cyg.apu','Escenario Mano de Obra',ondelete='cascade'),
                #Escenario 2
                'equipo2_id':fields.many2one('cyg.apu','Escenario Equipo',ondelete='cascade'),
                'material2_id':fields.many2one('cyg.apu','Escenario Material',ondelete='cascade'),
                'transporte2_id':fields.many2one('cyg.apu','Escenario Trasporte',ondelete='cascade'),
                'mano2_id':fields.many2one('cyg.apu','Escenario Mano de Obra',ondelete='cascade'),
                #otros
                'otro_id':fields.many2one('cyg.apu','Escenario Otros',ondelete='cascade'),
                'otro2_id':fields.many2one('cyg.apu','Escenario Otros',ondelete='cascade'),
                
                'uom_id':fields.many2one('product.uom','Unidad'),
                'qty':fields.float('Cantidad',digits_compute=dp.get_precision('Account')),
                'product_id':fields.many2one('product.product', 'Producto'),
                'price':fields.float('Precio Unitario',digits=(16,6)),
                'subtotal': fields.function(_amount, string='Subtotal',type='float',method=True,store=True,multi='all',digits=(16,6)),
                'rendimiento':fields.float('Rendimiento',digits=(16,6)),
                'desperdicio':fields.float('Desperdicio',digits=(16,6)),
                'total': fields.function(_amount, string='Total',type='float',method=True,store=True,multi='all',digits=(16,6)),
                #'total':fields.float('Total'),

                }
    _defaults = {  
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        
        }

cyg_apu_line()


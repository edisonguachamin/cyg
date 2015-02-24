# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today
#    CyG xxxx
#    @autor: Edison Guachamin <edison.guachamin@gmail.com>
#
##############################################################################
import datetime
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp

def strToDate(dt):
        dt_date=datetime.date(int(dt[0:4]),int(dt[5:7]),int(dt[8:10]))
        return dt_date

class cyg_presupuesto(osv.osv):
    _name = 'cyg.presupuesto'
    
    def create(self, cr, uid, vals, context={}):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cyg.budget') or '/'
        res_id = super(cyg_presupuesto, self).create(cr, uid, vals, context)
        return res_id
    
    def button_dummy(self, cr, uid, ids, context=None):
        resumen_obj = self.pool.get('cyg.presupuesto.resumen')
        presupuesto_line_obj = self.pool.get('cyg.presupuesto.line')
        resumen_ids =[]
        capitulos = []
        for item in self.browse(cr, uid,ids, context=context):
            if item.presupuesto_ids:
                for line in item.presupuesto_ids:
                    capitulos.append(line.capitulo_id.id)
                    resumen_ids = resumen_obj.search(cr, uid, [('presupuesto_id','=',item.id),
                                                               ('capitulo_id','=',line.capitulo_id.id)])
                    #list(set(resumen_ids))
                    if not resumen_ids:
                        resumen_obj.create(cr, uid,{'name':'resumen',
                                                    'presupuesto_id':item.id,
                                                    'capitulo_id':line.capitulo_id.id,
                                                    })
                if capitulos:
                    list(set(capitulos))
                    for l in capitulos:
                        amount = 0.00
                        iva = 0.00
                        lineas_ids = presupuesto_line_obj.search(cr, uid, [('presupuesto_id','=',item.id),
                                                                           ('capitulo_id','=',l)])
                        resumen_ids = resumen_obj.search(cr, uid, [('presupuesto_id','=',item.id),
                                                               ('capitulo_id','=',l)])
                        for x in presupuesto_line_obj.browse(cr, uid, lineas_ids):
                            amount += x.amount
                            #iva = x.amount * 1.12
                            #amount += iva 
                        resumen_obj.write(cr, uid,resumen_ids,{'amount':amount,'porcentaje':round(amount*100/item.amount_untaxed,2)} )
                
            print item
            
        return True
    
    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        cur_obj = self.pool.get('res.currency')
        
        cur = cur_obj.browse(cr, uid, 3)
        for apu in self.browse(cr, uid, ids, context=context):
            res[apu.id] = {
                'amount_total': 0.0,
                'amount_iva':0.0,
                'amount_untaxed':0.00
            }
            for line in apu.presupuesto_ids:
                
                res[apu.id]['amount_untaxed'] += cur_obj.round(cr, uid, cur, line.qty * line.price)
           
            res[apu.id]['amount_iva'] = res[apu.id]['amount_untaxed'] *0.12
            res[apu.id]['amount_total'] = res[apu.id]['amount_untaxed'] + res[apu.id]['amount_iva']
            print 'ampount_all', res
        return res
    
    def onchange_proyecto(self, cr, uid, ids, proyecto_id):
        res = {'value':{},'domain':{}}
        proyecto_obj = self.pool.get('cyg.proyecto')
        presupuesto_obj = self.pool.get('cyg.proyecto_linea_presupuesto')
        presupuesto_ids = presupuesto_obj.search(cr,uid,[('proyecto_id','=',proyecto_id)])
        tipos = []
        if presupuesto_ids:
            for item in presupuesto_obj.browse(cr, uid,presupuesto_ids):
                if item.tipo_presupuesto_id.code != 'cartera':
                    tipos.append(item.tipo_presupuesto_id.id)
            res['domain']['tipo_presupuesto_id'] =  [('id','in',tipos)]
        if proyecto_id:
            proyecto_info = proyecto_obj.browse(cr, uid, proyecto_id)
            res['value']['ubicacion']= proyecto_info.address or False
        return res
    
    def onchange_tipo(self, cr, uid, ids, tipo):
        res = {'value':{},'domain':{}}
        presupuesto_obj = self.pool.get('cyg.proyecto_linea_presupuesto')
        tipo_presupuesto_obj = self.pool.get('cyg.type.presupuesto')
        if tipo:
            presupuesto_ids = presupuesto_obj.search(cr, uid,[('proyecto_id','=',proyecto),
                                                              ('tipo_presupuesto_id','=',tipo)])
            if presupuesto_ids:
                presupuesto_info = presupuesto_obj.search(cr, uid, presupuesto_ids[0])
                #res['value']['director_id']= presupuesto_info.director_id and presupuesto_info.director_id.id or False
                res['value']['director_id']= presupuesto_info.director_id and presupuesto_info.director_id.id or False 
                res['value']['bodeguero_id']= presupuesto_info.bodeguero_id and presupuesto_info.bodeguero_id.id or False
                res['value']['ini_real_obra']=presupuesto_info.ini_real_obra or False
                res['value']['fin_real_obra']=presupuesto_info.fin_real_obra or False 
                res['value']['ini_prog_obra']=presupuesto_info.ini_prog_obra or False
                res['value']['fin_prog_obra']= presupuesto_info.fin_prog_obra or False
                res['value']['punto_equi_real']=presupuesto_info.punto_equi_real or False
                res['value']['punto_equi_prog']= presupuesto_info.punto_equi_prog or False
                res['value']['venta_real']=presupuesto_info.venta_real or False
                res['value']['venta_prog']= presupuesto_info.venta_prog or False
                res['value']['ini_oficina']=presupuesto_info.ini_oficina or False
                res['value']['fin_oficina']=presupuesto_info.fin_oficina or False
        return res
    
    def button_validar(self, cr, uid, ids,context={}):
        #for item in self.browse(cr, uid, ids):
        return self.write(cr,uid,ids,{'state':'done'})
    
    _columns = {
                'name':fields.char('Code',size=100),
                'codigo':fields.char('Codigo',size=100),
                'partner_id':fields.many2one('res.partner', 'Contratista'),
                'proyecto_id': fields.many2one('cyg.proyecto', 'Proyecto', ondelete='cascade'), 
                'etapa_id': fields.many2one('cyg.proyecto_etapa', 'Etapa', ondelete='cascade'),
                'ubicacion':fields.char('Ubicacion', size=1000),
                'date':fields.date('Fecha'),
                'capitulo_id':fields.many2one('cyg.apu.capitulo','Capitulo'),
                'tipo_presupuesto_id':fields.many2one('cyg.type.presupuesto','Tipo de Presupuesto'),
                # 'tipo_presupuesto_id': fields.selection([('directo', 'Costos directos'),
                                                 # ('indirecto', 'Costos indirectos'),
                                                 #------ ('cartera', 'Cartera'),
                                                 # ('sala_ventas', 'Sala de ventas'),
                                                 #------ ('oficina', 'Oficina'),
                                                 #--- ], 'Tipo de presupuesto'),
                'state':fields.selection([('draft','Abierto'),
                                          #('cancel', 'Cancelado'),
                                          #('confirm','Confirmado'),
                                          #('validate','Validado'),
                                          ('done','Cerrado')], 'Estado', select=True, readonly=True),
                'presupuesto_ids':fields.one2many('cyg.presupuesto.line','presupuesto_id','Lineas de Presupuesto'),
                'resumen_ids':fields.one2many('cyg.presupuesto.resumen','presupuesto_id','Resument Presupuesto'),
                'amount_total': fields.function(_amount_all, string="Total", digits=(16,4),type='float',store=False,multi='all'),
                'amount_iva': fields.function(_amount_all, string="Total Iva", digits=(16,4),type='float',store=False,multi='all'),
                'amount_untaxed': fields.function(_amount_all, string="Subtotal", digits=(16,4),type='float',store=False,multi='all'),
                'currency_id': fields.many2one('res.currency','Moneda'),
                'user_id': fields.many2one('res.users','Usuario'),
                #campos
                'director_id': fields.many2one('res.partner','Director/a o residente'),
                'bodeguero_id': fields.many2one('res.partner', 'Bodeguero/a'),
                'ini_real_obra': fields.date('Inicio real de la obra'),
                'fin_real_obra': fields.date('Fin real de la obra'),
                'ini_prog_obra': fields.date('Inicio programado de la obra'),
                'fin_prog_obra': fields.date('Fin programado de la obra'),
                'punto_equi_real': fields.date('Punto de equilibrio real'),
                'punto_equi_prog': fields.date('Punto de equilibrio programado'),
                'venta_real': fields.date('Venta real'),
                'venta_prog': fields.date('Venta programada'),
                'ini_oficina': fields.date('Inicio'),
                'fin_oficina': fields.date('Fin'),
               }
    _defaults = {  
                 'date': lambda *a: time.strftime('%Y-%m-%d'),
                 'name':'/',
                 'state':'draft',
                 'currency_id':lambda self,cr,uid,c: self.pool.get('res.currency').search(cr, uid, [('name','=','USD')], context=c)[0],
                 'user_id':lambda self, cr, uid, ctx: uid,
                 
        }
cyg_presupuesto()


class cyg_presupuesto_line(osv.osv):
    _name = 'cyg.presupuesto.line'
    _order = 'sequence_cap asc,sequence asc'
    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        #tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        cur = cur_obj.browse(cr, uid, 3)
        for line in self.browse(cr, uid, ids):
            price = line.price * line.qty
            
            res[line.id] = cur_obj.round(cr, uid, cur, price)
        return res
    
    def onchange_capitulo(self, cr, uid, ids, field_name):
        res = {}
        if field_name:
            capitulo_obj = self.pool.get('cyg.apu.capitulo')
            capitulo_info = capitulo_obj.browse(cr, uid, field_name)
            res['sequence_cap'] = int(capitulo_info.code)
        return {'value':res}
    
    def onchange_apu_escenario(self, cr, uid, ids, apu,escenario):
        res = {}
        if apu:
            apu_obj = self.pool.get('cyg.apu')
            apu_info = apu_obj.browse(cr,uid, apu)
            if escenario=='escenario_uno':
                precio = apu_info.amount_total
                res['price'] = precio or 0.00
                #res['price'] = precio * 
            elif escenario=='escenario_dos':
                precio = apu_info.amount_total2
                res['price'] = precio or 0.00
                
            res['uom_id'] = apu_info.uom_id and apu_info.uom_id.id or False
            res['code'] = apu_info.code
        print 'res', res
        return {'value':res}
    
    _columns = {
                'presupuesto_id': fields.many2one('cyg.presupuesto', 'Presupuesto', ondelete='cascade', select=True),
                'apu_id':fields.many2one('cyg.apu','Analisis de Precios Unitarios'),
                'capitulo_id':fields.many2one('cyg.apu.capitulo','Capitulo'),
                'precio_escenario':fields.selection([('escenario_uno','Escenario 1'),
                                                     ('escenario_dos','Escenario 2')],'Escoja Escenario'),
                'price':fields.float('Precio Unitario',digits_compute=dp.get_precision('Account')),
                #'amount':fields.float('Valor Total',digits_compute=dp.get_precision('Account')),
                'amount': fields.function(_amount_line, string='V.Total', type="float",
                                                  digits_compute= dp.get_precision('Account'), store=True),
                'uom_id':fields.many2one('product.uom','Unidad'),
                'code':fields.char('Rubro', size=100),
                'qty':fields.float('Cantidad'),
                'sequence_cap':fields.integer('Sequencia Capitulo'),
                'sequence':fields.integer('Sequencia'),
               }
    _defaults = {  
        #'datee': lambda *a: time.strftime('%Y-%m-%d'),
        'sequence':1,
        'qty':1,
        'precio_escenario':'escenario_uno'
        }
cyg_presupuesto_line()

class cyg_presupuesto_resumen(osv.osv):
    _name='cyg.presupuesto.resumen'
    
    _columns = {'name':fields.char('Nombre', size=500),
                'presupuesto_id': fields.many2one('cyg.presupuesto', 'Presupuesto', ondelete='cascade', select=True),
                'capitulo_id':fields.many2one('cyg.apu.capitulo','Capitulo'),
                'amount':fields.float('Total',digits_compute=dp.get_precision('Account')),
                'porcentaje':fields.float('Porcentaje',digits_compute=dp.get_precision('Account')),
                }
cyg_presupuesto_resumen()

class cyg_presupuesto_reforma(osv.osv):
    _name='cyg.presupuesto.reforma'
    
    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        #tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        cur = cur_obj.browse(cr, uid, 3)
        for line in self.browse(cr, uid, ids):
            price = line.price * line.qty
            
            res[line.id] = cur_obj.round(cr, uid, cur, price)
        return res


    _columns = {'name':fields.char('Nombre', size=500),
                'presupuesto_id': fields.many2one('cyg.presupuesto', 'Presupuesto', ondelete='cascade', select=True),
                'capitulo_id':fields.many2one('cyg.apu.capitulo','Capitulo'),
                'producto_id':fields.many2one('product.product','Producto'),
                'price':fields.float('Precio Unitario',digits_compute=dp.get_precision('Account')),
                'apu_id':fields.many2one('cyg.apu','Analisis de Precios Unitarios'),
                'uom_id':fields.many2one('product.uom','Unidad'),
                'code':fields.char('Rubro', size=100),
                'qty':fields.float('Cantidad'),
                'sequence_cap':fields.integer('Sequencia Capitulo'),
                'amount': fields.function(_amount_line, string='V.Total', type="float",
                                                  digits_compute= dp.get_precision('Account'), store=True),
                }
cyg_presupuesto_reforma()

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
import datetime
import openerp.addons.decimal_precision as dp

class proyecto_inmueble(osv.Model):
    #_name = 'sale.order'
    _inherit = 'cyg.proyecto_inmueble'
    _columns = {
                'sale_paymentes_ids':fields.one2many('cyg.payment','inmueble_id','Pagos'),
                'sale_cuota_ids':fields.one2many('cyg.inmueble.cuota','inmueble_id','Cuotas')
                }
proyecto_inmueble()


class cyg_payment_type(osv.osv):
    _name ='cyg.payment.type'
    _columns = {
                'name':fields.char('Nombre',size=100),
                'code':fields.char('codigo',size=100),
                }
cyg_payment_type()

class sale_order(osv.Model):
    #_name = 'sale.order'
    _inherit = 'sale.order'
    
    def _fnt_pagado(self,cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            pendiente = 0.00
            if len(order.pagos_ids) > 0:
                for item in order.pagos_ids:
                    pendiente += item.amount  
            res[order.id]= pendiente
        return res
    
    def _fnt_payment_extras(self,cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {'amount_payment_extra_cliente':0.00,
                             'amount_payment_extra_proyecto':0.00,
                             'amount_payment_extra_total':0.00,
                             }
            val1 = val2=val3 =0.00
            if order.payments_extras_ids:
                for item in order.payments_extras_ids:
                    if item.type=='cliente':
                        val1 += round(item.valor,2)
                    if item.type=='proyecto':
                        val2 += round(item.valor,2)
            res[order.id]['amount_payment_extra_cliente']=val1
            res[order.id]['amount_payment_extra_proyecto']=val2
            res[order.id]['amount_payment_extra_total']=round(val1  - val2,2)
            
        return res
    
    def _fnt_devolucion_extras(self,cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            val1 = val2=val3 =0.00
            if order.pagos_devolucion_ids:
                for item in order.pagos_devolucion_ids:
                    val1 += round(item.valor_devuelto,2)
            res[order.id]=val1
        return res
    
    
    def _fnt_devolucion_pending(self,cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            val1 = val2=val3 =0.00
            if order.pagos_devolucion_ids:
                for item in order.pagos_devolucion_ids:
                    val1 += item.valor_devuelto
            res[order.id]=order.amount_payment_extra_total - val1
        return res
    
    def button_dummy2(self, cr, uid, ids, context={}):
        #print 'entra',
        for item in self.browse(cr, uid, ids,context=context):
            val1 =val2=val3=val4=val5=0.00
            if item.payments_extras_ids:
                for x in item.payments_extras_ids:
                    if x.type=='cliente':
                        val1 += round(x.valor,2)
                    if x.type=='proyecto':
                        val2 += round(x.valor,2)
            if item.pagos_devolucion_ids:
                for x in item.pagos_devolucion_ids:
                    val3 += round(x.valor_devuelto,2)
            val4 = round(val1 - val2,2)
            val5 = round(val4 - val3,2)
            dict ={'amount_payment_extra_pendiente':round(val5,2)}
            if not val5:
                dict.update({'state':'paid'})
            else:
                dict.update({'state':'overpaid'})
            self.write(cr, uid,[item.id],dict)
        return True
    _columns = {
                'pagos_ids':fields.one2many('cyg.payment','sale_order_id','Pagos'),
                'payments_extras_ids':fields.one2many('cyg.payment.extra','sale_id','Pago Extras'),
                'pagos_devolucion_ids':fields.one2many('cyg.payment.devolucion','sale_id','Registro Devolución'),
                'amount_paid':fields.function(_fnt_pagado, string='Valor Pagado', type='float', digits_compute=dp.get_precision('Account'),  method=True, store=False),
                'amount_payment_extra_cliente':fields.function(_fnt_payment_extras, string='Total Cliente', type='float', digits_compute=dp.get_precision('Account'),  method=True, store=False,multi="payment_extras"),
                'amount_payment_extra_proyecto':fields.function(_fnt_payment_extras, string='Total Proyecto', type='float', digits_compute=dp.get_precision('Account'),  method=True, store=False,multi="payment_extras"),
                'amount_payment_extra_total':fields.function(_fnt_payment_extras, string='Resultado', type='float', digits_compute=dp.get_precision('Account'),  method=True, store=False,multi="payment_extras"),
                'amount_payment_extra_pagado':fields.function(_fnt_devolucion_extras, string='Pagado', type='float', digits_compute=dp.get_precision('Account'),  method=True, store=False),
                #'amount_payment_extra_pendiente':fields.function(_fnt_devolucion_pending, string='Pendiente', type='float', digits_compute=dp.get_precision('Account'),  method=True, store=False),
                'amount_payment_extra_pendiente':fields.float('Pendiente'),
                }
sale_order()


class cyg_payment(osv.osv):
    _name = 'cyg.payment'
    _description = 'Clase se genera los objetos de pagos de los inmuebles'
    
    def attachment_tree_view(self, cr, uid, ids, context):
        """ View a list of projects attachments """

        domain = [
            ('res_model', '=', 'cyg.payment'),
            ('res_id', 'in', ids),
            ]
        res_id = ids and ids[0] or False
        return {
            'name': 'Adjuntos',
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, res_id)
        }
    
    def button_validar(self, cr, uid, ids, context={}):
        cuota_obj = self.pool.get('cyg.inmueble.cuota')
        sale_inmueble = self.pool.get('cyg.proyecto_inmueble')
        payment_line_obj = self.pool.get('cyg.payment.line')
        sale_order_obj = self.pool.get('sale.order')
        payment_extras_obj = self.pool.get('cyg.payment.extra')
        cur_obj = self.pool.get('res.currency')
        cur = cur_obj.browse(cr, uid, 3)
        for item in self.browse(cr, uid, ids):
            sale_id = item.sale_order_id
            monto = item.amount
            saldo = 0.00
            sald2 = 0.00
            lc = []
            residual = 0.00
            if sale_id:
                residual = sale_id.amount_pending
                if monto > sale_id.amount_pending:
                    diff = monto - sale_id.amount_pending
                    payment_extras_obj.create(cr, uid,{'name':'Excedentes de Pagos',
                                                       'sale_id':sale_id.id,
                                                       'type':'cliente',
                                                       'date':item.date_payment,
                                                       'valor':round(diff,2),
                                                       'state':'overpaid'
                                                       })
                    sale_order_obj.write(cr, uid,[sale_id.id],{'state':'overpaid',
                                                               'amount_pending':0.00,
                                                               'amount_paid':round(sale_id.total + diff,2)})
                    #raise osv.except_osv(('Aviso !'), (u'El monto de pago supera el valor pendiente del credito en '+str(diff)+' revise el valor gracias!'))
                else:
                    residual = round(sale_id.amount_pending-monto,2)
                    sale_order_obj.write(cr, uid,[sale_id.id],{'amount_pending':sale_id.amount_pending-monto,
                                                               'amount_paid':sale_id.total - residual})
                #cuotas_ids = cuota_obj.search(cr, uid, [('state','=','done'),('sale_id','=',sale_id.id)],order='cuota asc')
                #print 'cuotas_ids', cuotas_ids
                sql = "select id from cyg_inmueble_cuota where sale_id = "+str(sale_id.id)+' order by fecha, cuota asc'
                cr.execute(sql)
                result = cr.fetchall()
                #print 'result', result
                cuotas_ids = [aux[0] for aux in result]
                #print '*******', cuotas_ids
                for line in cuota_obj.browse(cr, uid,cuotas_ids):
                    #print 'line', line.id
                    if line.afecta_precio =='no':
                        continue
                    if line.state == 'done':
                        #print 'monto entrada', monto
                        saldo = cur_obj.round(cr, uid, cur, monto - line.pendiente)
                        monto = saldo
                        
                        #print 'saldo', monto

                        val = {'name':line.code,
                               'cuota':line.cuota,
                               'payment_id':item.id,
                               'cuota_id':line.id,
                               'concepto':line.concepto,
                               'valor_cuota_cliente':line.cliente,
                               'valor_pagado_cliente':line.pendiente,
                               'valor_pendiente_cliente':0.00,
                               'valor_pagado_promotor':line.promotor,
                               'valor_pendiente_promotor':0.00, 
                               'state':'paid',}
                        if saldo > 0:
                             
                            cuota_obj.write(cr, uid, [line.id],{'comprobante':item.comprobante,
                                                                'pagado':line.pendiente,
                                                                'pendiente':0.00,
                                                                'state':'paid',
                                                                'parcial':False,
                                                                'fecha_pago':item.date_payment, 
                                                                'bank_id': item.bank_id and item.bank_id.id or False})
                            payment_line_obj.create(cr,uid,val)
                            continue
                        if saldo < 0:
                            valor = line.pendiente + saldo
                            #print 'line.cliente + saldo', valor
                            val.update({'valor_cuota_cliente':line.cliente ,
                                        'valor_pagado_cliente':valor,
                                        'valor_pendiente_cliente':- saldo,
                                        'valor_pagado_promotor':monto,
                                        'valor_pendiente_promotor':- saldo,
                                        'state':'done',
                                        })
                            
                            cuota_obj.write(cr, uid, [line.id],{'comprobante':item.comprobante,
                                                                'pagado': valor,
                                                                'pendiente':-saldo,
                                                                'parcial':True,
                                                                'fecha_pago':item.date_payment, 
                                                                'bank_id': item.bank_id and item.bank_id.id or False}) 
                            payment_line_obj.create(cr,uid,val)
                            break
                        else:#igual a cero
                            #print 'igual a cero'
                            cuota_obj.write(cr, uid, [line.id],{'comprobante':item.comprobante,
                                                                'pagado':line.pendiente,
                                                                'pendiente':0.00,
                                                                #este campo aumente antes mismo
                                                                'state':'paid',
                                                                'parcial':False,
                                                                'fecha_pago':item.date_payment,
                                                                'bank_id': item.bank_id and item.bank_id.id or False})
                            payment_line_obj.create(cr,uid,val)
                            break
                        
            if not residual:
                sale_order_obj.write(cr, uid,[sale_id.id],{'state':'paid'})    
                    
        return self.write(cr,uid, ids,{'state':'done'})
    
    def onchange_inmueble(self, cr, uid, ids, partner_id, inmueble_id):
        #sale_inmueble = self.pool.get('sale.inmueble.line')
        #print 'partner_id', partner_id
        #print 'inmueble_id', inmueble_id
        res = {}
        domain = {}
        sale_inmueble = self.pool.get('cyg.proyecto_inmueble')
        if partner_id and inmueble_id:
            inmueble_ids = sale_inmueble.search(cr,uid,[('partner_id','=',partner_id),
                                                        ('id','=',inmueble_id),
                                                        ('state','=','vendido')])
            #print 'inmueble_ids', inmueble_ids
            if inmueble_ids:
                info = sale_inmueble.browse(cr, uid,inmueble_ids[0])
                res['sale_order_id'] = info.sale_id and info.sale_id.id
                domain['sale_order_id'] = [('id','in',inmueble_ids),('state','=','vendido')]
        else:
            res['sale_order_id'] = False
            domain['sale_order_id'] = [('partner_id','=',partner_id),('state','=','vendido')]
        #print 'domain', domain
        return {'value':res,'domain': domain}
    
    def create(self, cr, uid, vals, context={}):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cyg.payment') or '/'
        if vals.get('inmueble_id'):
            inmueble_obj = self.pool.get('cyg.proyecto_inmueble')
            inmueble_info = inmueble_obj.browse(cr, uid, vals.get('inmueble_id'))
            vals['proyecto_id'] = inmueble_info.proyecto_id and inmueble_info.proyecto_id.id or False 
        res_id = super(cyg_payment, self).create(cr, uid, vals, context)
        return res_id
    
    def unlink(self, cr, uid, ids, context=None):
        #TODO: process before delete resource
        list = []
        for item in self.browse(cr, uid, ids):
            if item.state != 'draft':
                raise osv.except_osv(('Aviso !'), (u'No se permite borrar un pago en estado validado'))
            else:
                list.append(item.id)
        res = super(cyg_payment, self).unlink(cr, uid, list, context)
        return res 
    
    def onchange_banco(self,cr, uid,ids, field_name):
        res = {}
        bank_obj = self.pool.get('res.partner.bank')
        bancos = []
        if field_name:
             info = bank_obj.browse(cr, uid, field_name)
             res['nro_cuenta'] = info.acc_number
             
        return {'value':res}
    
    def onchange_proyecto(self,cr, uid,ids, field_name):
        res = {}
        domain = {}
        bancos = []
        bank_obj = self.pool.get('res.partner.bank')
        proyecto_obj = self.pool.get('cyg.proyecto')
        if field_name:
            info = proyecto_obj.browse(cr, uid, field_name)
            if info.datos_bancarios_ids:
                for b in info.datos_bancarios_ids:
                    res['bank_id'] = b.id
                    res['nro_cuenta'] = b.acc_number
                    bancos.append(b.id)
            domain['bank_id'] = [('id','in',bancos)]
        
        return {'value':res,'domain':domain}
    
    def _format_date(self, date):
        if date:
            campos = date.split('-')
            date = datetime.date(int(campos[0]), int(campos[1]), int(campos[2]))
            return date
    
    def onchange_fecha_pago(self, cr, uid, ids,field,field_name):
        res = {'value':{}}
        now = datetime.date.today()
        if field:
            fecha_pago = self._format_date(field)
            if fecha_pago > now:
                return {'value':{field_name:''},
                        'warning':{'title': "Error", "message": "La fecha de pago no debe ser mayor que la fecha actual"}}
        return res
    
    _columns = {
                'name': fields.char('Code', size=500),
                'comprobante': fields.char('Comprobante', size=500),
                'sale_order_id':fields.many2one('sale.order','Pedido'),
                'date': fields.date('Fecha de Registro'),
                'date_payment': fields.date('Fecha de Pago'),
                'user_id': fields.many2one('res.users','Usuario'),
                'bank_id': fields.many2one('res.partner.bank','Banco'),
                'partner_id': fields.many2one('res.partner','Cliente'),
                'inmueble_id':fields.many2one('cyg.proyecto_inmueble','Inmuebles'),
                'proyecto_id': fields.many2one('cyg.proyecto', 'Proyecto'),
                'etapa_id': fields.related('inmueble_id', 'etapa_id',
                                       type='many2one',
                                       relation='cyg.proyecto_etapa',
                                       string='Etapa',
                                       store=False,
                                       readonly=True),
                'note':fields.text('Observaciones'),
                'amount':fields.float('Valor del Pago'),
                'pendiente':fields.float('Valor Pendiente'),
                'mora':fields.float('Valor Mora'),
                #'nro_documento':
                'state':fields.selection([
                    ('draft','Borrador'),
                    ('done','Validado'),
                    ],'Estado', select=True, readonly=True),
                'type_id':fields.many2one('cyg.payment.type','Tipo de Pago'),
                'type_payment':fields.selection([
                    ('efectivo','Efectivo'),
                    ('banco','Banco'),
                    ],'Tipo de Pago', select=True),
                'payment_lines_ids':fields.one2many('cyg.payment.line','payment_id','Cuotas'),
                
                'nro_cuenta':fields.char('Nro Cuenta',size=100),
                #'company_id':fields.many2one('res.company','Compania'),
                
               }
    _defaults = {  
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'state':'draft',
        'user_id':lambda self, cr, uid, ctx: uid,
        'name': lambda obj, cr, uid, context: '/',
        #'partner_id':_get_partner,
        #'sale_order_id':_get_sale,
        }
cyg_payment()

class cyg_payment_line(osv.Model):
    _name ='cyg.payment.line'
    _description = 'Linea de Pago'
    _columns = {
                'name':fields.char('Code', size=64),
                'cuota':fields.char('Cuota', size=64),
                'payment_id':fields.many2one('cyg.payment','Pago'),
                'cuota_id':fields.many2one('cyg.inmueble.cuota','Cuota'),
                'fecha': fields.related('cuota_id', 'fecha',
                                       type='date',
                                       relation='cyg.inmueble.cuota',
                                       string='Fecha vencimiento',
                                       store=False,
                                       readonly=True),
                'valor_cuota_cliente':fields.float('Valor Cuota Cliente'),
                'valor_pagado_cliente':fields.float('Valor Pagado Cliente'),
                'valor_pendiente_cliente':fields.float('Valor Pendiente Cliente'),
                'valor_pagado_promotor':fields.float('Valor Pagado Promotor'),
                'valor_pendiente_promotor':fields.float('Valor Pendiente Promotor'),
                'state': fields.selection([ ('draft', 'Borrador'),
                                            ('sent', 'Proforma Enviada'),
                                            ('reservado', 'Reservado'),
                                            ('cancel', 'Cancelada'),
                                            ('desistido', 'Desistido'),
                                            ('done', 'Pendiente'),
                                            ('paid', 'Pagada'),
                                            ], 'Estado', readonly=True,select=True),
                'concepto':fields.selection([('reserva','Reserva'),
                                            ('entrada','Entrada'),
                                            ('financiamiento','Financiamiento'),
                                            ('extraordinaria','Cuota Extraordinaria'),
                                            ('descuento','Descuento'),
                                            ('penalizacion','Penalización'),
                                            ('desistido','Desistido'),
                                            ('saldo_reserva','Saldo reserva 10%'),
                                            ('bono_vivienda','Bono de vivienda'),
                                            ('cuota_extra','Cuota por extras'),
                                            ],'Concepto'),
                }
cyg_payment_line()   

class cyg_payment_devolucion(osv.osv):
    _name ='cyg.payment.devolucion'
    _description = 'Pagos Devoluciones'
    
    def button_validar(self, cr, uid, ids, context={}):
        sale_order_obj =self.pool.get('sale.order')
        sale_cuota_obj = self.pool.get('cyg.inmueble.cuota')
        for item in self.browse(cr, uid,ids,context=context):
            info_sale = sale_order_obj.browse(cr, uid,item.sale_id.id)
            pendiente = info_sale.amount_payment_extra_pendiente
            print 'pendiente',pendiente   
            if item.valor_devuelto > info_sale.amount_payment_extra_pendiente:
                raise osv.except_osv(('Aviso !'), (u'El valor devuelto supera el valor esperado '))
                break
            elif item.valor_devuelto < 0:
                raise osv.except_osv(('Aviso !'), (u'El valor devuelto no debe ser negativo'))
            elif not item.valor_devuelto:
                raise osv.except_osv(('Aviso !'), (u'El valor devuelto no debe ser cero'))
            else:
                if item.valor_devuelto== info_sale.amount_payment_extra_pendiente:
                    sale_order_obj.write(cr,uid,[item.sale_id.id],{'state':'paid','amount_payment_extra_pendiente':0.00})
                else:
                    sale_order_obj.write(cr,uid,[item.sale_id.id],{'amount_payment_extra_pendiente':info_sale.amount_payment_extra_pendiente-item.valor_devuelto})
        return self.write(cr, uid, ids, {'state':'done'})
    
    def attachment_tree_view(self, cr, uid, ids, context):
        """ View a list of projects attachments """

        domain = [
            ('res_model', '=', 'cyg.payment.devolucion'),
            ('res_id', 'in', ids),
            ]
        res_id = ids and ids[0] or False
        return {
            'name': 'Adjuntos',
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, res_id)
        }

    def create(self, cr, uid, vals, context={}):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cyg.payment.devolucion') or '/'
        res_id = super(cyg_payment_devolucion, self).create(cr, uid, vals, context)
        return res_id
    
    def unlink(self, cr, uid, ids, context=None):
        #TODO: process before delete resource
        list = []
        for item in self.browse(cr, uid, ids):
            if item.state != 'draft':
                raise osv.except_osv(('Aviso !'), (u'No se permite borrar un pago en estado validado'))
            else:
                list.append(item.id)
        res = super(cyg_payment_devolucion, self).unlink(cr, uid, list, context)
        return res   
    
    def _format_date(self, date):
        if date:
            campos = date.split('-')
            date = datetime.date(int(campos[0]), int(campos[1]), int(campos[2]))
            return date
    
    def onchange_fecha_pago(self, cr, uid, ids,field,field_name):
        res = {'value':{}}
        now = datetime.date.today()
        if field:
            fecha_pago = self._format_date(field)
            if fecha_pago > now:
                return {'value':{field_name:''},
                        'warning':{'title': "Error", "message": "La fecha de devolucion no debe ser mayor que la fecha actual"}}
        return res

 
    _columns = {
                'name':fields.char('Nombre',size=100),
                'code':fields.char('Codigo',size=100),
                'sale_id':fields.many2one('sale.order','Venta'),
                'type':fields.char('Tipo',size=100),
                'comprobante':fields.char('Comprobante',size=500),
                'user_id':fields.many2one('res.users','Usuario'),
                'date':fields.date('Fecha de Registro'),
                'fecha_devolucion':fields.date('Fecha de Devolución'),
                'bank_id': fields.many2one('res.partner.bank','Banco'),
                'partner_id': fields.many2one('res.partner','Cliente'),
                'inmueble_id':fields.many2one('cyg.proyecto_inmueble','Inmuebles'),
                'proyecto_id': fields.many2one('cyg.proyecto', 'Proyecto'),
                'etapa_id': fields.many2one('cyg.proyecto_etapa','Etapa'),
                
                'valor_devuelto':fields.float('Valor devuelto'),
                'type_payment':fields.selection([
                    ('efectivo','Efectivo'),
                    ('banco','Banco'),
                    ],'Tipo de Pago', select=True),
                'note':fields.text('Observaciones'),
                'state':fields.selection([
                    ('draft','Borrador'),
                    ('done','Validado'),
                    ],'Estado', select=True, readonly=True),
                }
    _defaults = {  
        'name': '/',
        'state':'draft',
        'user_id':lambda self, cr, uid, ctx: uid,
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'type':'Devolucion'
        }
    
cyg_payment_devolucion()

class cyg_payment_extra(osv.osv):
    _name ='cyg.payment.extra'
    _description = 'Pagos Extras'
    def create(self, cr, uid, vals, context={}):
        if vals.get('code','/')=='/':
            vals['code'] = self.pool.get('ir.sequence').get(cr, uid, 'cyg.payment.extra') or '/'
        res_id = super(cyg_payment_extra, self).create(cr, uid, vals, context)
        return res_id
    
    def _format_date(self, date):
        if date:
            campos = date.split('-')
            date = datetime.date(int(campos[0]), int(campos[1]), int(campos[2]))
            return date
    
    def onchange_fecha_pago(self, cr, uid, ids,field,field_name):
        res = {'value':{}}
        now = datetime.date.today()
        if field:
            fecha_pago = self._format_date(field)
            if fecha_pago > now:
                return {'value':{field_name:''},
                        'warning':{'title': "Error", "message": "La fecha de pago no debe ser mayor que la fecha actual"}}
        return res
    
    
    
    _columns = {
                'name':fields.char('Descripción',size=100),
                'descripcion_id':fields.many2one('cyg.payment.extra.descripcion','Descripción'),
                'code':fields.char('codigo',size=100),
                'sale_id':fields.many2one('sale.order','Venta'),
                'type':fields.selection([('cliente','Cliente'),
                                         ('proyecto','Proyecto'),],'Beneficiario'),
                'user_id':fields.many2one('res.users','Usuario'),
                'date':fields.date('Fecha de Devolución'),
                
                'valor':fields.float('Valor'),
                
                'note':fields.text('Observaciones'),
                'state':fields.selection([
                    ('overpaid','Sobrepagado'),
                    ('paid','Pagado'),
                    ],'Estado', select=True, readonly=True),
                }
    _defaults = {  
        'code': '/',
        'state':'overpaid',
        'user_id':lambda self, cr, uid, ctx: uid,
        }
cyg_payment_extra()


class sale_inmueble_cuota(osv.osv):
    #_name = 'sale.order'
    _inherit = 'cyg.inmueble.cuota'
    _columns = {
                'deposit_ids':fields.one2many('cyg.payment.deposit','cuota_id','Abono/Pagos Mora'),
                }
sale_inmueble_cuota()

class cyg_payment_deposit(osv.Model):
    _name = 'cyg.payment.deposit'
    _description = 'Registrar pago de abono y moras sobre la cuota'
    
    def _get_type(self, cr, uid, context=None):
        if context is None:
            context = {}
        return context.get('type', 'abono')
    
    def button_validar(self, cr, uid, ids, context={}):
        cuota_obj = self.pool.get('cyg.inmueble.cuota')
        deposit_line_obj = self.pool.get('cyg.payment.deposit.line')
        payment_line_obj = self.pool.get('cyg.payment.line')
        payment_obj = self.pool.get('cyg.payment')
        sale_order_obj = self.pool.get('sale.order')
        cur_obj = self.pool.get('res.currency')
        #cur = cur_obj.browse(cr, uid, 3)
        for item in self.browse(cr, uid, ids):
            dict = {'name':item.name,
                    'type':item.type,
                    'deposit_id':item.id,
                    'valor_cuota':item.cuota_id.cliente,
                    'comprobante':item.comprobante or '',
                    'fecha':item.date_payment,
                    'valor_mora':item.amount_interes_mora or 0.00,
                    'amount':item.amount,
                    'state':'done'
                    }
            if not item.amount or item.amount < 0:
                raise osv.except_osv(('Aviso !'), (u'El valor que va a registrar debe ser mayor a cero'))
            if item.type =='abono':
                if item.amount > item.cuota_id.pendiente:
                    raise osv.except_osv(('Aviso !'), (u'El valor supera al valor pendiente'))
                else:
                    dict.update({'valor_pendiente_cuota':item.cuota_id.pendiente-item.amount})
                    if item.amount == item.cuota_id.pendiente:
                        cuota_obj.write(cr, uid, [item.cuota_id.id],{'pendiente':0.00,
                                                                     'mostrar_pagos':True,
                                                                     'valor_pagado_abono':item.amount,
                                                                     'fecha_pago_abono':item.date_payment,
                                                                     'valor_actual_pendiente':item.valor_actual_pendiente,
                                                                     'state':'paid'})
                        
                        
                    else:
                        cuota_obj.write(cr, uid, [item.cuota_id.id],{'pendiente':item.cuota_id.pendiente - item.amount,
                                                                     'mostrar_pagos':True,
                                                                     'valor_pagado_abono':item.amount,
                                                                     'fecha_pago_abono':item.date_payment,
                                                                     'valor_actual_pendiente':item.valor_actual_pendiente,
                                                                     })
                        
                    
                    true = deposit_line_obj.create(cr, uid,dict)
                    if true:
                        paymente_dict = {
                                        'date_payment':item.date_payment,
                                        'user_id': uid,
                                        'partner_id': item.partner_id and item.partner_id.id,
                                        'inmueble_id':item.inmueble_id and item.inmueble_id.id or False,
                                        'sale_order_id':item.sale_id and item.sale_id.id,
                                        'note': item.note,
                                        'amount':item.amount,
                                        'pendiente':item.cuota_id.pendiente - item.amount,
                                        'state':'done',
                                        'proyecto_id':item.cuota_id.project_id and item.cuota_id.project_id.id or False,
                                        'etapa_id':item.inmueble_id and item.inmueble_id.etapa_id and item.inmueble_id.etapa_id.id or False,  
                                        }
                        id_payment = payment_obj.create(cr,uid,paymente_dict)
                        line_payment = {'name':'Abono',
                                       'cuota':item.cuota_id.cuota,
                                       'payment_id':id_payment,
                                       'cuota_id':item.cuota_id.id,
                                       'concepto':item.cuota_id.concepto,
                                       'valor_cuota_cliente':0.00,
                                       'valor_pagado_cliente':item.amount,
                                       'valor_pendiente_cliente':0.00,
                                       'valor_pagado_promotor':item.cuota_id.promotor,
                                       'valor_pendiente_promotor':0.00, 
                                       'state':'paid',}
                        payment_line_obj.create(cr, uid,line_payment)
                        sale_id = item.sale_id
                        residual = sale_id.amount_pending-item.amount
                        sale_order_obj.write(cr, uid,[sale_id.id],{'amount_pending':sale_id.amount_pending-item.amount,
                                                                   'amount_paid':sale_id.total - residual})
                        if not residual:
                            sale_order_obj.write(cr, uid,[sale_id.id],{'state':'paid'})
                        
            if item.type =='mora':
                if item.amount > item.amount_interes_mora:
                    raise osv.except_osv(('Aviso !'), (u'El valor supera al valor pendiente'))
                else:
                    dict.update({'valor_pendiente_mora':item.amount_interes_mora-item.amount})
                    cuota_obj.write(cr, uid, [item.cuota_id.id],{'mostrar_pagos':True,
                                                                 'valor_pagado_mora':item.amount,
                                                                 'fecha_pago_mora':item.date_payment,
                                                                 'valor_mora':item.amount_interes_mora,#interes de mora a la fecha del pago
                                                                 'mora_paid':True #marco si la mora esta pagada
                                                                 })
                    deposit_line_obj.create(cr, uid,dict)
            if item.type =='extra':
                if item.amount > item.cuota_id.pendiente:
                    raise osv.except_osv(('Aviso !'), (u'El valor supera al valor pendiente'))
                else:
                    dict.update({'valor_pendiente_cuota':item.cuota_id.pendiente-item.amount})
                    valor_extra = item.cuota_id.valor_extra or  0.00
                    valor_extra += item.amount
                    if item.amount == item.cuota_id.pendiente:
                        
                        cuota_obj.write(cr, uid, [item.cuota_id.id],{'pendiente':0.00,
                                                                     'mostrar_extra':False,
                                                                     'mostrar_pagos':True,
                                                                     'valor_extra':valor_extra,
                                                                     'fecha_pago_extra':item.date_payment,
                                                                     'descripcion_extra':item.note,
                                                                     'state':'paid'})
                        
                        
                    else:
                        cuota_obj.write(cr, uid, [item.cuota_id.id],{'pendiente':item.cuota_id.pendiente - item.amount,
                                                                     'mostrar_extra':True,
                                                                     'mostrar_pagos':True,
                                                                     'valor_extra':valor_extra,
                                                                     'fecha_pago_extra':item.date_payment,
                                                                     'descripcion_extra':item.note,
                                                                     'state':'done',
                                                                     })
                        
                    
                    deposit_line_obj.create(cr, uid,dict)
                    
                
        return self.write(cr,uid, ids,{'state':'done'})
    
    def attachment_tree_view(self, cr, uid, ids, context):
        """ View a list of projects attachments """

        domain = [
            ('res_model', '=', 'cyg.payment.deposit'),
            ('res_id', 'in', ids),
            ]
        res_id = ids and ids[0] or False
        return {
            'name': 'Adjuntos',
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, res_id)
        }
    
    def create(self, cr, uid, vals, context={}):
        if vals.get('name','/')=='/':
            if context.get('default_type', False):
                if context.get('default_type') == 'abono':
                    vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cyg.deposit.abono') or '/'
                if context.get('default_type') == 'mora':
                    vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cyg.deposit.mora') or '/'
                if context.get('default_type') == 'extra':
                    vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cyg.payment.extra') or '/'
        res_id = super(cyg_payment_deposit, self).create(cr, uid, vals, context)
        return res_id
    
    def onchange_descuento(self, cr, uid, ids, abono, interes, dias):
        res = {'value':{}}
        if interes:
            if interes < 0 or interes > 100:
                return {'value':{'tasa_interes':0},
                        'warning':{'title': "Error", "message": "La tasa de interes debe estar entre 0 y 100"}}
        
        if abono and interes and dias:
            interes = interes / 100.00
            cal = abono * (interes/360.00) * dias
            res['value']['descuento_calculado'] =cal
        return res
    
    def _format_date(self, date):
        if date:
            campos = date.split('-')
            date = datetime.date(int(campos[0]), int(campos[1]), int(campos[2]))
            return date
    
    def onchange_fecha_pago(self, cr, uid, ids,field,field_name):
        res = {'value':{}}
        now = datetime.date.today()
        if field:
            fecha_pago = self._format_date(field)
            if fecha_pago > now:
                return {'value':{field_name:''},
                        'warning':{'title': "Error", "message": "La fecha de abono/extra/mora no debe ser mayor que la fecha actual"}}
        return res


    _columns = {
                'name': fields.char('Code', size=500),
                'comprobante': fields.char('Comprobante', size=500),
                'date': fields.date('Fecha de Registro'),
                'date_payment': fields.date('Fecha de Pago'),
                'user_id': fields.many2one('res.users','Usuario'),
                'tasa_id': fields.many2one('cyg.tasa.interes','Tasa de Interes'),
                'date_interes': fields.date('Fecha de Interes'),
                'sale_id':fields.many2one('sale.order','Pedido'),
                'partner_id': fields.many2one('res.partner','Cliente'),
                'inmueble_id':fields.many2one('cyg.proyecto_inmueble','Inmuebles'),
                'cuota_id':fields.many2one('cyg.inmueble.cuota','Cuota'),
                'note':fields.text('Observaciones'),
                'amount':fields.float('Valor del Pago'),
                'amount_interes_mora':fields.float('Interes por Mora'),
                'valor_actual_pendiente':fields.float('Valor actual pendiente de la cuota'),
                'state':fields.selection([
                    ('draft','Borrador'),
                    ('done','Validado'),
                    ],'Estado', select=True, readonly=True),
                'type':fields.selection([
                    ('abono','Abono'),
                    ('mora','Mora'),
                    ('extra','Abono Extra'),
                    ],'Tipo', select=True),
                'payment_deposit_line_ids':fields.one2many('cyg.payment.deposit.line','deposit_id','Pagos'),
                'proyecto_id': fields.many2one('cyg.proyecto', 'Proyecto'),
                'etapa_id': fields.many2one('cyg.proyecto_etapa','Etapa'),
                'abono_propuesto':fields.float('Abono Propuesto'),
                'tasa_interes':fields.float('Tasa de Interés por dsct.%', help="Valores entre 0 y 100"),
                'dias_anticipados':fields.integer('Dias anticipados'),
                'descuento_calculado':fields.float('Descuento Calculado'),
                
               }
    _defaults = {  
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'date_payment': lambda *a: time.strftime('%Y-%m-%d'),
        'state':'draft',
        'user_id':lambda self, cr, uid, ctx: uid,
        'name': lambda obj, cr, uid, context: '/',
        'type': _get_type,
        }
cyg_payment_deposit()

class cyg_payment_deposit_line(osv.Model):
    _name ='cyg.payment.deposit.line'
    _description = 'Linea de Abonos y Cuotas'
    _columns = {
                'name':fields.char('Code', size=64),
                'deposit_id':fields.many2one('cyg.payment.deposit','Pago', ondelete='cascade'),
                'comprobante': fields.char('Comprobante', size=500),
                'cuota_id':fields.many2one('cyg.inmueble.cuota','Cuota'),
                'fecha':fields.date('Fecha Pago/Abono/Extra'),
                'valor_cuota':fields.float('Valor Cuota'),
                'valor_mora':fields.float('Valor Interes Mora'),
                'valor_extra':fields.float('Valor Extra'),
                'valor_pendiente_cuota':fields.float('Valor Pendiente Cuota'),
                'valor_pendiente_mora':fields.float('Valor Pendiente Mora'),
                'amount':fields.float('Valor Descuento / Mora / Extra'),
                #'amount_interes':fields.float('Valor recaudado por Mora'),
                'type':fields.selection([
                    ('abono','Abono'),
                    ('mora','Mora'),
                    ('extra','Extra'),
                    ],'Tipo', select=True),
                'state': fields.selection([ ('draft', 'Borrador'),
                                            ('cancel', 'Cancelada'),
                                            ('done', 'Pagada'),
                                            ], 'Estado', readonly=True,select=True),
                
                }
cyg_payment_deposit_line()
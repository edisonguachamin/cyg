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
from openerp.tools.translate import _

class cyg_broker_payment(osv.osv):
    _name = 'cyg.broker.payment'
    _description = 'Clase se genera los objetos de pagos de broker'
    
    def attachment_tree_view(self, cr, uid, ids, context):
        """ View a list of projects attachments """
        domain = [
            ('res_model', '=', 'cyg.broker.payment'),
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
        broker_obj = self.pool.get('cyg.broker')
        payment_line_obj = self.pool.get('cyg.broker.payment.line')
        cur_obj = self.pool.get('res.currency')
        cur = cur_obj.browse(cr, uid, 3)
        
        for item in self.browse(cr, uid, ids):
            monto = item.amount
            saldo = 0.00
            sald2 = 0.00
            lc = []
            type =item.type
            residual = 0.00
            broker_id = item.type == 'cliente' and item.broker_cliente_id or item.broker_reasegurador_id
            print 'broker_id',broker_id
            if not monto:
                break
            if broker_id:
                if type == 'cliente' and monto > broker_id.amount_pending_cliente:
                    diff = monto - broker_id.amount_pending_cliente
                    raise osv.except_osv(('Aviso !'), (u'El monto de pago supera el valor pendiente en '+str(diff)+' revise el valor gracias!'))
                if type == 'reasegurador' and monto > broker_id.amount_pending_reasegurador:
                    diff = monto - broker_id.amount_pending_reasegurador
                    raise osv.except_osv(('Aviso !'), (u'El monto de pago supera el valor pendiente en '+str(diff)+' revise el valor gracias!'))
                    
                if type == 'cliente' and monto <= broker_id.amount_pending_cliente:
                    residual = broker_id.amount_pending_cliente-monto
                    broker_obj.write(cr, uid,[broker_id.id],{'amount_pending_cliente':broker_id.amount_pending_cliente-monto,
                                                             'amount_paid_cliente':broker_id.amount_total_cliente - residual})
                if type == 'reasegurador' and monto <= broker_id.amount_pending_reasegurador:
                    residual = broker_id.amount_pending_reasegurador-monto
                    broker_obj.write(cr, uid,[broker_id.id],{'amount_pending_reasegurador':broker_id.amount_pending_reasegurador-monto,
                                                             'amount_paid_reasegurador':broker_id.amount_total_reasegurador - residual})
                #cuotas_ids = cuota_obj.search(cr, uid, [('state','=','done'),('sale_id','=',sale_id.id)],order='cuota asc')
                #print 'cuotas_ids', cuotas_ids
                if type == 'reasegurador':
                    sql = "select id from cyg_broker_cuota_reasegurador where broker_id = "+str(broker_id.id)+' order by date_payment, numero asc'
                    cuota_obj = self.pool.get('cyg.broker.cuota.reasegurador')
                else:
                    sql = "select id from cyg_broker_cuota_cliente where broker_id = "+str(broker_id.id)+' order by date_payment, numero asc'
                    cuota_obj = self.pool.get('cyg.broker.cuota.cliente')
                cr.execute(sql)
                result = cr.fetchall()
                #print 'result', result
                cuotas_ids = [aux[0] for aux in result]
                #print '*******', cuotas_ids
                for line in cuota_obj.browse(cr, uid,cuotas_ids):
                    if line.state == 'done':
                        #print 'monto entrada', monto
                        saldo = cur_obj.round(cr, uid, cur, monto - line.pendiente)
                        monto = saldo
                        if type == 'cliente':
                            val = {'name':line.name,
                                   'cuota':line.numero,
                                   'payment_id':item.id,
                                   'cuota_id':line.id,
                                   'valor_cuota_cliente':line.valor,
                                   'valor_pagado_cliente':line.pendiente,
                                   'valor_pendiente_cliente':0.00,
                                   'state':'paid',}
                        else:
                            val = {'name':line.name,
                                   'cuota':line.numero,
                                   'payment_id':item.id,
                                   'cuota_id':line.id,
                                   'valor_cuota_reasegurador':line.valor,
                                    'valor_pagado_reasegurador':line.pendiente,
                                    'valor_pendiente_reasegurador':0.00,
                                    'state':'paid',
                                }
                        if saldo > 0:
                            cuota_obj.write(cr, uid, [line.id],{'comprobante':item.comprobante,
                                                                'pagado':line.pendiente,
                                                                'pendiente':0.00,
                                                                'state':'paid',
                                                                'fecha_pago':item.date_payment, 
                                                                'bank_id': item.bank_id and item.bank_id.id or False})
                            payment_line_obj.create(cr,uid,val)
                            continue
                        if saldo < 0:
                            valor = line.pendiente + saldo
                            #print 'line.cliente + saldo', valor
                            if type == 'cliente':
                                val.update({'valor_pagado_cliente':valor,
                                            'valor_pendiente_cliente':-saldo,
                                            'state':'done',
                                            })
                            else:
                                val.update({'valor_pagado_reasegurador':valor,
                                            'valor_pendiente_reasegurador':-saldo,
                                            'state':'done',
                                            })
                            
                            cuota_obj.write(cr, uid, [line.id],{'comprobante':item.comprobante,
                                                                'pagado': valor,
                                                                'pendiente':-saldo,
                                                                'fecha_pago':item.date_payment, 
                                                                'bank_id': item.bank_id and item.bank_id.id or False}) 
                            payment_line_obj.create(cr,uid,val)
                            break
                        else:#igual a cero
                            #print 'igual a cero'
                            cuota_obj.write(cr, uid, [line.id],{'comprobante':item.comprobante,
                                                                'pagado':line.pendiente,
                                                                'pendiente':0.00,
                                                                'state':'paid',
                                                                'fecha_pago':item.date_payment,
                                                                'bank_id': item.bank_id and item.bank_id.id or False})
                            payment_line_obj.create(cr,uid,val)
                            break
                        
            #if not residual:
                #broker_obj.write(cr, uid,[broker_id.id],{'state':'paid'})    
            self.write(cr,uid, [item.id],{'state':'done'})        
        return True
    
    
    
    def create(self, cr, uid, vals, context={}):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cyg.broker.payment') or '/'
         
        res_id = super(cyg_broker_payment, self).create(cr, uid, vals, context)
        return res_id
    
    def unlink(self, cr, uid, ids, context=None):
        #TODO: process before delete resource
        list = []
        for item in self.browse(cr, uid, ids):
            if item.state != 'draft':
                raise osv.except_osv(('Aviso !'), (u'No se permite borrar un pago en estado validado'))
            else:
                list.append(item.id)
        res = super(cyg_broker_payment, self).unlink(cr, uid, list, context)
        return res 
    
    def onchange_banco(self,cr, uid,ids, field_name):
        res = {}
        bank_obj = self.pool.get('res.partner.bank')
        bancos = []
        if field_name:
             info = bank_obj.browse(cr, uid, field_name)
             res['nro_cuenta'] = info.acc_number or '/'
             
        return {'value':res}
    
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
                'broker_cliente_id':fields.many2one('cyg.broker','Broker'),
                'broker_reasegurador_id':fields.many2one('cyg.broker','Broker'),
                'comprobante': fields.char('Comprobante', size=500),
                'date': fields.date('Fecha de Registro'),
                'date_payment': fields.date('Fecha de Pago'),
                'user_id': fields.many2one('res.users','Usuario'),
                'bank_id': fields.many2one('res.partner.bank','Banco'),
                'partner_id': fields.many2one('res.partner','Cliente'),
                'note':fields.text('Observaciones'),
                'amount':fields.float('Valor del Pago'),
                'pendiente':fields.float('Valor Pendiente'),
                'mora':fields.float('Valor Mora'),
                'state':fields.selection([
                    ('draft','Borrador'),
                    ('done','Validado'),
                    ],'Estado', select=True, readonly=True),
                #'type_id':fields.many2one('cyg.broker.payment.type','Tipo de Pago'),
                'type_payment':fields.selection([
                    ('efectivo','Efectivo'),
                    ('banco','Banco'),
                    ],'Tipo de Pago', select=True),
                'type':fields.selection([
                    ('cliente','Cliente'),
                    ('reasegurador','Reasegurador'),
                    ],'Tipo de Pago', select=True),
                'payment_lines_ids':fields.one2many('cyg.broker.payment.line','payment_id','Lineas de Pagos'),
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
cyg_broker_payment()

class cyg_broker_payment_line(osv.Model):
    _name ='cyg.broker.payment.line'
    _description = 'Broker Lineas de Pago'
    _columns = {
                'name':fields.char('Code', size=64),
                'cuota':fields.char('Cuota', size=64),
                'payment_id':fields.many2one('cyg.broker.payment','Pago'),
                'cuota_cliente_id':fields.many2one('cyg.broker.cuota.cliente','Cuota Cliente'),
                'cuota_reasegurador_id':fields.many2one('cyg.broker.cuota.reasegurador','Cuota Reasegurador'),
                'fecha':fields.date('Fecha de Vencimiento'),
                'valor_cuota_cliente':fields.float('Valor Cuota Cliente'),
                'valor_pagado_cliente':fields.float('Valor Pagado Cliente'),
                'valor_pendiente_cliente':fields.float('Valor Pendiente Cliente'),
                'valor_cuota_reasegurador':fields.float('Valor Cuota Cliente'),
                'valor_pagado_reasegurador':fields.float('Valor Pagado Reasegurador'),
                'valor_pendiente_reasegurador':fields.float('Valor Pendiente Reasegurador'),
                
                'state': fields.selection([ ('draft', 'Borrador'),
                                            ('cancel', 'Cancelada'),
                                            ('done', 'Pendiente'),
                                            ('paid', 'Pagada'),
                                            ], 'Estado', readonly=True,select=True),
                
                }
cyg_broker_payment_line()   

class cyg_broker(osv.osv):
    _inherit = 'cyg.broker' 
    #Do not touch _name it must be same as _inherit
    #_name = 'cyg.broker' cr
    
    def broker_pay_cliente(self, cr, uid, ids, context=None):
        if not ids: return []
        bank_id = False
        nro_cuenta = False
        
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'cyg_broker', 'view_cyg_broker_payment_form')

        broker = self.browse(cr, uid, ids[0], context=context)
                
        return {
            'name':_("Pago Broker Cliente"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'cyg.broker.payment',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_amount': 0.00,
                'default_type':'cliente',
                'default_reference': broker.name,
                'close_after_process': True,
                'default_broker_cliente_id':broker.id,
            }
        }
    
    def broker_pay_reasegurador(self, cr, uid, ids, context=None):
        if not ids: return []
        bank_id = False
        nro_cuenta = False
        
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'cyg_broker', 'view_cyg_broker_payment_form')

        broker = self.browse(cr, uid, ids[0], context=context)
                
        return {
            'name':_("Pago Broker Reasegurador"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'cyg.broker.payment',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_amount': 0.00,
                'default_type':'reasegurador',
                'default_reference': broker.name,
                'close_after_process': True,
                'default_broker_reasegurador_id':broker.id,
            }
        }
        
    _columns = {
                'payments_lines_cliente':fields.one2many('cyg.broker.payment','broker_cliente_id','Pagos Cliente'),
                'payments_lines_reaseguro':fields.one2many('cyg.broker.payment','broker_reasegurador_id','Pagos Reasegurador'),
                
                }
    

cyg_broker()

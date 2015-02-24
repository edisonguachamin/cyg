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
from dateutil.relativedelta import *

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import re
from lxml.html.builder import INS

from utils import cambiarTildes

class cyg_broker(osv.osv):
    _name= 'cyg.broker'
    _description = 'Broker'
    
    def onchange_ramo(self, cr, uid, ids, field):
        res  = {'value':{}}
        ramo_obj = self.pool.get('cyg.broker.ramo')
        if field:
            ramo_info = ramo_obj.browse(cr,uid,field)
            res['value']['codigo']=ramo_info.code
            res['value']['tipo_id']=False
        return res

    def attachment_tree_view(self, cr, uid, ids, context):
        """ View a list of projects attachments """

        domain = [
            ('res_model', '=', 'cyg.broker'),
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
        
    def _format_date(self, date):
        if date:
            campos = date.split('-')
            date = datetime.date(int(campos[0]), int(campos[1]), int(campos[2]))
            return date
        
    def button_tabla(self, cr, uid, ids,context=None):
        cuota_reasegurador_obj = self.pool.get('cyg.broker.cuota.reasegurador')
        cuota_cliente_obj = self.pool.get('cyg.broker.cuota.cliente')
        prima_neta_reasegurado = prima_neta_reasegurador = 0.00
        for item in self.browse(cr, uid,ids):
            if item.cuotas_reasegurador_ids or item.cuotas_cliente_ids:
                break
            if not item.nro_instalamentos or item.nro_instalamentos < 0:
                raise osv.except_osv(('Aviso !'), u'El valor de instalamentos debe ser mayor a 0')
            if item.prima_neta_reasegurador < 0:
                raise osv.except_osv(('Aviso !'), u'El valor del reasegurador (PNR) debe ser mayor a 0')
            
            if item.prima_neta_reasegurado < 0:
                raise osv.except_osv(('Aviso !'), u'El valor del reasegurado (PNC )debe ser mayor a 0')
            
            if item.periodicidad < 0:
                raise osv.except_osv(('Aviso !'), u'La periodicidad debe ser mayor a 0')
            
            if item.prima_neta_reasegurado:
                prima_neta_reasegurado = item.prima_neta_reasegurado
                n = item.nro_instalamentos
                now = self._format_date(item.fecha_inicio_pago)
                valor = item.prima_neta_reasegurado / n
                i=1 
                while n > 0:
                    if i==1:
                        fecha_pago = item.fecha_inicio_pago
                    else:
                        fecha_pago = (now + relativedelta(days=+item.periodicidad)).strftime('%Y-%m-%d')
                    now = self._format_date(fecha_pago)
                    #now = fecha_pago
                    n-=1
                    dict = {'numero':i,
                             'broker_id':item.id,
                             'valor':valor,
                             'pendiente':valor,
                             'date_payment':fecha_pago,
                             'state':'done'}
                    cuota_cliente_obj.create(cr, uid,dict)
                    i+=1
                    
                    
            if item.prima_neta_reasegurador:
                prima_neta_reasegurador = item.prima_neta_reasegurador 
                n = item.nro_instalamentos    
                now = self._format_date(item.fecha_inicio_pago)
                valor = item.prima_neta_reasegurador / n
                i = 1 
                while n > 0:
                    if i==1:
                        fecha_pago = (now + relativedelta(days=+15)).strftime('%Y-%m-%d')
                    else:
                        fecha_pago = (now + relativedelta(days=+item.periodicidad)).strftime('%Y-%m-%d')
                    #now = fecha_pago
                    now = self._format_date(fecha_pago)
                    n-=1
                    dict = {'numero':i,
                            'broker_id':item.id,
                            'valor':valor,
                            'pendiente':valor,
                            'date_payment':fecha_pago,
                            'state':'done'}
                    cuota_reasegurador_obj.create(cr, uid,dict)
                    i+=1
            self.write(cr, uid, [item.id],{'show_buttons':True,'amount_total_cliente':prima_neta_reasegurado,'amount_pending_cliente':prima_neta_reasegurado,
                                            'amount_total_reasegurador':prima_neta_reasegurador,'amount_pending_reasegurador':prima_neta_reasegurador})
                    
        return True
    
    def onchage_fecha_inicio_pago(self, cr, uid,ids,field_name):
        res = {'value':{}}
        #now = datetime.date.today()
        cuota_reasegurador_obj = self.pool.get('cyg.broker.cuota.reasegurador')
        cuota_cliente_obj = self.pool.get('cyg.broker.cuota.cliente')
        lineas = []
        lineas_cliente = []
        if field_name:
            #res['value']['fecha_entrega'] = date
            res['value']['cuotas_reasegurador_ids'] = []
            res['value']['cuotas_cliente_ids'] = []
            res['value']['show_buttons'] = False
            for item in self.browse(cr, uid, ids):
                for line in item.cuotas_reasegurador_ids:
                    lineas.append(line.id)
                for line in item.cuotas_cliente_ids:
                    lineas_cliente.append(line.id)
                cuota_reasegurador_obj.unlink(cr, uid,lineas)
                cuota_cliente_obj.unlink(cr, uid,lineas_cliente)
        return res
    
    def onchage_periodicidad(self, cr, uid,ids,field_name):
        print 'onchage_periodicidad',field_name
        res = {'value':{}}
        #now = datetime.date.today()
        cuota_reasegurador_obj = self.pool.get('cyg.broker.cuota.reasegurador')
        cuota_cliente_obj = self.pool.get('cyg.broker.cuota.cliente')
        lineas = []
        lineas_cliente = []
        if field_name:
            #res['value']['fecha_entrega'] = date
            res['value']['cuotas_reasegurador_ids'] = []
            res['value']['cuotas_cliente_ids'] = []
            res['value']['show_buttons'] = False
            for item in self.browse(cr, uid, ids):
                for line in item.cuotas_reasegurador_ids:
                    lineas.append(line.id)
                for line in item.cuotas_cliente_ids:
                    lineas_cliente.append(line.id)
                cuota_reasegurador_obj.unlink(cr, uid,lineas)
                cuota_cliente_obj.unlink(cr, uid,lineas_cliente)
        return res
    
    def button_sent_aprobacion(self, cr, uid, ids,context=None):
        return self.write(cr, uid, ids, {'state':'sent'})
    
    def button_cancelada(self, cr, uid, ids,context=None):
        return self.write(cr, uid, ids, {'state':'cancel'})
    
    def button_cobertura(self, cr, uid, ids,context=None):
        return self.write(cr, uid, ids, {'state':'coverage'})
    
    def onchange_cobertura(self, cr, uid, ids, field_name):
        res = {'value':{}}
        cobertura_obj = self.pool.get('cyg.broker.cobertura')
        if field_name:
            cobertura_info = cobertura_obj.browse(cr, uid,field_name)
            res['value']['descripcion_cobertura'] = cobertura_info.descripcion
        return res
    
    def _format_datetime(self, date):
        if date:
            fecha = date.split(' ')
            campos = fecha[0].split('-')
            hora =  fecha[1].split(':')
            date = datetime.datetime(int(campos[0]), int(campos[1]), int(campos[2]),int(hora[0]),int(hora[1]),int(hora[2]))
            return date
    
    def onchange_fechas(self, cr, uid, ids,inicial,final):
        res = {'value':{}}
        now = datetime.date.today()
        if final and inicial:
            fecha_inicial = self._format_datetime(inicial)
            fecha_final = self._format_datetime(final)
            
            if fecha_final < fecha_inicial:
                return {'value':{'to_vigencia':''},
                        'warning':{'title': "Error", "message": "La fecha hasta debe ser mayor que la fecha desde"}}
            
        return res
    
    def valida_porcentaje(self,cr, uid, ids,valor, field_name):
        res = {}
        if valor:
            if valor < 0 or valor > 100:
                return {'value':{field_name:0},
                        'warning':{'title': "Error", "message": "El porcentaje debe estar entre 0 y 100"}}
            else:
                return res
    
    def create(self, cr, uid, vals, context={}):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cyg.broker') or '/'
        res_id = super(cyg_broker, self).create(cr, uid, vals, context)
        return res_id
    
    _columns = {
                'name':fields.char('Code', size=500),
                'date':fields.date('Fecha de Creación'),
                'date_sent':fields.date('Fecha de Envió'),
                'date_answer':fields.date('Fecha de Respuesta'),
                'date_sent_cedente':fields.date('Fecha de Envió Cedente'),
                'date_answer_cedente':fields.date('Fecha de Respuesta Cedente'),
                'date_orden':fields.date('Fecha de Orden en Firme'),
                'ramo_id':fields.many2one('cyg.broker.ramo','Ramo'),
                'codigo':fields.char('Codigo', size=500),
                'tipo_id':fields.many2one('cyg.broker.tipo','Tipo'),
                'partner_id':fields.many2one('res.partner','Reasegurado'),
                'reasegurador_ids':fields.one2many('cyg.broker.reasegurador','broker_id','Reasegurador'),
                'asegurado':fields.char('Asegurado', size=5000),
                #'reasegurado_id':fields.many2one('res.partner', 'Reasegurado'),
                'giro':fields.text('Giro del Negocio'),
                'ubicacion':fields.text('Ubicación'),
                'territorio':fields.text('Territorio'),
                'from_vigencia':fields.datetime('Desde'),
                'to_vigencia':fields.datetime('Hasta'),
                'limite_geografico':fields.text('Límite Geográfico'),
                'limite_embarque':fields.text('Límite por Embarque'),
                'exceso_limite_embarque':fields.text('Exceso en Límite por embarque'),
                'trayecto_asegurado':fields.text('Trayecto Asegurado'),
                'medios_transporte':fields.text('Medios de Transporte'),
                'uso_id':fields.many2one('cyg.broker.uso','Usos'),
                'detalle_embarcacion_ids':fields.one2many('cyg.broker.detalle.embarcacion','broker_id','Detalle de embarcaciones'),
                'limite_catastrofico':fields.float('Límite Catastrófico', size=10),
                'exceso_limite':fields.float('Exceso de Límite(USD)'),
                'definiciones_id':fields.many2one('cyg.broker.definiciones','Definiciones'),
                #
                'interes_asegurado':fields.text('Interés Asegurado'),
                'valor_asegurado':fields.float('Valor Asegurado'),
                'asegurado_ids':fields.one2many('cyg.broker.valor.asegurado','broker_id','Valores Asegurados'),
                'valor_asegurable':fields.float('Valores Asegurables'),
                'asegurable_ids':fields.one2many('cyg.broker.valor.asegurable','broker_id','Valores Asegurables'),
                'sublimites':fields.selection([('si','Si'),
                                               ('no','No')],'Sublimites'),
                'cobertura_id':fields.many2one('cyg.broker.cobertura','Cobertura'),
                'descripcion_cobertura':fields.text('Descripción Cobertura'),
                'cobertura_adicional_id':fields.many2one('cyg.broker.cobertura','Cobertura Adicional'),
                'descripcion_cobertura_adicional':fields.text('Descripción Cobertura'),
                'amparo_adicional_id':fields.many2one('cyg.broker.cobertura','Amparo Adicional'),
                'bien_asegurable':fields.text('Bienes Asegurables'),
                'clausula_adicional_id':fields.many2one('cyg.broker.clausula','Clausula Adicional'),
                'aclaraciones':fields.text('Aclaraciones'),
                'pilotos':fields.selection([('si','Si'),
                                               ('no','No')],'Pilotos'),
                'pilotos_ids':fields.one2many('cyg.broker.piloto','broker_id','Pilotos'),
                'naves_ids':fields.one2many('cyg.broker.aeronaves','broker_id','Naves'),
                'exclusion_id':fields.many2one('cyg.broker.exclusiones','Exclusiones'),
                'deducibles':fields.text('Deducibles'),
                #Campo Tabla
                'ley_jurisdiccion':fields.text('Ley y Jurisdicción'),
                #Adjuntar Archivos
                'orden_colocacion':fields.float('Orden de Colocación %'),
                'tasa_reaseguro':fields.float('Tasa Neta de Reaseguro'),
                'nro_instalamentos':fields.integer('Nro de Instalamentos'),
                'prima_neta_reasegurador':fields.float('Prima Neta de Reasegurador (PNR)'),
                'prima_neta_reasegurado':fields.float('Prima Neta de Reasegurado (PNC)'),
                'fecha_inicio_pago':fields.date('Fecha de Inicio de Pago'),
                'garantia_pgo':fields.char('Garantía del Pago', size=5000),
                'sujeto':fields.text('Sujeto a'),
                'informacion':fields.text('Información Adicional'),
                'tercero':fields.selection([('juridico','Jurídico'),
                                            ('natural','Natural')],'Tercero'),
                'limite_aprobacion':fields.date('Fecha Límite Aprobación'),
                'user_id':fields.many2one('res.users','Usuario Responsable'),
                'descripcion_cobertura':fields.text('Descripción'),
                'state':fields.selection([
                    ('draft','Slip'),
                    ('sent','Enviado a Aprobación'),
                    ('cancel','Cancelado'),
                    ('coverage','Nota de Cobertura'),
                    ],'State', select=True, readonly=True),
                'siniestros_ids':fields.one2many('cyg.broker.siniestros','broker_id','Siniestros'),
                'cuotas_reasegurador_ids':fields.one2many('cyg.broker.cuota.reasegurador','broker_id','Tabla de Cuotas de Reasegurador'),
                'cuotas_cliente_ids':fields.one2many('cyg.broker.cuota.cliente','broker_id','Tablas de Cuotas Cliente'),
                'cobertura_ids':fields.one2many('cyg.broker.cobertura.line','broker_id','Coberturas'),
                'cobertura_adicional_ids':fields.one2many('cyg.broker.cobertura.adicional.line','broker_id','Coberturas Adicional'),
                'amparo_adicional_ids':fields.one2many('cyg.broker.amparo.adicional.line','broker_id','Amparo Adicional'),
                'exclusiones_ids':fields.one2many('cyg.broker.exclusion','broker_id','Exclusiones'),
                'periodicidad':fields.integer('Periodicidad de pago Cliente (días)',size=3),
                'amount_total_cliente':fields.float('Total Cliente',digits=(16,2)),
                'amount_total_reasegurador':fields.float('Total Reasegurador',digits=(16,2)),
                'amount_pending_cliente':fields.float('Pendiente Cliente',digits=(16,2)),
                'amount_pending_reasegurador':fields.float('Pendiente Reasegurador',digits=(16,2)),
                'amount_paid_cliente':fields.float('Pagado Cliente',digits=(16,2)),
                'amount_paid_reasegurador':fields.float('Pagado Reasegurador',digits=(16,2)),
                'show_buttons':fields.boolean('Mostrar')
                }
    _defaults = {  
        'state':'draft',
        'name': lambda obj, cr, uid, context: '/',
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'ramo_id':lambda self,cr,uid,c: self.pool.get('cyg.broker.ramo').search(cr, uid, [('name','=','Casco Aereo')], context=c)[0],
        'user_id':lambda self, cr, uid, ctx: uid,
        'periodicidad':30,
        'ley_jurisdiccion':"""Este reaseguro será gobernado por y construido de acuerdo con la ley de Ecuador y cada parte acuerda referir a la jurisdicción exclusiva de las cortes de Ecuador a menos que ambas partes acuerden referir el caso a arbitraje""",
        'show_buttons':False
        }
    
    _sql_constraints = [('name_uniq', 'unique (name)', 'Existe un broker con el mismo nombre !'),      ]
    
cyg_broker()

class cyg_broker_exclusion(osv.osv):
    _name= 'cyg.broker.exclusion'
    _description = 'Exclusiones Broker'
    _columns = {
                'name':fields.char('Exclusión', size=500),
                'broker_id':fields.many2one('cyg.broker','Broker'),
                }
cyg_broker_exclusion()

class cyg_broker_detalle_embarcacion(osv.osv):
    _name= 'cyg.broker.detalle.embarcacion'
    _description = 'Detalle de Embarcaciones'
    _columns = {
                'name':fields.char('Embarcación', size=500),
                'broker_id':fields.many2one('cyg.broker','Broker'),
                }
cyg_broker_detalle_embarcacion()

class cyg_broker_valor_asegurado(osv.osv):
    _name= 'cyg.broker.valor.asegurado'
    _description = 'Valores Asegurado Broker'
    _columns = {
                'name':fields.char('Descripción', size=500),
                'broker_id':fields.many2one('cyg.broker','Broker'),
                'valor':fields.float('Valor Asegurado(USD)'),
                }
cyg_broker_valor_asegurado()

class cyg_broker_valor_asegurable(osv.osv):
    _name= 'cyg.broker.valor.asegurable'
    _description = 'Valores Asegurable Broker'
    _columns = {
                'name':fields.char('Descripción', size=500),
                'broker_id':fields.many2one('cyg.broker','Broker'),
                'valor':fields.float('Valor Asegurable(USD)'),
                }
cyg_broker_valor_asegurable()


class cyg_broker_reasegurador(osv.osv):
    _name= 'cyg.broker.reasegurador'
    _description = 'Reasegurador Broker'
    _columns = {
                'name':fields.char('Nombre', size=500),
                'broker_id':fields.many2one('cyg.broker','Broker'),
                'partner_id':fields.many2one('res.partner','Reasegurador'),
                'prima_neta':fields.float('Prima neta reasegurador'),
                'observacion':fields.char('Observaciones', size=5000),
                'date_sent':fields.date('Fecha de Envió'),
                'date':fields.date('Fecha de Respuesta')
                }
cyg_broker_reasegurador()


class cyg_broker_cuota_reasegurador(osv.osv):
    _name= 'cyg.broker.cuota.reasegurador'
    _description = 'Pago Reasegurador Broker'
    
    def create(self, cr, uid, vals, context={}):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cyg.broker.cuota.reasegurador') or '/'
         
        res_id = super(cyg_broker_cuota_reasegurador, self).create(cr, uid, vals, context)
        return res_id
    
    _columns = {
                'name':fields.char('Code', size=500),
                'numero':fields.char('Nro', size=500),
                'broker_id':fields.many2one('cyg.broker','Broker'),
                'date_payment':fields.date('Fecha de Pago'),
                'valor':fields.float('Valor (USD)'),
                'concepto':fields.text('Concepto'),
                'pendiente':fields.float('Valor Pendiente(USD)'),
                'pagado':fields.float('Valor Pagado(USD)'),
                'state':fields.selection([
                    ('done','Abierta'),
                    ('paid','Pagada'),
                    ],    'State', select=True, readonly=True),
                }
    _defaults = {  
        'name': '/',
        'state':'done'
        }
cyg_broker_cuota_reasegurador()

class cyg_broker_cuota_cliente(osv.osv):
    _name= 'cyg.broker.cuota.cliente'
    _description = 'Pago Cliente Broker'
    
    def create(self, cr, uid, vals, context={}):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cyg.broker.cuota.cliente') or '/'
         
        res_id = super(cyg_broker_cuota_cliente, self).create(cr, uid, vals, context)
        return res_id
    _columns = {
                'name':fields.char('Code', size=500),
                'numero':fields.char('Nro', size=500),
                'broker_id':fields.many2one('cyg.broker','Broker'),
                'date_payment':fields.date('Fecha de Pago'),
                'concepto':fields.text('Concepto'),
                'valor':fields.float('Valor (USD)'),
                'pagado':fields.float('Valor Pagado(USD)'),
                'pendiente':fields.float('Valor Pendiente(USD)'),
                'state':fields.selection([
                    ('done','Abierta'),
                    ('paid','Pagada'),
                    ],    'State', select=True, readonly=True),
                }
    
    _defaults = {  
        'name': '/',
        'state':'done'
        }
    
cyg_broker_cuota_cliente()

class cyg_broker_piloto(osv.osv):
    _name= 'cyg.broker.piloto'
    _description = 'Pilotos Broker'
    _columns = {
                'name':fields.char('Nombre', size=500),
                'broker_id':fields.many2one('cyg.broker','Broker'),
                'edad':fields.char('Edad', size=500),
                'experiencia':fields.char('Experiencia', size=500),
                'marca':fields.char('Marca', size=500),
                'modelo':fields.char('Modelo', size=500),
                
                }
cyg_broker_piloto()

class cyg_broker_aeronaves(osv.osv):
    _name= 'cyg.broker.aeronaves'
    _description = 'Aeronaves Broker'
    _columns = {
                'name':fields.char('Matrícula', size=500),
                'broker_id':fields.many2one('cyg.broker','Broker'),
                'marca':fields.char('Marca', size=500),
                'modelo':fields.char('Modelo', size=500),
                'anio':fields.integer('Año', size=4),
                'pasajeros':fields.char('Pasajeros', size=500),
                'tripulantes':fields.char('Tripulantes', size=500),
                'valor':fields.float('Valor (USD)'),
                }
cyg_broker_aeronaves()

class cyg_broker_siniestros(osv.osv):
    _name= 'cyg.broker.siniestros'
    _description = 'Siniestros Broker'
    _columns = {
                'name':fields.char('Nombre del Siniestro', size=500),
                'broker_id':fields.many2one('cyg.broker','Broker'),
                'descripcion':fields.char('Descripción', size=5000),
                'date':fields.date('Fecha de Creación'),
                }
    _defaults = {  
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        }
cyg_broker_siniestros()

class cyg_broker_cobertura_line(osv.osv):
    _name= 'cyg.broker.cobertura.line'
    _description = 'Cobertura Line'
    
    
    def onchange_cobertura(self, cr, uid, ids, field):
        res  = {'value':{}}
        cobertura_obj = self.pool.get('cyg.broker.cobertura')
        if field:
            cobertura_info = cobertura_obj.browse(cr,uid,field)
            res['value']['descripcion']=cobertura_info.descripcion
            
        return res
    
    _columns = {
                'name':fields.char('Nombre del Siniestro', size=500),
                'broker_id':fields.many2one('cyg.broker','Broker'),
                'cobertura_id':fields.many2one('cyg.broker.cobertura','Cobertura'),
                'descripcion':fields.char('Descripción', size=5000),
                'date':fields.date('Fecha de Creación'),
                }
    _defaults = {  
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        }
cyg_broker_cobertura_line()

class cyg_broker_cobertura_adicional_line(osv.osv):
    _name= 'cyg.broker.cobertura.adicional.line'
    _description = 'Cobertura Line'
    
    
    def onchange_cobertura(self, cr, uid, ids, field):
        res  = {'value':{}}
        cobertura_obj = self.pool.get('cyg.broker.cobertura.adicional')
        if field:
            cobertura_info = cobertura_obj.browse(cr,uid,field)
            res['value']['descripcion']=cobertura_info.descripcion
            
        return res
    
    _columns = {
                'name':fields.char('Nombre del Siniestro', size=500),
                'broker_id':fields.many2one('cyg.broker','Broker'),
                #'grupo_id':fields.many2one('cyg.broker.ramo','Grupo'),
                'grupo_adicional_id':fields.many2one('cyg.broker.grupo.cobertura.adicional','Grupo'),
                'cobertura_id':fields.many2one('cyg.broker.cobertura.adicional','Cobertura'),
                'limite':fields.float('Límite (USD)', size=5000),
                'plazo':fields.integer('Plazo (días)', size=3),
                'por_evento':fields.selection([('si','Si'),
                                               ('no','No')],'Por Evento'),
                'date':fields.date('Fecha de Creación'),
                'descripcion':fields.text('Descripción'),
                }
    _defaults = {  
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        }
cyg_broker_cobertura_adicional_line()

class cyg_broker_amparo_adicional_line(osv.osv):
    _name= 'cyg.broker.amparo.adicional.line'
    _description = 'Amparo Adicional Line'
    
    
    def onchange_amparo(self, cr, uid, ids, field):
        res  = {'value':{}}
        amparo_obj = self.pool.get('cyg.broker.amparo.adicional')
        if field:
            amparo_info = amparo_obj.browse(cr,uid,field)
            res['value']['descripcion']=amparo_info.descripcion
            
        return res
    
    _columns = {
                'name':fields.char('Nombre del Siniestro', size=500),
                'broker_id':fields.many2one('cyg.broker','Broker'),
                'grupo_adicional_id':fields.many2one('cyg.broker.grupo.amparo.adicional','Grupo'),
                'amparo_id':fields.many2one('cyg.broker.amparo.adicional','Amparo'),
                'limite':fields.float('Límite (USD)', size=5000),
                'plazo':fields.integer('Plazo (días)', size=3),
                'por_evento':fields.selection([('si','Si'),
                                               ('no','No')],'Por Evento'),
                'date':fields.date('Fecha de Creación'),
                'descripcion':fields.text('Descripción'),
                }
    _defaults = {  
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        }
cyg_broker_amparo_adicional_line()
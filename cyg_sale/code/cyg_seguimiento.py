# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today
#    CyG xxxx
#    @autor: Jonathan Finlay <jfinlay@riseup.net>
#    @date: 03-06-2014
#    @last_modified: 03-06-2014
#
##############################################################################
from openerp.osv import fields, osv
import time

class proyecto_inmueble(osv.Model):
    #_name = 'sale.order'
    _inherit = 'cyg.proyecto_inmueble'
    _columns = {
                'seguimiento_inmueble_ids':fields.one2many('cyg.inmueble.seguimiento','inmueble_id','Seguimiento de Entrega'),
                'comisiones_ids':fields.one2many('cyg.historico_comisiones_inmueble','inmueble_id','Comisiones')
                }
proyecto_inmueble()

class seguimiento(osv.osv):
    """Clase para la administración de lotes de terreno"""
    _name = 'cyg.inmueble.seguimiento'
    _description = "Clase para la administración de lotes de terreno"
    
    
    def button_open(self, cr, uid, ids, context={}):
        for item in self.browse(cr, uid, ids):
            self.write(cr,uid, [item.id],{'state':'open'})
        return True
    
    def button_close(self, cr, uid, ids, context={}):
        for item in self.browse(cr, uid, ids):
            self.write(cr,uid, [item.id],{'state':'close'})
        return True
    
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
                res['sale_id'] = info.sale_id and info.sale_id.id
                res['etapa_id2'] = info.sale_id and info.sale_id.etapa_id.id
                res['proyecto_id'] = info.sale_id and info.sale_id.proyecto_id.id
                domain['sale_id'] = [('id','in',inmueble_ids),('state','=','vendido')]
        else:
            res['sale_id'] = False
            domain['sale_id'] = [('partner_id','=',partner_id),('state','=','vendido')]
        #print 'domain', domain
        return {'value':res,'domain': domain}
    
    def create(self, cr, uid, vals, context={}):
        #print 'vals',vals
        #print 'context',context
        inmueble_obj = self.pool.get('cyg.proyecto_inmueble')
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cyg.inmueble.seguimiento') or '/'
        if vals.get('inmueble_id'):
            info = inmueble_obj.browse(cr, uid, vals.get('inmueble_id'))
            vals['partner_id'] = info.partner_id and info.partner_id.id 
            vals['sale_id'] = info.sale_id and info.sale_id.id
            
        vals['state'] = 'open'
        res_id = super(seguimiento, self).create(cr, uid, vals, context)
        return res_id

    _columns = {
                'name':fields.char('Nro de Orden', size=500),
                'inmueble_id':fields.many2one('cyg.proyecto_inmueble','Inmueble'),
                'etapa_id2': fields.related('inmueble_id', 'etapa_id', type="many2one", relation='cyg.proyecto_etapa',string="Etapa", store=True, readonly=True),
                'proyecto_id': fields.related('inmueble_id', 'proyecto_id', type="many2one", relation='cyg.proyecto',string="Proyecto", store=True, readonly=True),
                'partner_id':fields.many2one('res.partner','Cliente'),
                'sale_id':fields.many2one('sale.order','Orden'),
                'fecha_inicial':fields.date('Fecha de Apertura'),
                'fecha_final':fields.date('Fecha de Cierre'),
                'seguimiento_lines_ids':fields.one2many('cyg.inmueble.seguimiento_lines','seguimiento_id','Seguimientos'),
                'fisuras':fields.boolean('Fisuras'),
                'obs_1':fields.text('Observacion'),
                'albanileria':fields.boolean('Albanileria'),
                'obs_2':fields.text('Observacion'),
                'aluminio':fields.boolean('Aluminio & Vidrio'),
                'obs_3':fields.text('Observacion'),
                'cubierta':fields.boolean('Cubierta'),
                'obs_4':fields.text('Observacion'),
                'instalacion_electrica':fields.boolean('Instalacion Electrica'),
                'obs_5':fields.text('Observacion'),
                'gas_centralizado':fields.boolean('Gas Centralizado'),
                'obs_6':fields.text('Observacion'),
                'jardineria':fields.boolean('Jardineria'),
                'obs_7':fields.text('Observacion'),
                'mesones':fields.boolean('Mesones'),
                'obs_8':fields.text('Observacion'),
                'ceramica':fields.boolean('Ceramica'),
                'obs_9':fields.text('Observacion'),
                'observaciones':fields.boolean('Observaciones'),
                'obs_10':fields.text('Observacion'),
                'tuberia_fria':fields.boolean('Tuberia Agua Fria'),
                'obs_11':fields.text('Observacion'),
                'tuberia_caliente':fields.boolean('Tuberia Agua Caliente'),
                'obs_12':fields.text('Observacion'),
                'cocina':fields.boolean('Cocina'),
                'obs_13':fields.text('Observacion'),
                'dormintorio':fields.boolean('Dormitorio'),
                'obs_14':fields.text('Observacion'),
                'banio':fields.boolean('Baño'),
                'obs_15':fields.text('Observacion'),
                'puertas':fields.boolean('Puerta'),
                'obs_16':fields.text('Observacion'),
                'barrederas':fields.boolean('Barrederas'),
                'obs_17':fields.text('Observacion'),
                'madera':fields.boolean('Madera'),
                'obs_18':fields.text('Observacion'),
                'piso_ceramica':fields.boolean('Piso Ceramica'),
                'obs_19':fields.text('Observacion'),
                'alfombra':fields.boolean('Alfombra'),
                'obs_20':fields.text('Observacion'),
                'pintura_interiores':fields.boolean('Pintura Interiores'),
                'obs_21':fields.text('Observacion'),
                'pintura_exteriores':fields.boolean('Pintura Exteriores'),
                'obs_22':fields.text('Observacion'),
                'humedad_paredes':fields.boolean('Paredes'),
                'obs_23':fields.text('Observacion'),
                'humedad_techos':fields.boolean('Techos'),
                'obs_24':fields.text('Observacion'),
                'humedad_pisos':fields.boolean('Pisos'),
                'obs_25':fields.text('Observacion'),
                'state':fields.selection([('draft','Borrador'),
                    ('open','Abierto'),
                    ('close','Cerrado'),
                    ],'Estado', select=True, readonly=True),
                
                }
    _defaults = {  
        'fecha_inicial': lambda *a: time.strftime('%Y-%m-%d'),
        'state':'draft',
        'name': lambda obj, cr, uid, context: '/',
        }
seguimiento()

class seguimiento_lineas(osv.osv):
    """Clase para la administración de lotes de terreno"""
    _name = 'cyg.inmueble.seguimiento_lines'
    _description = "Clase para la administración de lotes de terreno"
    _columns = {
                'name':fields.char('Nombre', size=500),
                'seguimiento_id':fields.many2one('cyg.inmueble.seguimiento','Seguimiento'),
                'fecha_inicial':fields.date('Fecha de Apertura'),
                'fecha_final':fields.date('Fecha de Cierre'),
                'state':fields.selection([
                    ('draft','Borrador'),   
                    ('open','Abierta'),
                    ('close','Cerrada'),
                   ], 'Estado', select=True),
                'tipo_id':fields.many2one('cyg.seguimiento_tipo','Tipo'),
                'detalle_id':fields.text('Detalle'),
                'note':fields.text('Observacion'),
                'aplican_garantias':fields.selection([('si','Si'),('no','No'),
                                                     ],'Aplican Garantias'),
                'autoriza_id':fields.many2one('res.users','Autoriza'),
                
                
                }
    _defaults = {  
        'fecha_inicial': lambda *a: time.strftime('%Y-%m-%d'),
        'state':'draft'
        }
seguimiento_lineas()
# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright (C) 2014-Today
#    CyG xxxx
#    @author: Jonathan Finlay <jfinlay@riseup.net>
#    @date: 03-06-2014
#    @last_modified: 03-06-2014
#
##############################################################################
from openerp.osv import fields, osv
import datetime
import time


class transferencia_dominio(osv.osv):
    """Clase para la administración de las transferencias de dominio"""
    _name = 'cyg.transferencia_dominio'
    _description = "Clase para la administración de transferencias de dominio"

    def onchange_proyecto(self, cr, uid, id, proyecto_id, context=None):
        country_id = False
        state_id = False
        city_id = False
        if proyecto_id:
            proyecto = self.pool.get('cyg.proyecto').browse(cr, uid, proyecto_id, context=context)
            country_id = proyecto.country_id.id
            state_id = proyecto.state_id.id
            city_id = proyecto.city_id.id
        return {'value': {'country_id': country_id, 'state_id': state_id, 'city_id': city_id}}

    def onchange_valor_prestamo(self, cr, uid, id, valor_prestamo, inmueble_id, context=None):
        res = {}
        precio_inmueble = self.pool.get('cyg.proyecto_inmueble').browse(cr, uid, inmueble_id).precio_actual
        if valor_prestamo > precio_inmueble:
            res['warning'] = {'title': 'Error', 'message': 'El valor del prestamo no puede ser mayor al valor del inmueble'}
            res['value'] = {'valor_prestamo': 0.0}
        return res

    def attachment_tree_view(self, cr, uid, ids, context):
        """ View a list of projects attachments """

        domain = [
            ('res_model', '=', 'cyg.transferencia_dominio'),
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
        
    def on_change_comprador_id(self, cr, uid, ids,field_name):
        res = {}
        patner_obj = self.pool.get('res.partner')
        if field_name:
            info = patner_obj.browse(cr, uid,field_name)
            res['conyuge_id'] = info.conyuge_id and info.conyuge_id.id or False 
            res['separacion_bienes'] = info.separacion_bienes
            
        return {'value':res}
    
    _columns = {
        'proyecto_id': fields.many2one('cyg.proyecto', 'Proyecto'),
        'recepcion_carpeta': fields.date('Fecha de recepción carpeta'),
        'fecha_asignacion_tramite': fields.date('Fecha de asignación tramite'),
        'fecha_minuta': fields.date('Fecha de minuta'),
        'fecha_estimada_desembolso': fields.date('Fecha estimada de desembolso'),
        'fecha_desembolso': fields.date('Fecha real de desembolso'),
        'fecha_entrega': fields.date('Fecha de entrega a banco'),
        #Cambio de Aumentar fecha
        'fecha_factura': fields.date('Fecha de factura'),
        'estudio_juridico_id': fields.many2one('res.partner', 'Estudio Jurídico'),
        'constructor_id': fields.many2one('res.partner', 'Constructor'),
        'comprador_id': fields.many2one('res.partner', 'Comprador'),
        'notaria': fields.integer('Notaría'),
        'country_id': fields.many2one('res.country', 'Pais'),
        'state_id': fields.many2one('res.country.state', 'Provincia'),
        'city_id': fields.many2one('res.country.city', 'Cantón'),
        'responsable': fields.char('Responsable',
                                   size=128),
        'estado_civil': fields.related('comprador_id', 'estado_civil',
                                       type='char',
                                       relation='res.partner',
                                       string='Estado civil',
                                       store=False,
                                       readonly=True),
#         'conyuge_id': fields.related('comprador_id', 'conyuge_id',
#                                      type='many2one',
#                                      relation='res.partner',
#                                      string='Conyuge',
#                                      store=False,
#                                      readonly=True),
        'conyuge_id': fields.many2one('res.partner', 'Conyuge'),
        'separacion_bienes': fields.related('comprador_id',
                                            'separacion_bienes',
                                            type='boolean',
                                            relation='res.partner',
                                            string='Separación de bienes',
                                            store=False,
                                            readonly=True),
        'apoderado': fields.boolean('Tiene apoderado'),
        'apoderado_id': fields.many2one('res.partner', 'Apoderado'),
        'fecha_poder': fields.date('Fecha poder'),
        'notaria_apoderado': fields.char('Notaría', size=64),
        'fecha_vigencia': fields.date('Fecha vigencia poder'),
        'inmueble_id': fields.many2one('cyg.proyecto_inmueble', 'Inmueble'),
        'banco_prestamista_id': fields.many2one('res.bank',
                                                'Banco prestamista'),
        'valor_prestamo': fields.float('Valor prestamo'),
        'producto_prestamo': fields.selection([
                                                  ('vivienda_terminada', 'Vivienda terminada'),
                                                  ('terreno', 'Terreno'),
                                                  ('compra_inmueble', 'Compra de inmueble'),
                                                  ('remodelacion_ampliacion', 'Remodelacion / ampliacion'),
                                                  ('hipoteca', 'Vivienda hipotecada'),
                                                  ('sustitucion_hipoteca', 'Sustitucion hipoteca'),
                                                  ('construccion', 'Construcción'),
                                              ],
                                              'Producto prestamo'),
        'nombre_ejecutivo': fields.char('Nombre del ejecutivo',
                                        size=128),
        'email_ejecutivo': fields.char('Correo-e ejecutivo', size=64),
        'fecha_emision': fields.date('Fecha de emisión'),
        'factura_ids': fields.one2many('cyg.control_facturacion',
                                       'tranferencia_id',
                                       'Facturación'),
        'actividades_ids': fields.one2many('cyg.trans_dominio_actividad',
                                           'tranferencia_id',
                                           'Actividades'),
        'nro_tramite': fields.char('Número de tramite', size=64, required=True),
        'calificado_biess': fields.boolean('Calificado por BIESS'),
        'observaciones': fields.text('Observaciones generales'),
        'vendedor_id': fields.many2one('res.partner', 'Vendedor'),
    }


transferencia_dominio()


class trans_dominio_actividad(osv.osv):
    """Clase para la administración de actividades en las transferencias
    de dominio"""
    _name = 'cyg.trans_dominio_actividad'
    _description = 'Clase para la administración de actividades'

    def _ultima_observacion(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        obs_obj = self.pool.get('cyg.actividad_observacion')
        for record in self.browse(cr, uid, ids, context=context):
            observaciones = self.read(cr, uid, record.id, ['observacion'])
            ultima = {}
            for observacion in obs_obj.browse(cr, uid, observaciones['observacion']):
                if not ultima or time.strptime(observacion.date, '%Y-%m-%d') > time.strptime(ultima['fecha'], '%Y-%m-%d'):
                    ultima['fecha'] = observacion.date
                    ultima['observacion'] = observacion.observacion
                    res[record.id] = ultima['observacion'] if ultima else ''
        return res


    def onchange_grupo(self, cr, uid, id, context=None):
        return {'value': {'actividad_id': False}}

    def onchange_date(self, cr, uid, id, start, end, context=None):
        res = {}
        if start and start > time.strftime('%Y-%m-%d'):
            value = {
                'fecha_ini': False
            }
            return {
                'value': value,
                'warning': {
                    'title': 'Error de usuario',
                    'message': 'La fecha de inicio no puede ser futura'
                }
            }
        if start and end:
            if end > time.strftime('%Y-%m-%d'):
                value = {
                    'fecha_fin': False
                }
                return {
                    'value': value,
                    'warning': {
                        'title': 'Error de usuario',
                        'message': 'La fecha de fin no puede ser futura'
                    }
                }
            if start > end:
                value = {
                    'fecha_fin': False
                }
                return {
                    'value': value,
                    'warning': {
                        'title': 'Error de usuario',
                        'message': 'La fecha de inicio es mayor a la fin'
                    }
                }
        if start:
            res['state']='open'
        return {'value':res}

    def _dias_transcurridos(self, cr, uid, id, field_name, arg, context=None):
        res = {}
        for actividad in self.browse(cr, uid, id, context=context):
            if 'fecha_ini' in actividad and actividad.fecha_ini:
                y1, m1, d1 = (int(x) for x in actividad.fecha_ini.split('-'))
                if 'fecha_fin' in actividad and actividad.fecha_fin:
                    y2, m2, d2 = (int(x) for x in actividad.fecha_fin.split('-'))
                else:
                    now = datetime.datetime.now()
                    y2, m2, d2 = now.year, now.month, now.day
                datediff = datetime.date(y2, m2, d2) - datetime.date(y1, m1, d1)
                res[actividad.id] = datediff.days
            else:
                res[actividad.id] = 0
        return res


    def onchange_actividad(self, cr, uid, id, actividad_id, context=None):
        dias = 0
        if actividad_id:
            actividad = self.pool.get('cyg.actividad').browse(cr, uid, actividad_id, context=context)
            dias = actividad.dias
            grupo = actividad.group_id.id
        return {
            'value': {
                'dias_programados': dias,
                'grupo_id': grupo,
            }
        }
    
    def unlink(self, cr, uid, ids, context=None):
        #TODO: process before delete resource
        list=[]
        for item in self.browse(cr, uid, ids):
            if item.state != 'draft':
                raise osv.except_osv(('Aviso !'),u'Solo puede eliminar actividades en estado borrador')
            else:
                list.append(item.id)
        res = super(trans_dominio_actividad, self).unlink(cr, uid, list, context)
        return res

    _columns = {
        'tranferencia_id': fields.many2one('cyg.transferencia_dominio',
                                           'Transferencia de dominio'),
        'grupo_id': fields.many2one('cyg.actividad_grupo',
                                    'Grupo'),
        'actividad_id': fields.many2one('cyg.actividad',
                                        'Actividad', required=True),
        'dias_programados': fields.integer('Días programados'),
        'fecha_ini': fields.date('Fecha inicio'),
        'fecha_fin': fields.date('Fecha fin'),
        'dias_diferencia': fields.function(_dias_transcurridos, string='Días transcurridos',
                                           type='integer'),
        'persona_entrega_id': fields.many2one('res.partner', 'Entrega'),
        'persona_recibe_id': fields.many2one('res.partner', 'Recibe'),
        'ubicacion': fields.char('Ubicación', size=64),
        'factura_ids': fields.one2many('cyg.actividad_factura', 'actividad_id',
                                       'Facturas'),
        'observacion': fields.one2many('cyg.actividad_observacion', 'actividad_id',
                                       'Observaciones'),
        'ultima_observacion': fields.function(_ultima_observacion, string='Última observación',
                                           type='text', store=True),
        'state': fields.selection([('draft', 'Borrador'),
                                   ('open', 'Abierta'),
                                   ('close', 'Cerrada')], 'Estado'),
    }

    def create(self, cr, uid, values, context=None):
        if 'fecha_ini' in values and values['fecha_ini']:
            values['state'] = 'open'
        if 'fecha_fin' in values and values['fecha_fin']:
            values['state'] = 'close'
        return super(trans_dominio_actividad, self).create(cr, uid, values, context=context)

    def write(self, cr, uid, ids, values, context=None):
        if 'fecha_fin' in values and values['fecha_fin']:
            values['state'] = 'close'
        return super(trans_dominio_actividad, self).write(cr, uid, ids, values, context=context)

    _defaults = {
        'state': 'draft'
    }


trans_dominio_actividad()


class actividad_factura(osv.osv):
    """Clase para la administración de facturas en actividades
    de tranferencias de dominio"""
    _name = 'cyg.actividad_factura'
    _description = "Clase para la administración de facturas en TD"

    _columns = {
        'tercero_id': fields.many2one('res.partner', 'Emisor'),
        'name': fields.char('N° factura', size=64, required=True),
        'fecha_factura': fields.date('Fecha de factura'),
        'valor_factura': fields.float('Valor factura',
                                      digits=(10, 2), required=True),
        'fecha_factura': fields.date('Fecha de factura'),
        'factura_escaneada': fields.binary('Subir factura'),
        'pagada_tercero': fields.selection([('tercero', 'Tercero'), ('banco', 'Banco acreedor')], 'Pagada por'),
        'persona_pago_id': fields.many2one('res.partner', 'Tercero'),
        'forma_pago_id': fields.selection([('efectivo', 'Efectivo'),
                                           ('cheque', 'Cheque'),
                                           ('tarjeta', 'Tarjeta'),
                                           ('tranferencia', 'Tranferencia')
                                          ], 'Forma pago'),
        'num_doc_pago': fields.char('N° de pago', size=64),
        'repuesto': fields.boolean('Ha sido repuesto'),
        'state': fields.selection([('pagado', 'Pagado'),
                                   ('nopagado', 'No pagado')
                                  ], 'Estado pago'),
        'actividad_id': fields.many2one('cyg.trans_dominio_actividad',
                                        'Actividad'),
        'banco_pago_id': fields.many2one('res.bank', 'Banco'),
        'observacion': fields.text('Observaciones')
    }

    _defaults = {
        'state': 'nopagado'
    }


actividad_factura()


class actividad_grupo(osv.osv):
    """Clase para la administración de los grupos para actividades
    de tranferencias de dominio"""
    _name = 'cyg.actividad_grupo'
    _description = "Clase para la administración de grupos en TD"

    _columns = {
        'name': fields.char('Nombre', size=64, required=True),
        'description': fields.text('Descripción'),
        'actividad_ids': fields.one2many('cyg.actividad', 'group_id', 'Actividades', required=True),
        'sequence': fields.float('Secuencia', digits=(10,2)),
    }

    _defaults = {  
        'sequence': 0.0
    }

    _order = 'sequence asc'

actividad_grupo()


class actividad(osv.osv):
    """Clase para la administración de las actividades
    de tranferencias de dominio"""
    _name = 'cyg.actividad'
    _description = "Clase para la administración de actividades en TD"

    _columns = {
        'group_id': fields.many2one('cyg.actividad_grupo',
                                    'Grupo'),
        'name': fields.char('Nombre', size=64, required=True),
        'description': fields.text('Descripción'),
        'code': fields.integer('Código extra', required=True),
        'dias': fields.integer('Días', required=True),
        'secuencia': fields.float('Secuencia', digits=(10,2)),
    }

    _order = 'secuencia asc'

actividad()


class actividad_observacion(osv.osv):
    """Clase para la administración de las actividades
    de tranferencias de dominio"""
    _name = 'cyg.actividad_observacion'
    _description = "Clase para observaciones en actividades en TD"

    _columns = {
        'actividad_id': fields.many2one('cyg.trans_dominio_actividad',
                                    'Actividad'),
        'observacion': fields.text('Observación'),
        'fecha': fields.date('Fecha'),
        'date': fields.date('Fecha de creación'),
        'usuario_id': fields.many2one('res.users', 'Usuario'),
    }

    _order = 'date desc'

    _defaults = {
        'usuario_id': lambda self, cr, uid, context: uid,
        'fecha': lambda *x: time.strftime('%Y-%m-%d')}

actividad()


class control_facturacion(osv.osv):
    """Clase para la administración del control de facturacion"""
    _name = 'cyg.control_facturacion'
    _description = "Clase para la administración de facturacion"

    _columns = {
        'tranferencia_id': fields.many2one('cyg.transferencia_dominio',
                                           'Transferencia de dominio'),
        'cliente_id': fields.many2one('res.partner', 'Cliente'),
        'num_factura': fields.char('Factura',
                                   size=64),
        'fecha_factura': fields.date('Fecha de factura'),
        'valor_factura': fields.float('Valor ($)', digits=(10, 2)),
        'estado_factura': fields.selection([('facturado', 'Facturado'),
                                            ('nofacturado', 'No facturado')],
                                           'Estado facturación'),
        'estado_pago': fields.selection([('pagado', 'Pagado'),
                                         ('nopagado', 'No pagado')],
                                        'Estado pago'),
        'fecha_pago': fields.date('Fecha de pago'),
        'doc_pago': fields.char('N° Cheque o transferencia',
                                size=64),
        'factura_escaneada': fields.binary('Subir factura'),
        'observacion': fields.text('Observaciones')
    }


control_facturacion()
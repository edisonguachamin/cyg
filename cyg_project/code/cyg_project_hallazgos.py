# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today
#    CyG xxxx
#    @autor: Edison Guachamin <edison.guachamin@gmail.com>
#
##############################################################################

import logging
import datetime 
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

class cyg_project_hallazgos(osv.osv):
    _name= 'cyg.project.hallazgos'
    _description = 'Hallazgos'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    
    def onchange_anio(self, cr, uid, ids, texto):
        res = {}
        if texto:
            for item in texto:
                if item not in ('0','1','2','3','4','5','6','7','8','9'):
                    res['warning'] = {'title': 'ERROR', 'message': u"Ingrese solo numeros"}
                    res['value'] = {'anio':''}
                    break
                
        return res
    
    def attachment_tree_view(self, cr, uid, ids, context):
        """ View a list of projects attachments """

        domain = [
            ('res_model', '=', 'cyg.project.hallazgos'),
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
    
    def onchange_fechas(self, cr, uid, ids,entrega,cierre,emision,control,planificado):
        #print '##########onchange_fecha_entrega', entrega
        #print '##########onchange_field_name2', inicial
        res = {'value':{}}
        now = datetime.date.today()
        if emision and entrega:
            fecha_inicial = self._format_date(entrega)
            fecha_emision = self._format_date(emision)
            
            if fecha_inicial < fecha_emision:
                return {'value':{'fecha_entrega':''},
                        'warning':{'title': "Error", "message": "La fecha entrega no debe ser menor que la fecha de emision"}}
        
        
        if cierre and entrega:
            fecha_inicial = self._format_date(entrega)
            fecha_final = self._format_date(cierre)
            
            if fecha_inicial > fecha_final:
                return {'value':{'fecha_entrega':''},
                        'warning':{'title': "Error", "message": "La fecha entrega no debe ser mayor que la fecha de cierre"}}
             
            else:
                res['value']['tiempo_cierre'] = (fecha_final-fecha_inicial).days
        
        if control and entrega:
            fecha_inicial = self._format_date(entrega)
            fecha_final = self._format_date(control)
            if fecha_inicial > fecha_final:
                return {'value':{'fecha_entrega':''},
                        'warning':{'title': "Error", "message": "La fecha entrega no debe ser mayor que la fecha de control de actividad"}}
             
        
        if  emision and cierre:
            fecha_inicial = self._format_date(emision)
            fecha_final = self._format_date(cierre)
            if fecha_final < fecha_inicial:
                return {'value':{'fecha_cierre':''},
                        'warning':{'title': "Error", "message": "La fecha cierre no debe ser menor que la fecha de emision"}}
        
        if  control and cierre:
            fecha_inicial = self._format_date(control)
            fecha_final = self._format_date(cierre)
            if fecha_final > fecha_inicial:
                return {'value':{'fecha_cierre':''},
                        'warning':{'title': "Error", "message": "La fecha cierre no debe ser mayor que la fecha de control de actividad"}}
        
        if  emision and control:
            fecha_inicial = self._format_date(control)
            fecha_final = self._format_date(emision)
            if fecha_inicial < fecha_final:
                return {'value':{'fecha_control':''},
                        'warning':{'title': "Error", "message": "La fecha control no debe ser menor que la fecha de emision"}}
        
        if  cierre and planificado:
            fecha_inicial = self._format_date(planificado)
            fecha_final = self._format_date(cierre)
            if fecha_inicial > fecha_final:
                return {'value':{'fecha_planificacion':''},
                        'warning':{'title': "Error", "message": "La fecha de replanificacion no debe ser mayor que la fecha de cierre"}}
        
        if  control and planificado:
            fecha_inicial = self._format_date(planificado)
            fecha_final = self._format_date(control)
            if fecha_inicial > fecha_final:
                return {'value':{'fecha_planificacion':''},
                        'warning':{'title': "Error", "message": "La fecha de replanificacion no debe ser mayor que la fecha de control"}}
        
        
        return res
    
    def _fnt_fechas(self, cursor, user, ids, name, args, context=None):
        #print 'context amount', context
        if not ids:
            return {}
        
        if context is None:
            context = {}
        res = {}
        for line in self.browse(cursor, user, ids, context=context):
            inicio=fin= 0
            if line.fecha_entrega:
                inicio = self._format_date(line.fecha_entrega)
            if line.fecha_cierre:
                fin = self._format_date(line.fecha_cierre)
            
            if inicio and fin:
                res[line.id] = str((fin-inicio).days)
            
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        #TODO: process before updating resource
        if 'fecha_cierre' in vals:
            vals['state'] = 'cerrado'
        if 'fecha_control' in vals:
            vals['state'] = 'verificado'
        
        res = super(cyg_project_hallazgos, self).write(cr, uid, ids, vals, context)
        return res
    
    def create(self, cr, uid, vals, context={}):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cyg.project.hallazgos') or '/'
            vals['state'] = 'abierto'
            
        if 'fecha_cierre' in vals:
            vals['state'] = 'cerrado'
        
        if 'fecha_control' in vals:
            vals['state'] = 'verificado'
        res_id = super(cyg_project_hallazgos, self).create(cr, uid, vals, context)
        return res_id
    
    
        
    _columns = {
                'name':fields.char('Code', size=500),
                'nro_informe':fields.char('Informe de Auditoria#', size=500),
                'country_id':fields.many2one('res.country','País'),
                'anio':fields.char('Año',size=4),
                #'origen':fields.char('Origen',size=500,helper="Externo (Cliente, Auditoria Externa, Homologaciones de proveedores)"),
                'origen_id':fields.many2one('cyg.project.origen','Origen',helper="Externo (Cliente, Auditoria Externa, Homologaciones de proveedores)"),
                'grado_id':fields.many2one('cyg.project.grado','Grado'),
                'auditor_id':fields.many2one('res.partner','Empresa que Audita'),
                'partner_id':fields.many2one('res.partner','Nombre Auditor'),
                'cliente_id':fields.many2one('res.partner','Cliente'),
                'sitio_id':fields.many2one('cyg.project.sitio','Sitio'),
                'categoria_id':fields.many2one('cyg.project.hallazgo.categoria','Categoría de Hallazgo'),
                'numero':fields.char('Referencia',size=100),
                'area_id':fields.many2one('cyg.project.area','Área de Hallazgo'),
                'responsable_id':fields.many2one('cyg.project.hallazgo.responsable','Responsable de Área'),
                'fecha_emision':fields.date('Fecha de Emisión'),
                'fecha_entrega':fields.date('Fecha de Entrega'),
                'fecha_planificacion':fields.date('Fecha RePlanificada'),
                'fecha_cierre':fields.date('Fecha de Cierre'),
                'state':fields.selection([('draft','Borrador'),
                                          ('abierto','Abierto'),
                                          ('cerrado','Cerrado'),
                                          ('verificado','Verificado')],'Estado'),
                #'tiempo_cierre':fields.float('Tiempo de Cierre'),
                'tiempo_cierre':fields.function(_fnt_fechas, string='Duracion',type='char', size=60,method=True,store=False),
                'fecha_control':fields.date('Fecha Control de actividad'),
                'observaciones':fields.text('Obsevaciones'),
                #'actividades_ids':fields.one2many('cyg.project.hallazgo.actividad','hallazgos_id','Actividades'),
                'hallazgos_line_ids':fields.one2many('cyg.project.hallazgo.line','hallazgos_id','Descripción de Hallazgos'),
                }
    _defaults = {  
        'anio': lambda *a: time.strftime('%Y'),
        'country_id':lambda self,cr,uid,c: self.pool.get('res.country').search(cr, uid, [('name','=','Ecuador')], context=c)[0],
        #'area_id':lambda self,cr,uid,c: self.pool.get('res.country').search(cr, uid, [('name','=','Ecuador')], context=c)[0],
        #'datee': lambda *a: time.strftime('%Y-%m-%d')
        'name': lambda obj, cr, uid, context: '/',
        #'origen':'EX',
        'state':'draft',
        }
cyg_project_hallazgos()

class cyg_project_hallazgo_line(osv.osv):
    _name = 'cyg.project.hallazgo.line'
    _description = 'Descripcion de Hallazgo'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    
    def _fnt_avance(self, cursor, user, ids, name, args, context=None):
        #print 'context amount', context
        if not ids:
            return {}
        
        if context is None:
            context = {}
        res = {}
        
        for line in self.browse(cursor, user, ids, context=context):
            if line.actividades_ids:
                peso=factores=0
                for x in line.actividades_ids:
                    peso += x.prioridad_id and x.prioridad_id.code or 0
                    factores +=  x.prioridad_id and x.prioridad_id.code or 0  * x.porcentage_avance or 0.0
                if peso:
                    res[line.id] = factores / peso
                else:
                    res[line.id] = 0
            else:
                res[line.id] = 0
        return res
    
    def onchange_clausula(self, cr, uid, ids, clausula):
        res = {'value':{}}
        clausula_obj = self.pool.get('cyg.project.clausula')
        
        if clausula:
            clausula_info = clausula_obj.browse(cr, uid,clausula)
            res['value']['descripcion'] =clausula_info.descripcion

        return res
    
    def attachment_tree_view(self, cr, uid, ids, context):
        """ View a list of projects attachments """

        domain = [
            ('res_model', '=', 'cyg.project.hallazgos.line'),
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

    
    _columns = {
                'name':fields.char('Descripción', size=500),
                'hallazgos_id':fields.many2one('cyg.project.hallazgos','Hallazgos'),
                'norma_id':fields.many2one('cyg.project.norma','Norma'),
                'clausula_id':fields.many2one('cyg.project.clausula','Cláusula'),
                'descripcion':fields.text('Descripción'),
                'avance': fields.function(_fnt_avance, string='Avance', type='float',digits=(16,2), method=True,store=False),
                'descripcion_hallazgo':fields.text('Descripción del Hallazgo'),
                'impacto_id':fields.many2one('cyg.project.impacto','Impacto'),
                'accion':fields.text('Acción Curativa o Inmediata',size=1000),
                'analisis':fields.text('Analisis de Causa',size=1000),
                'accion_propuesta':fields.text('Acción Correctiva Propuesta',size=1000),
                'actividades_ids':fields.one2many('cyg.project.hallazgo.actividad','hallazgo_line_id','Actividades'),
                'causas_ids':fields.one2many('cyg.project.hallazgo.causa','hallazgo_line_id','Causas'),
                'accion_correctiva_ids':fields.one2many('cyg.project.hallazgo.accion.correctiva','hallazgo_line_id','Acción Correctiva'),
                'state':fields.selection([('abierto','Abierto'),
                                          ('ejecucion','Ejecución'),
                                                  ('cerrado','Cerrado'),],'Estado'),
                }
    _defaults = {  
        'state': 'abierto'
        }
cyg_project_hallazgo_line()

class cyg_project_hallazgo_accion_correctiva(osv.osv):
    _name = 'cyg.project.hallazgo.accion.correctiva'
    _description = 'Accion Correctiva'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    
    def onchange_causa(self, cr, uid, ids, causa):
        res = {'value':{}}
        causa_obj = self.pool.get('cyg.project.causa')
        
        if causa:
            causa_info = causa_obj.browse(cr, uid,causa)
            res['value']['descripcion_causa'] =causa_info.descripcion

        return res
    
    _columns = {
                'name':fields.char('Accion Correctiva', size=100),
                'hallazgo_line_id':fields.many2one('cyg.project.hallazgo.line','Hallazgo'),
                'descripcion':fields.text('Descripción'),
                }
    _defaults = {  
        #'state': 'abierto'
        }
cyg_project_hallazgo_accion_correctiva()


class cyg_project_hallazgo_causa(osv.osv):
    _name = 'cyg.project.hallazgo.causa'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    
    def onchange_causa(self, cr, uid, ids, causa):
        res = {'value':{}}
        causa_obj = self.pool.get('cyg.project.causa')
        
        if causa:
            causa_info = causa_obj.browse(cr, uid,causa)
            res['value']['descripcion_causa'] =causa_info.descripcion

        return res
    
    _columns = {
                'name':fields.char('Causa', size=100),
                'hallazgo_line_id':fields.many2one('cyg.project.hallazgo.line','Hallazgo'),
                'causa_id':fields.many2one('cyg.project.causa','Definición de Causa (6m)'),
                'descripcion_causa':fields.text('Descripción Causa'),
                'state':fields.selection([('abierto','Abierto'),
                                          ('ejecucion','Ejecución'),
                                                  ('cerrado','Cerrado'),],'Estado'),
                }
    _defaults = {  
        'state': 'abierto'
        }
cyg_project_hallazgo_causa()


class cyg_project_hallazgo_actividad(osv.osv):
    _name = 'cyg.project.hallazgo.actividad'
    
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    
    def valida_porcentaje(self,cr, uid, ids,valor):
        res = {}
        if valor:
            if valor < 0 or valor > 100:
                return {'value':{'porcentage_avance':0},
                        'warning':{'title': "Error", "message": "El porcentaje debe estar entre 0 y 100"}}
            else:
                return res
    
    def onchange_cierre(self, cr, uid, ids, fecha, avance):
        res = {'value':{}}
        
        if avance < 0 or avance > 100:
                return {'value':{'porcentage_avance':0},
                        'warning':{'title': "Error", "message": "El porcentaje debe estar entre 0 y 100"}}
        if fecha and avance:
            
            if avance ==100:
                res['value']['state'] ='cerrado'
        return res
    
    def attachment_tree_view(self, cr, uid, ids, context):
        """ View a list of projects attachments """

        domain = [
            ('res_model', '=', 'cyg.project.hallazgo.actividad'),
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
        
    def onchange_accion(self, cr, uid, ids, accion):
        res = {'value':{}}
        correctiva_obj = self.pool.get('cyg.project.hallazgo.accion.correctiva')
        
        if accion:
            accion_info = correctiva_obj.browse(cr, uid,accion)
            res['value']['name'] =accion_info.name

        return res
    
    _columns = {
                'name':fields.char('Actividad', size=5000),
                'hallazgo_line_id':fields.many2one('cyg.project.hallazgo.line','Hallazgos Lines'),
                'actividad_id':fields.many2one('cyg.project.actividad.hallazgo','Actividad'),
                'new_accion_id':fields.many2one('cyg.project.hallazgo.accion.correctiva','Acción Correctiva'),
                #'accion_id':fields.many2one('cyg.project.actividad.correctiva','Acción Correctiva'),
                'date_inicio':fields.date('Fecha de Inicio'),
                'date_fin':fields.date('Fecha de Fin Propuesta'),
                'sequence':fields.integer('#'),
                'presupuesto_requerido':fields.float('Presupuesto Requerido'),
                'partner_id':fields.many2one('res.partner','Responsable'),
                'prioridad_id':fields.many2one('cyg.project.prioridad', 'Prioridad'),
                'linea_negocio':fields.many2one('cyg.project.negocio', 'Línea de Negocio'),
                'presupuesto_ejecutado':fields.float('Presupuesto Ejecutado'),
                'nro_orden_compra':fields.char('Nro Orden Compra', size=100),
                'fecha_cierre':fields.date('Fecha de cierre real'),
                'porcentage_avance':fields.float('% de Avance'),
                'observacion':fields.text('Observación'),
                'seguimiento_ids':fields.one2many('cyg.project.hallazgo.seguimiento','actividad_id','Seguimiento'),
                'state':fields.selection([('abierto','Abierto'),
                                          ('ejecucion','Ejecución'),
                                                  ('cerrado','Cerrado'),],'Estado'),
                }
    _defaults = {  
        'state': 'abierto',
        #'accion_id':lambda self,cr,uid,c: self.pool.get('cyg.project.actividad.correctiva').search(cr, uid, [('code','=','01')], context=c)[0],
        }
cyg_project_hallazgo_actividad()

class cyg_project_hallazgo_seguimiento(osv.osv):
    _name = 'cyg.project.hallazgo.seguimiento'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Seguimiento', size=100),
                'actividad_id':fields.many2one('cyg.project.hallazgo.actividad','Actividad'),
                'date':fields.date('Fecha de Verificación'),
                'observacion':fields.text('Observación'),
                'state':fields.selection([('abierto','Abierto'),
                                          ('ejecucion','Ejecución'),
                                                  ('cerrado','Cerrado'),],'Estado'),
                }
    _defaults = {  
        'state': 'abierto'
        }
cyg_project_hallazgo_seguimiento()


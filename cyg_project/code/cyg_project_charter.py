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
from openerp import tools
from openerp import SUPERUSER_ID
from openerp import pooler, tools
from openerp.osv import fields, osv, expression
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round

import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)
from utils import cambiarTildes

class cyg_project_charter(osv.osv):
    _name= 'cyg.project.charter'
    _description = 'Project Charter'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    
    def attachment_tree_view(self, cr, uid, ids, context):
        """ View a list of projects attachments """

        domain = [
            ('res_model', '=', 'cyg.project.charter'),
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
        if vals.get('code','/')=='/':
            vals['code'] = self.pool.get('ir.sequence').get(cr, uid, 'cyg.project.charter') or '/'
        res_id = super(cyg_project_charter, self).create(cr, uid, vals, context)
        return res_id
    
    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result
    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)
    
    def _fnt_contratos(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for project in self.browse(cr, uid, ids, context=context):
            #print 'order', order.poreserva
            
            res[project.id] = {
                'costos': 0.00,
                'utilidad_costos': 0.00,
                'utilidad_ingresos': 0.00,
            }
            val = val1 = 0.00
            
            for line in project.project_budget_ids:
                val1 += line.presupuesto_aprobado
            res[project.id]['costos'] = val1
            if project.valor_contrato:
                res[project.id]['utilidad_costos'] = round((project.valor_contrato - val1)/ val1,2)*100
                res[project.id]['utilidad_ingresos'] = round((project.valor_contrato - val1)/ project.valor_contrato,2)*100
        return res
    def button_dummy(self, cr, uid, ids, context=None):
        return True
    
    
    def button_target_requisitos(self, cr, uid, ids, context={}):
        requisitos_obj = self.pool.get('cyg.project.requisito')
        result = requisitos_obj.search(cr, uid, [], context=context)
        repetidos =[]
        for item in self.browse(cr, uid, ids):
            if item.project_cierre_ids:
                for y in item.project_cierre_ids:
                    repetidos.append(y.requisito_id.id)
            print 'repetidos',repetidos
            for x in requisitos_obj.browse(cr, uid,result):
                if x.id not in repetidos:
                    dict = {'name':x.descripcion,
                            'requisito_aceptacion':x.descripcion,
                            'project_id':item.id,
                            'requisito_id':x.id,
                            }
                    self.pool.get('cyg.project.cierre').create(cr,uid,dict)
        return True
    
    def button_target_actividades(self, cr, uid, ids, context={}):
        actividades_obj = self.pool.get('cyg.project.actividad')
        result = actividades_obj.search(cr, uid, [], context=context)
        repetidos =[]
        for item in self.browse(cr, uid, ids):
            if item.project_plan_ids:
                for y in item.project_plan_ids:
                    repetidos.append(y.actividad_id.id)
            print 'repetidos',repetidos
            for x in actividades_obj.browse(cr, uid,result):
                if x.id not in repetidos:
                    dict = {'name':x.descripcion,
                            'project_id':item.id,
                            'actividad_id':x.id,
                            'grupo_id':x.grupo_id and x.grupo_id.id,
                            'sequence':x.code,
                            'sequence_grupo':x.grupo_id and x.grupo_id.code,
                            'descripcion':x.descripcion
                            }
                    self.pool.get('cyg.project.plan').create(cr,uid,dict)
        return True
    
    _columns = {
                'name':fields.char('Nombre de Proyecto', size=5000),
                'code':fields.char('Código del Proyecto', size=500),
                'fecha_primer_contacto':fields.date('Fecha de primer contacto'),
                'fecha_firma_contrato':fields.date('Fecha firma contrato'),
                'fecha_inicio_proyecto':fields.date('Fecha inicio proyecto'),
                'fecha_tentativa_cierre':fields.date('Fecha tentativa cierre'),
                'fecha_real_cierre':fields.date('Fecha real de cierre'),
                'responsable_ids':fields.one2many('cyg.project.responsable','project_id','Responsables'),
                'proveedor_ids':fields.one2many('cyg.project.proveedor','project_id','Proveedores'),
                'partner_id':fields.many2one('res.partner','Gerente de Proyecto'),
                'unidad_negocio_id':fields.many2one('cyg.project.negocio', 'Unidad de Negocio'),
                'resumen_ejecutivo':fields.text('Resumen Ejecutivo'),
                'objetivos_proyecto':fields.text('Objetivos de Proyectos'),
                'alcance':fields.text('Alcance'),
                'entregables':fields.text('Entregables'),
                'estructura_proyectos':fields.text('Estructura de Proyectos'),
                'gobernanza_proyecto':fields.text('Gobernanza de Proyectos'),
                'riesgos_proyecto':fields.text('Riesgos del Proyecto'),
                'supuestos':fields.text('Supuestos'),
                'hitos_fundamentales':fields.text('Hitos Fundamentales'),
                'presupuestos':fields.text('Presupuesto'),
                'anexos':fields.text('Anexos'),
                'observaciones':fields.text('Observaciones Generales'),
                'state':fields.selection([('abierto','Abierto'),
                                          ('ejecucion','Ejecución'),
                                                  ('cerrado','Cerrado'),],'Estado'),
                'grupos_interes_ids':fields.one2many('cyg.project.grupos.interes','project_id','Grupo de Interés'),
                'matrix_riesgos_ids':fields.one2many('cyg.project.matrix.riesgos','project_id','Matriz de Riesgos'),
                'project_plan_ids':fields.one2many('cyg.project.plan','project_id','Project Plan / Cronograma'),
                'project_budget_ids':fields.one2many('cyg.project.budget','project_id','Presupuesto'),
                'project_cambios_ids':fields.one2many('cyg.project.cambios','project_id','Gestion Cambios'),
                'project_cierre_ids':fields.one2many('cyg.project.cierre','project_id','Cierre de Proyecto'),
                'project_lecciones_ids':fields.one2many('cyg.project.lecciones','project_id','Lecciones Aprendidas'),
                'observacion_matrix':fields.text('Observaciones Generales'),
                'image': fields.binary("Photo",
                                       help="This field holds the image used as photo for the employee, limited to 1024x1024px."),
                'image_medium': fields.function(_get_image, fnct_inv=_set_image,
                string="Medium-sized photo", type="binary", multi="_get_image",
                store = {
                    'cyg.project.charter': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                },
                help="Medium-sized photo of the employee. It is automatically "\
                     "resized as a 128x128px image, with aspect ratio preserved. "\
                     "Use this field in form views or some kanban views."),
                'image_small': fields.function(_get_image, fnct_inv=_set_image,
                string="Small-sized photo", type="binary", multi="_get_image",
                store = {
                    'cyg.project.charter': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                },
                help="Small-sized photo of the employee. It is automatically "\
                     "resized as a 64x64px image, with aspect ratio preserved. "\
                     "Use this field anywhere a small image is required."),
                
                'script_interes':fields.text('Instrucciones'),
                'script_paso1':fields.text('Paso 1'),
                'script_paso2':fields.text('Paso 2'),
                'script_paso3':fields.text('Paso 3'),
                'script_paso4':fields.text('Paso 4'),
                'script_paso5':fields.text('Paso 5'),
                #'script_paso6':fields.text('Paso 5'),
                #PANTALLA DE RIESGOS
                'ocurrencia_1':fields.text('Ocurrencia'),
                'gravedad_1':fields.text('Gravedad'),
                'deteccion_1':fields.text('Detección'),
                'factor_1':fields.text('Factor'),
                #PANTALLA DE PRESUPUESTOS
                'valor_contrato':fields.float('Valor del Contrato', digits=(16,2)),
                'costos': fields.function(_fnt_contratos, string='Costos', type='float', digits=(16,2),  method=True, store=False,multi='presupuestos'),
                'utilidad_costos': fields.function(_fnt_contratos, string='Utilidad sobre Costos', type='float', digits=(16,2),  method=True, store=False,multi='presupuestos'),
                'utilidad_ingresos': fields.function(_fnt_contratos, string='Utilidad sobre Ingresos', type='float', digits=(16,2),  method=True, store=False,multi='presupuestos'),
                'currency_id':fields.many2one('res.currency','Moneda'),
                #PANTALLA DE CIERRE
                'proveedor':fields.char('Nombre', size=100),
                'cargo':fields.char('Cargo', size=100),
                'fecha':fields.date('Fecha'),
                'cliente':fields.char('Nombre', size=100),
                'cargo_cliente':fields.char('Cargo', size=100),
                'fecha_cliente':fields.date('Fecha'),
            }
    
        
    
    _defaults = {  
        'code': lambda obj, cr, uid, context: '/',
        #'code':lambda self,cr,uid,context: self.pool.get('ir.sequence').get(cr, uid, 'cyg.project.charter'),
        'currency_id':lambda self,cr,uid,c: self.pool.get('res.currency').search(cr, uid, [('name','=','USD')], context=c)[0],
        #'project_cierre_ids':_getdefault_cierre,
        'state':'abierto',
        'ocurrencia_1':"""
        1 Improbable
        2 Remoto
        3 Ocasional
        4 Probable
        5 Frecuente
        """,
        'gravedad_1':"""
        1 No significativa
        2 Bajo Impacto
        3 Significante
        4 Mayor
        5 Falla crítica
        
        """,
        'deteccion_1':"""
        1 Inmediata
        2 Detectado Facilmente
        3 Detectable siguiendo el proceso
        4 Muy díficil de detectar
        5 Indetectable
        """,
        'factor_1':"""
        1 No hay peligro
        to
        125 Falla crítica 
        """,
        'script_interes':"""
        El líder con su equipo, intercambian ideas sobre las preguntas de cada columna para desarrollar el análisis de los grupos de interés.
        Esta información se incorporará entonces en su plan de comunicación.
        """,
        'script_paso1':"""
        ¿Quién tiene un interés en el proyecto en términos de proceso o resultado?
        ¿Quién tiene información o especialización para contribuir?
        ¿Quién tiene responsabilidad funcional por el proyecto o su resultado?
        ¿Quién debe ser involucrado en decisiones del proyecto y aprobaciones?
        ¿Quién tiene la autoridad para aprobar gastos del proyecto y compra?
        ¿Quién se beneficiaría de participación o de observaciones?
        ¿Quién debe ser involucrado en una perspectiva orgánica o política?
        """,
        'script_paso2':"""
        ¿Cuáles son los intereses de este grupo con respecto al proyecto?
        ¿Cuáles son las sensibilidades o "botones calientes" para cada uno de los grupos de interés?
        ¿Cuáles son sus específicas preocupaciones o necesidades como resultado del proyecto?   
        Ejemplo: Proyecto exitoso.  
        A tiempo, dentro del presupuesto, y entrega de entregables esperados.  
        No desea sorpresas.  
        Obtener advertencias tempranas.  
        Quiere saber impacto de, riesgos, e implicaciones del proyecto.
        """,
        'script_paso3':"""
        Para cada grupo, intercambio de ideas de lo que su proyecto necesita de los grupos de interés 
        y los resultados esperados de sus comunicaciones con este grupo.  
        Ejemplo: Apoyo continuo del proyecto.  
        Problema que resuelve cuando se necesita. 
        Comunicaciones eficaces a lo largo de la ejecución del proyecto.  
        Entender el impacto del proyecto para ayudarlos a toman decisiones correctas sobre sus procesos comerciales.
        """,
        'script_paso4':"""
        Para evaluar el impacto de los grupos de interés, considere el papel que ellos deben jugar el éxito del proyecto, 
        y la probabilidad que el grupo de interés tenga en este éxito.  
        También considere la probabilidad e impacto de la contestación negativa de un grupo de interés al proyecto.
        Asigne A para sumamente importante, B para bastante importante, y C para no muy importante.
        """,
        'script_paso5':"""
        Considere que las cosas que usted podría hacer para ganar el apoyo y reducir la oposición del grupo de interés.
        Considere cómo usted podría acercarse a cada uno de los grupos de interés.
        ¿Qué tipo de información necesitarán ellos?
        ¿Qué importante es el involucrar al Grupo de interés en el proceso de la planificación?
        ¿Existen otros grupos o individuos que podrían influir en el grupo de interés para apoyar su iniciativa?
        """,
        #---------------------------------------------------- 'script_paso6':"""
        #----------- ¿Cuáles métodos son los más apropiados para ésta audiencia?
        #------------------------------------------------------------------ """,
        }
cyg_project_charter()

class cyg_project_responsable(osv.osv):
    _name = 'cyg.project.responsable'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Responsable', size=100),
                'project_id':fields.many2one('cyg.project.charter','Proyecto'),
                'partner_id':fields.many2one('res.partner','Responsable'),
                'observacion':fields.text('Observación'),
                }
cyg_project_responsable()

class cyg_project_proveedor(osv.osv):
    _name = 'cyg.project.proveedor'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Proveedor', size=100),
                'project_id':fields.many2one('cyg.project.charter','Proyecto'),
                'partner_id':fields.many2one('res.partner','Proveedor'),
                'observacion':fields.text('Observación'),
                }
cyg_project_proveedor()

class cyg_project_grupos_interes(osv.osv):
    _name = 'cyg.project.grupos.interes'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.text('Grupo Interés'),
                'project_id':fields.many2one('cyg.project.charter','Proyecto'),
                'paso_uno':fields.text('Paso 1 \nGrupos de Interés'),
                'paso_dos':fields.text('Paso 2 \nNecesidades'),
                'paso_tres':fields.text('Paso 3 \nQue esperamos como resultado'),
                'paso_impacto_id':fields.many2one('cyg.project.grupo.interes.impacto','Paso 4 \nImpacto'),
                'paso_cinco':fields.text('Paso 5 Posibles Estrategias'),
                #'paso_seis':fields.text('Paso 6 Metodos Apropiados'),
                'observacion':fields.text('Observación'),
                }
    _defaults = {  
        'name': """
        Instrucciones: El líder con su equipo, intercambian ideas sobre las preguntas de cada columna para desarrollar el análisis de los grupos de interés.  Esta información se incorporará entonces en su plan de comunicación.
        """
        }
cyg_project_grupos_interes()

class cyg_project_matrix_riesgos(osv.osv):
    _name = 'cyg.project.matrix.riesgos'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    
    def on_change_calificaciones(self, cr, uid, ids, ocurrencia, serveridad,deteccion):
        res = {}
        val1=val2=val3 = 0
        if ocurrencia:
            val1= int(ocurrencia)
        if serveridad:
            val2= int(serveridad)
        if deteccion:
            val3= int(deteccion)
        res['value'] = {'factor_danio': val1*val2*val3}
        return  res
    
    def on_change_calificaciones01(self, cr, uid, ids, ocurrencia, serveridad,deteccion):
        res = {}
        val1=val2=val3 = 0
        if ocurrencia:
            val1= int(ocurrencia)
        if serveridad:
            val2= int(serveridad)
        if deteccion:
            val3= int(deteccion)
        res['value'] = {'factor_danio_01': val1*val2*val3}
        return  res
        
    def _factor_danio(self, cursor, user, ids, name, args, context=None):
        #print 'context amount', context
        if not ids:
            return {}
        
        if context is None:
            context = {}
        res = {}
        
        for line in self.browse(cursor, user, ids, context=context):
            ocurrencia = severidad=deteccion=0.00
            if line.ocurrencia:
                ocurrencia = int(line.ocurrencia)
            if line.severidad:
                severidad = int(line.severidad)
            if line.deteccion:
                deteccion = int(line.deteccion)
            res[line.id] = ocurrencia*severidad*deteccion
            
        return res
    
    def _factor_danio_01(self, cursor, user, ids, name, args, context=None):
        #print 'context amount', context
        if not ids:
            return {}
        
        if context is None:
            context = {}
        res = {}
        
        for line in self.browse(cursor, user, ids, context=context):
            ocurrencia = severidad = deteccion=0.00
            if line.ocurrencia:
                ocurrencia = int(line.ocurrencia_01)
            if line.severidad:
                severidad = int(line.severidad_01)
            if line.deteccion:
                deteccion = int(line.deteccion_01)
            res[line.id] = ocurrencia*severidad*deteccion
            
        return res
    _columns = {
                'name':fields.char('Nombre', size=100),
                'sequence':fields.integer('#'),
                'project_id':fields.many2one('cyg.project.charter','Proyecto'),
                'riesgo_id':fields.many2one('cyg.project.area.riesgo',"Área Riesgo"),
                'modo_fallo':fields.text('Modo Fallos'),
                'efecto_falla':fields.text('Efecto Falla'),
                'causa_falla':fields.text('Causas Falla'),
                'ocurrencia':fields.selection([('1','1'),
                                               ('2','2'),
                                               ('3','3'),
                                               ('4','4'),
                                               ('5','5'),
                                               ],'O'),
                'severidad':fields.selection([('1','1'),
                                               ('2','2'),
                                               ('3','3'),
                                               ('4','4'),
                                               ('5','5'),
                                               ],'S'),
                'deteccion':fields.selection([('1','1'),
                                               ('2','2'),
                                               ('3','3'),
                                               ('4','4'),
                                               ('5','5'),
                                               ],'D'),
                'factor_danio': fields.function(_factor_danio, string='FD', type='char', size=60,method=True,store=False),
                'recomendaciones':fields.text('Recomend.Control'),
                'responsable':fields.text('Resp.'),
                'fecha_limite_accion':fields.date('Fecha Límite Acción'),
                'acciones_tomadas':fields.text('Acciones Tomadas'),
                'ocurrencia_01':fields.selection([('1','1'),
                                               ('2','2'),
                                               ('3','3'),
                                               ('4','4'),
                                               ('5','5'),
                                               ],'O'),
                'severidad_01':fields.selection([('1','1'),
                                               ('2','2'),
                                               ('3','3'),
                                               ('4','4'),
                                               ('5','5'),
                                               ],'S'),
                'deteccion_01':fields.selection([('1','1'),
                                               ('2','2'),
                                               ('3','3'),
                                               ('4','4'),
                                               ('5','5'),
                                               ],'D'),
                'factor_danio_01': fields.function(_factor_danio_01,type='char', size=60, string='FD', method=True,store=False),
                'ok':fields.text('Ok'),
                }
cyg_project_matrix_riesgos()

class cyg_project_plan(osv.osv):
    _name = 'cyg.project.plan'
    _order = 'sequence_grupo,sequence'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    
    def _format_date(self, date):
        if date:
            campos = date.split('-')
            date = datetime.date(int(campos[0]), int(campos[1]), int(campos[2]))
            return date
    
    def onchange_fechas(self, cr, uid, ids,inicial,final,real):
        #print '##########onchange_fecha_entrega', entrega
        #print '##########onchange_field_name2', inicial
        res = {'value':{}}
        now = datetime.date.today()
        if final and inicial:
            fecha_inicial = self._format_date(inicial)
            fecha_final = self._format_date(final)
            
            if fecha_final < fecha_inicial:
                return {'value':{'fecha_cumplimiento':''},
                        'warning':{'title': "Error", "message": "La fecha cumplimiento debe ser mayor que la fecha de inicio"}}
             
            else:
                res['value']['duracion'] = (fecha_final-fecha_inicial).days
        if inicial and real:
            fecha_real = self._format_date(real)
            fecha_inicial = self._format_date(inicial)
            if fecha_real < fecha_inicial:
                return {'value':{'fecha_real_fin':''},
                        'warning':{'title': "Error", "message": "La fecha real de fin debe ser mayor que la fecha de inicio"}}
            else:
                res['value']['tiempo_transcurrido'] = (fecha_real-fecha_inicial).days
        return res
    
    def _fnt_fechas(self, cursor, user, ids, name, args, context=None):
        #print 'context amount', context
        if not ids:
            return {}
        
        if context is None:
            context = {}
        res = {}
        for line in self.browse(cursor, user, ids, context=context):
            res[line.id] = {'duracion':'0',
               'tiempo_transcurrido':'0'
               }
            inicio=fin=real= 0
            if line.fecha_inicio:
                inicio = self._format_date(line.fecha_inicio)
            if line.fecha_cumplimiento:
                fin = self._format_date(line.fecha_cumplimiento)
            if line.fecha_real_fin:
                real = self._format_date(line.fecha_real_fin)
            if inicio and fin:
                res[line.id]['duracion'] = str((fin-inicio).days)
            if inicio and real: 
                res[line.id]['tiempo_transcurrido'] = str((real-inicio).days)
        return res
    
    def valida_porcentaje(self,cr, uid, ids,valor):
        res = {}
        if valor:
            if valor < 0 or valor > 100:
                return {'value':{'porcentage':0},
                        'warning':{'title': "Error", "message": "El porcentaje debe estar entre 0 y 100"}}
            else:
                return res
    
    def onchange_actividad(self, cr,uid, ids, actividad):
        res ={'value':{}}
        actividad_obj = self.pool.get('cyg.project.actividad')
        if actividad:
            actividad_info = actividad_obj.browse(cr, uid, actividad)
            res['value']['descripcion'] = actividad_info.descripcion
            res['value']['sequence'] = actividad_info.code
            res['value']['grupo_id'] = actividad_info.grupo_id and actividad_info.grupo_id.id or False
            res['value']['sequence_grupo'] = actividad_info.grupo_id and actividad_info.grupo_id.code or False
            
        return res
    
    _columns = {
                'name':fields.char('Project Plan', size=100),
                'project_id':fields.many2one('cyg.project.charter','Proyecto'),
                'sequence':fields.integer('#', size=3),
                'sequence_grupo':fields.integer('#', size=3),
                'actividad_id':fields.many2one('cyg.project.actividad','Descripcion Actividad'),
                'partner_id':fields.many2one('res.partner','Responsable'),
                'grupo_id':fields.many2one('cyg.project.grupo.actividad','Grupo'),
                'descripcion':fields.text('Descripción Actividad'),
                'recursos':fields.text('Recursos'),
                'fecha_inicio':fields.date('Fecha Inicio'),
                'fecha_cumplimiento':fields.date('Fecha Cumpl.'),
                'duracion':fields.function(_fnt_fechas, string='Duracion',type='char', size=60,method=True,store=False, multi='fechas'),
                'fecha_real_fin':fields.date('Fecha Real Fin'),
                'tiempo_transcurrido':fields.function(_fnt_fechas, string='Transcurrido',type='char', size=60,method=True,store=False,multi='fechas'),
                'porcentage':fields.integer('%', size=3),#
                'observacion':fields.text('Observaciones'),
                }
cyg_project_plan()
class cyg_project_budget(osv.osv):
    _name = 'cyg.project.budget'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    
    def _fnt_diferencia(self, cursor, user, ids, name, args, context=None):
        #print 'context amount', context
        if not ids:
            return {}
        
        if context is None:
            context = {}
        res = {}
        
        for line in self.browse(cursor, user, ids, context=context):
            diferencia = 0
            if line.presupuesto_aprobado and line.ejecucion_presupuestaria:
                res[line.id] = line.presupuesto_aprobado - line.ejecucion_presupuestaria
            else:
                res[line.id] =0.00 
            
        return res
    
    def onchange_presupuesto(self, cr, uid, ids, aprobado,ejecutado):
        res = {}
        if aprobado and ejecutado:
            res['value'] = {'diferencia': aprobado-ejecutado}
        return res
    
    _columns = {
                'name':fields.char('Grupo Interés', size=100),
                'project_id':fields.many2one('cyg.project.charter','Proyecto'),
                'fase_id':fields.many2one('cyg.project.fase','Fases'),
                'descripcion':fields.char('Descripción', size=500),
                'presupuesto_aprobado':fields.float('Aprobado'),
                'ejecucion_presupuestaria':fields.float('Ejecutado'),
                'diferencia':fields.function(_fnt_diferencia, string='Diferencia', type='float', digits=(16,2), method=True, store=False),
                'observacion':fields.text('Observación'),
                }
cyg_project_budget()
class cyg_project_cambios(osv.osv):
    _name = 'cyg.project.cambios'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    def create(self, cr, uid, vals, context={}):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cyg.project.cambios') or '/'
        res_id = super(cyg_project_cambios, self).create(cr, uid, vals, context)
        return res_id
    
    _columns = {
                'name':fields.char('Código Requerimiento', size=100),
                'project_id':fields.many2one('cyg.project.charter','Proyecto'),
                'persona_solicita':fields.char('Persona que solicita el cambio', size=500),
                'descripcion':fields.text('Descripción detallada de la modificación'),
                'justificacion':fields.text('Justificación del cambio'),
                'impacto':fields.text('Impacto al Presupuesto'),
                'cronograma':fields.text('Impacto al cronograma'),
                'otros':fields.text('Otros impactos'),
                'calendario':fields.text('Calendario para implementación al cambio'),
                'proveedor':fields.char('Nombre', size=100),
                'cargo':fields.char('Cargo', size=100),
                'fecha':fields.date('Fecha'),
                'cliente':fields.char('Nombre', size=100),
                'cargo_cliente':fields.char('Cargo', size=100),
                'fecha_cliente':fields.date('Fecha'),
                'observacion':fields.text('Observaciones Generales'),
                }
    _defaults = {  
        'name': '/'
        }
cyg_project_cambios()

class cyg_project_cierre(osv.osv):
    _name = 'cyg.project.cierre'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    
    def onchange_requisito(self, cr, uid, ids, requisito):
        requisito_obj = self.pool.get('cyg.project.requisito')
        res = {'value':{}}
        if requisito:
            requisito_info = requisito_obj.browse(cr, uid,requisito)
            res['value']['requisito_aceptacion']=requisito_info.descripcion
            res['value']['name']=requisito_info.descripcion
        return res
    
    def onchange_pendiente(self, cr, uid, ids, pendiente):
        res = {'value':{}}
        if pendiente:
            res['value']['cerrado']=False
            res['value']['no_aplica']=False
        return res
    
    def onchange_cerrado(self, cr, uid, ids, cerrado):
        res = {'value':{}}
        if cerrado:
            res['value']['pendiente']=False
            res['value']['no_aplica']=False
        return res
    
    def onchange_noaplica(self, cr, uid, ids, noaplica):
        res = {'value':{}}
        if noaplica:
            res['value']['pendiente']=False
            res['value']['cerrado']=False
        return res
        
    _columns = {
                'name':fields.char('Proyecto Cierre', size=100),
                'project_id':fields.many2one('cyg.project.charter','Proyecto'),
                'requisito_aceptacion':fields.char('Descripción', size=500),
                'requisito_id':fields.many2one('cyg.project.requisito','Requisito de Aceptación/Cierre'),
                'pendiente':fields.boolean('Pendiente'),
                'cerrado':fields.boolean('Cerrado'),
                'no_aplica':fields.boolean('No Aplica'),
                'observacion':fields.text('Observaciones Generales'),
                
                }
    _defaults = {  
        #"project_id": lambda self, cr, uid, c: c.get('project_id', False),
        }
cyg_project_cierre()


class cyg_project_lecciones(osv.osv):
    _name = 'cyg.project.lecciones'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    def create(self, cr, uid, vals, context={}):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cyg.project.lecciones') or '/'
        res_id = super(cyg_project_charter, self).create(cr, uid, vals, context)
        return res_id
    
    _columns = {
                'name':fields.char('Codigo', size=100),
                'project_id':fields.many2one('cyg.project.charter','Proyecto'),
                'adjunto_lecciones_ids':fields.one2many('ir.attachment','leccion_id','Lecciones Aprendidas'),
                'persona_lidera':fields.char('Persona que lidera',size=100),
                'fecha_registro':fields.date('Fecha de Registro'),
                'fecha_ejecucion':fields.date('Fecha de ejecución de los trabajos'),
                'progreso_id':fields.many2one('cyg.project.progreso','Progeso'),
                'actividad':fields.text('Actividad específica'),
                'descripcion':fields.text('Descripción de la lección aprendida'),
                'identificar':fields.text('¿Cómo se puede identificar una situación similar en el futuro?'),
                'conducta':fields.text('¿Qué conducta se recomienda para el futuro?'),
                'conocimiento_presente':fields.text('¿Dónde y cómo se puede usar este conocimiento en el presente Proyecto?'),
                'conocimiento_futuro':fields.text('¿Dónde y cómo se puede usar este conocimiento en un futuro Proyecto?'),
                'planos':fields.text('Planos, fotos, sketches que se adjuntan para aclarar la propuesta (Mencionar y adjuntar)'),
                'procedimientos':fields.text('Procedimientos que se mejoraron o que deberían mejorarse a partir de la incorporación de esta "LECCIÓN APRENDIDA"'),
                'observacion':fields.text('Observaciones Generales'),
                }
    _defaults = {  
        'name': '/'
        }
cyg_project_lecciones()

class ir_attachment(osv.osv):
    _inherit = 'ir.attachment'
    _columns = {
                'leccion_id':fields.many2one('cyg.project.lecciones','Proyecto'),
                }
ir_attachment()


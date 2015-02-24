# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today
#    CyG xxxx
#    @autor: Edison Guachamin <edison.guachamin@gmail.com>
#
##############################################################################

import logging
from datetime import datetime
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

class cyg_project_norma(osv.osv):
    _name= 'cyg.project.norma'
    _description = 'Norma'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Norma', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_project_norma()

class cyg_project_hallazgo_categoria(osv.osv):
    _name= 'cyg.project.hallazgo.categoria'
    _description = 'Codigo'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Categoría', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_project_hallazgo_categoria()

class cyg_project_sitio(osv.osv):
    _name= 'cyg.project.sitio'
    _description = 'Sitio'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Sitio', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_project_sitio()

class cyg_project_area(osv.osv):
    _name= 'cyg.project.area'
    _description = 'Area'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Area de Hallazgo', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_project_area()

class cyg_project_grado(osv.osv):
    _name= 'cyg.project.grado'
    _description = 'Grado de Hallazgo'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Grado de Hallazgo', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_project_grado()

class cyg_project_origen(osv.osv):
    _name= 'cyg.project.origen'
    _description = 'Origen'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Origen de Hallazgo', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_project_origen()

class cyg_project_hallazgo_responsable(osv.osv):
    _name= 'cyg.project.hallazgo.responsable'
    _description = 'Responsable'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Responsable', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_project_hallazgo_responsable()

class cyg_project_clausula(osv.osv):
    _name= 'cyg.project.clausula'
    _description = 'Clausula'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Clausula', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                'norma_id':fields.many2one('cyg.project.norma','Norma'),
                }
cyg_project_clausula()
class cyg_project_impacto(osv.osv):
    _name= 'cyg.project.impacto'
    _description = 'Clausula'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Impacto', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_project_impacto()

class cyg_project_grupo_interes_impacto(osv.osv):
    _name= 'cyg.project.grupo.interes.impacto'
    _description = 'Impacto Grupo de Interes'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Impacto', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_project_grupo_interes_impacto()


class cyg_project_causa(osv.osv):
    _name= 'cyg.project.causa'
    _description = 'Causas'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Causa', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_project_causa()
class cyg_project_avance(osv.osv):
    _name= 'cyg.project.avance'
    _description = 'Causas'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Avance', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_project_avance()
class cyg_project_prioridad(osv.osv):
    _name= 'cyg.project.prioridad'
    _description = 'Prioridad'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Prioridad', size=500),
                'code':fields.integer('Peso'),
                'descripcion':fields.text('Descripción'),
                }
cyg_project_prioridad()
class cyg_project_negocio(osv.osv):
    _name= 'cyg.project.negocio'
    _description = 'Unidad de Negocio'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Area de Negocio', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_project_negocio()
class cyg_project_linea_negocio(osv.osv):
    _name= 'cyg.project.linea.negocio'
    _description = 'Linea de Negocio'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Línea de Negocio', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_project_linea_negocio()
class cyg_project_area_riesgo(osv.osv):
    _name= 'cyg.project.area.riesgo'
    _description = 'Areas de Riesgo'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Area de Riesgo', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_project_area_riesgo()
class cyg_project_grupo_cronograma(osv.osv):
    _name= 'cyg.project.grupo.cronograma'
    _description = 'Areas de Riesgo'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Cronograma', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_project_grupo_cronograma()
class cyg_project_fase(osv.osv):
    _name= 'cyg.project.fase'
    _description = 'Fase Proyecto'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Fase de Proyecto', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_project_fase()
class cyg_project_progreso(osv.osv):
    _name= 'cyg.project.progreso'
    _description = 'Progreso Proyecto'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Progreso del Proyecto', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_project_progreso()

class cyg_project_requisito(osv.osv):
    _name= 'cyg.project.requisito'
    _description = 'Progreso Proyecto'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Requisito Aceptacion/Cierre', size=500),
                'code':fields.char('Código', size=500),
                'descripcion':fields.text('Descripción'),
                }
cyg_project_requisito()

class cyg_project_grupo_actividad(osv.osv):
    _name= 'cyg.project.grupo.actividad'
    _description = 'Actividad Proyecto'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Grupo Actividad', size=500),
                'code':fields.integer('Secuenca'),
                'descripcion':fields.text('Descripción'),
                }
cyg_project_grupo_actividad()

class cyg_project_actividad(osv.osv):
    _name= 'cyg.project.actividad'
    _description = 'Actividad Proyecto'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Actividad', size=500),
                'grupo_id':fields.many2one('cyg.project.grupo.actividad','Grupo Actividad',required=1),
                'code':fields.integer('Secuencia'),
                'descripcion':fields.text('Descripción'),
                }
cyg_project_actividad()


class cyg_project_actividad_hallazgo(osv.osv):
    _name= 'cyg.project.actividad.hallazgo'
    _description = 'Actividad Hallazgos'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Actividad', size=500),
                'code':fields.integer('Secuenca'),
                'descripcion':fields.text('Descripción'),
                }
cyg_project_actividad_hallazgo()

class cyg_project_actividad_correctiva(osv.osv):
    _name= 'cyg.project.actividad.correctiva'
    _description = 'Actividad Correctiva'
    def onchange_mayusculas(self, cr, uid, ids, texto, field_name):
        res = {}
        if texto:
            txt1 = cambiarTildes(texto.encode('UTF-8'))
            txt = txt1.upper()
            res['value'] = {field_name: txt}
        return res
    _columns = {
                'name':fields.char('Actividad', size=500),
                'code':fields.char('Code',size=10),
                'descripcion':fields.text('Descripción'),
                }
cyg_project_actividad_correctiva()
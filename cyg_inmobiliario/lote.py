# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today
#    CyG xxxx
#    @autor: Jonathan Finlay <jfinlay@riseup.net>
#
##############################################################################
from openerp.osv import fields, osv


class lote(osv.osv):
    """Clase para la administración de lotes de terreno"""
    _name = 'cyg.lote'
    _description = "Clase para la administración de lotes de terreno"

    _columns = {
        'proyecto_id': fields.many2one('cyg.proyecto',
                                       'Proyecto', required=True),
        'propietario_id': fields.many2one('res.partner',
                                          'Propietario/a del lote', required=True),
        'representante_prop_id': fields.many2one('res.partner',
                                                 'Representante propietario'),
        'predio': fields.char('Predio', size=64, required=True),
        'superficie_bruta': fields.float('Superficie bruta',
                                         digits=(10, 2), required=True),
        'forma': fields.char('Forma', size=64),
        'asolamiento': fields.char('Asolamiento', size=64),
        'iluminacion': fields.char('Iluminación', size=64),
        'topografia': fields.char('Topografía', size=64),
        'pendiente': fields.char('Pendiente', size=64),
        'vistas': fields.char('Vistas', size=64),
        'ventilacion': fields.char('Ventilación', size=64),
        'suelo': fields.char('Suelo', size=64),
        'notaria': fields.integer('N° Notaría'),
        'notario': fields.char('Notario', size=64),
        'fecha_otorgamiento': fields.date('Fecha otorgamiento escritura'),
        'fecha_inscripcion': fields.date('Fecha inscripción'),
        'hipotecado': fields.boolean('Hipotecado'),
        'observaciones': fields.text('Observaciones'),
        'fecha_escritura_hipoteca': fields.date('Fecha escritura hipotecaria'),
        'fecha_inscripcion_hipoteca': fields.date('Fecha inscripción'),
        'notaria_hipoteca': fields.integer('N° Notaría'),
        'notario_hipoteca': fields.char('Notario', size=64),
        'acreedor_hipotecario': fields.char('Acreedor hipotecario', size=64),
    }

lote()

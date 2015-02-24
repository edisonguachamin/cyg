# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today
#    CyG xxxx
#    @author: Jonathan Finlay <jfinlay@riseup.net>
#    @date: 03-06-2014
#    @last_modified: 03-06-2014
#
##############################################################################
from openerp.osv import fields, osv


class estado_civil(osv.osv):
    """Clase para la administración de estados civiles"""
    _name = 'cyg.estado_civil'
    _description = "Clase para la administración de estados civiles"

    _columns = {
        'name': fields.char('Nombre', size=64),
        'description': fields.text('Descripción'),
        }

estado_civil()

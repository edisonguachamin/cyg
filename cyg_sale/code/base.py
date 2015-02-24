# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today
#    CyG xxxx
#    @autor: Jonathan Finlay <jfinlay@riseup.net>
#
##############################################################################
from openerp.osv import fields, osv

class cyg_canal(osv.osv):

    _name = 'cyg.canal'

    _columns = {
                'name': fields.char('Nombre',size=200),
                'sequence': fields.integer('Secuencia'),
                }

cyg_canal()

class cyg_seguimiento_tipo(osv.osv):

    _name = 'cyg.seguimiento_tipo'

    _columns = {
                'name': fields.char('Nombre',size=100),
                'note': fields.text('Descripcion'),
                }

cyg_seguimiento_tipo()

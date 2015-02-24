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
from openerp.osv.expression import get_unaccent_wrapper

class res_users(osv.osv):
    """Herencia para extension de la clase res.users """
    _name = 'res.users'
    _inherit = 'res.users'

    def complete_name(self, cr, uid, id, nombre, apellido, context=None):
        return {'value': {'name': "%s %s" % (apellido, nombre)}}

res_users()


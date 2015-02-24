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

class ir_attachment(osv.osv):
    """Herencia para extension de la clase ir.atttachment """
    _name = 'ir.attachment'
    _inherit = 'ir.attachment'

    def goto_document(self, cr, uid, id, context=None):
        if isinstance(id, list):
            id = id[0]
        doc = self.browse(cr, uid, id, context=context)
        res = {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': doc['res_model'],
                'res_id': doc['res_id'],
                'views': [(False, 'form')],
                'target': 'current',
                'context': context,
            }
        return res

ir_attachment()
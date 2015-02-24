# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today
#    CyG xxxx
#    @author: Jonathan Finlay <jfinlay@riseup.net>
#
##############################################################################

from openerp.osv import fields, osv
import time


class cambio_precios_inmueble_wiz(osv.osv_memory):
    _name = 'cyg.cambio_precios_inmueble_wiz'

    def cambio_precio(self, cr, uid, id, context=None):
        wiz = self.browse(cr, uid, id, context=context)[0]
        if 'active_ids' in context and 'active_model' in context:
            for active_id in context['active_ids']:
                historial_obj = self.pool.get('cyg.historico_precios_inmueble')
                inmueble_obj = self.pool.get(context['active_model'])
                record = inmueble_obj.browse(cr, uid, active_id, context=context)
                historial_obj.create(cr, uid, {'inmueble_id': active_id,
                                               'precio_anterior': record.precio_actual,
                                               'precio_actual': wiz.precio,
                                               'usuario_cambio': uid,
                                               'date': time.strftime('%Y-%m-%d %H:%M:%S')
                                               })
                inmueble_obj.write(cr, uid, active_id, {'precio_actual': wiz.precio})
        return {'type': 'ir.actions.act_window_close'}

    _columns = {
        'precio': fields.float('Precio', digits=(10,10)),
        }

cambio_precios_inmueble_wiz()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

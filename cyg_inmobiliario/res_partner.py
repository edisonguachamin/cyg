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


class res_partner_bank(osv.osv):
    _name = 'res.partner.bank'
    _inherit = 'res.partner.bank'

    def name_get(self, cr, uid, ids, context=None):
        res = []
        name = ''
        for line in self.browse(cr, uid, ids, context=context):
            name = "%s - %s" %(line.bank.name, line.acc_number)
            res.append((line.id, name))

        return res
    
    def onchange_tipo_cuenta(self, cr, uid, ids, cuenta_id, context=None):
        print 'cuenta_id', cuenta_id
        type_obj = self.pool.get('res.partner.bank.type')
        result = {}
        if cuenta_id:
            cuenta_ids = type_obj.search(cr, uid, [('code','=',cuenta_id)])
            if cuenta_ids:
                cuota_info = type_obj.browse(cr, uid,cuenta_ids[0])
                result['tipo_cuenta'] = cuota_info.name
            else:
                result['tipo_cuenta'] = ''
        return {'value': result}
    

    _columns = {
        'proyecto_id': fields.many2one('cyg.proyecto',
                                       'Proyecto inmobiliario'),
        'uso': fields.char('Uso', size=64),
        'tipo_cuenta': fields.char('Tipo Cuenta', size=64),
    }

res_partner_bank()

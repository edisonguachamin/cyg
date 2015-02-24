# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv
from openerp.tools.translate import _

class sale_order(osv.osv):
    _inherit = 'sale.order'
    
    def print_statement(self, cr, uid, ids, context=None):
        '''
        This function prints the invoice and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        datas = {
             'ids': ids,
             'model': 'sale.order',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'cyg_statement',
            'datas': datas,
            'nodestroy' : True
        }

    def sale_pay_customer(self, cr, uid, ids, context=None):
        
        if not ids: return []
        inmueble_id = False
        proyecto_id = False
        bank_id = False
        nro_cuenta = False
        
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'cyg_plan_pagos', 'view_cyg_payment_form')

        inv = self.browse(cr, uid, ids[0], context=context)
        if inv.proyecto_id and inv.proyecto_id.datos_bancarios_ids:
            for x in  inv.proyecto_id.datos_bancarios_ids:
                #Res partner bank
                bank_id = x.id #Res partner bank
                nro_cuenta = x.acc_number
        
        for item in inv.inmuebles_ids:
            inmueble_id = item.inmueble_id.id
                
        return {
            'name':_("Pago Inmueble"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'cyg.payment',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                'default_amount': 0.00,
                'default_reference': inv.name,
                'default_inmueble_id':inmueble_id,
                'close_after_process': True,
                'default_sale_order_id':inv.id,
                'default_proyecto_id':inv.proyecto_id.id,
                'default_bank_id':bank_id,
                'default_nro_cuenta':nro_cuenta,
            }
        }
    
    def sale_pay_devolucion(self, cr, uid, ids, context=None):
        
        if not ids: return []
        inmueble_id = False
        proyecto_id = False
        
        
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'cyg_plan_pagos', 'view_cyg_payment_devolucion_form')

        inv = self.browse(cr, uid, ids[0], context=context)
        if inv.proyecto_id and inv.proyecto_id.datos_bancarios_ids:
            for x in  inv.proyecto_id.datos_bancarios_ids:
                #Res partner bank
                bank_id = x.id #Res partner bank
                nro_cuenta = x.acc_number
        
        for item in inv.inmuebles_ids:
            inmueble_id = item.inmueble_id.id
        
        return {
            'name':_("Registra Devolucion"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'cyg.payment.devolucion',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                'default_valor_devuelto': 0.00,
                'default_inmueble_id':inmueble_id,
                'close_after_process': True,
                'default_proyecto_id':inv.proyecto_id.id,
                'default_sale_id':inv.id,
                'default_type':'Devolucion',
                'default_etapa_id':inv.etapa_id.id,
                'default_bank_id':bank_id,
                'default_nro_cuenta':nro_cuenta,
            }
        }



sale_order()

class sale_inmueble_cuota(osv.osv):
    _inherit = 'cyg.inmueble.cuota'
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        name = ''
        for line in self.browse(cr, uid, ids, context=context):
            name = line.code or '/'
            if line.fecha:
                name = name + ' [' + line.fecha + ']'
            res.append((line.id, name))
        return res
    
    def customer_pay_abono(self, cr, uid, ids, context=None):
        
        if not ids: return []
        inmueble_id = False
        proyecto_id = False
        
        
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'cyg_plan_pagos', 'view_cyg_payment_deposit_form')

        inv = self.browse(cr, uid, ids[0], context=context)
        
        return {
            'name':_("Pago Abono por Descuento"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'cyg.payment.deposit',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                'default_amount': 0.00,
                'default_inmueble_id':inv.inmueble_id and inv.inmueble_id.id,
                'close_after_process': True,
                'default_proyecto_id':inv.project_id.id,
                'default_sale_id':inv.sale_id.id,
                'default_type':'abono',
                'default_cuota_id':ids and ids[0] or False,
                'default_etapa_id':inv.etapa_id.id,
            }
        }
    
    def customer_pay_mora(self, cr, uid, ids, context=None):
        
        if not ids: return []
        inmueble_id = False
        proyecto_id = False
        
        
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'cyg_plan_pagos', 'view_cyg_payment_deposit_mora_form')

        inv = self.browse(cr, uid, ids[0], context=context)
        
        return {
            'name':_("Pago Mora"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'cyg.payment.deposit',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                'default_amount': 0.00,
                'default_inmueble_id':inv.inmueble_id and inv.inmueble_id.id,
                'close_after_process': True,
                'default_proyecto_id':inv.project_id.id,
                'default_sale_id':inv.sale_id.id,
                'default_type':'mora',
                'default_cuota_id':ids and ids[0] or False,
                'default_amount_interes_mora':inv.amount_interes_mora or 0.00,
                'default_date_interes':inv.fecha,
                'default_etapa_id':inv.etapa_id.id,
            }
        }
    
    def customer_pay_extra(self, cr, uid, ids, context=None):
        
        if not ids: return []
        inmueble_id = False
        proyecto_id = False
        
        
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'cyg_plan_pagos', 'view_cyg_payment_deposit_extra_form')

        inv = self.browse(cr, uid, ids[0], context=context)
        
        return {
            'name':_("Pago Extra"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'cyg.payment.deposit',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                'default_amount': 0.00,
                'default_inmueble_id':inv.inmueble_id and inv.inmueble_id.id,
                'close_after_process': True,
                'default_proyecto_id':inv.project_id.id,
                'default_sale_id':inv.sale_id.id,
                'default_type':'extra',
                'default_cuota_id':ids and ids[0] or False,
                'default_etapa_id':inv.etapa_id.id,
            }
        }

    
sale_inmueble_cuota()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

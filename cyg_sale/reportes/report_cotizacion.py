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

import time
from openerp.report import report_sxw

__author__ = 'Edison Guachamin'


class cotizacion(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(cotizacion, self).__init__(cr, uid, name, context=context)
        #print 'context', context
        self.localcontext.update({
            'time': time,
            'get_info':self.get_info,
        })
        self.context = context
        self.valor = 0.00
    
    def get_info(self, o):
        #print '$$$$$$$$$',o
        res ={}
        valor = 0
        bodegas = 0
        total = 0
        if o:
            name = ''
            nro_paqueaderos = ''
            nro_bodegas = ''
            
            if len(o.inmuebles_ids) > 1:
                inmuebles = [str(x.inmueble_id.numero) for x in o.inmuebles_ids if x.inmueble_id and x.inmueble_id.numero ]
                #print 'inmuebles', inmuebles 
                name = ' - '.join(inmuebles)
                
            if len(o.inmuebles_ids) == 1:
                for line in o.inmuebles_ids:
                    if line.inmueble_id:
                        name = line.inmueble_id and line.inmueble_id.numero or '/'
            res['numero'] = name
            for item in o.inmuebles_ids:
                #print '#########',item
                res['area_casa'] = item.inmueble_id and item.inmueble_id.area_cubierta or ''
                total += item.inmueble_id and item.inmueble_id.area_cubierta or 0.00
                res['area_terraza'] = item.inmueble_id and item.inmueble_id.area_terraza or ''
                total += item.inmueble_id and item.inmueble_id.area_terraza or 0.00
                res['area_balcon'] = item.inmueble_id and item.inmueble_id.area_balcon or ''
                total += item.inmueble_id and item.inmueble_id.area_balcon or 0.00
                res['area_patio_privado'] = item.inmueble_id and item.inmueble_id.area_patio_privado or ''
                total += item.inmueble_id and item.inmueble_id.area_patio_privado or 0.00
                print 'item.inmueble_id', item.inmueble_id
                if item.inmueble_id.parqueadero_ids:
                    valor = len(item.inmueble_id.parqueadero_ids)
                    res['parqueaderos'] = valor
                    
                    parqueaderos_ids = item.inmueble_id.parqueadero_ids
                    #print '666666666', parqueaderos_ids
                    #print '999999999', parqueaderos_ids[0]
                    parqueaderos = [str(y.numero) for y in parqueaderos_ids if y.numero ]
                    nro_paqueaderos = ' - '.join(parqueaderos)
                    res['nro_paqueaderos'] = nro_paqueaderos
                    
                #print 'item.inmueble_id.bodega_ids', item.inmueble_id.bodega_ids
                if item.inmueble_id.bodega_ids:
                    bodegas = len(item.inmueble_id.bodega_ids)
                    res['bodegas'] = bodegas
                    bodegas_ids = item.inmueble_id.bodega_ids
                    arr_bodegas = [str(z.numero) for z in bodegas_ids if z.numero ]
                    nro_bodegas = ' - '.join(arr_bodegas)
                    res['nro_bodegas'] = nro_bodegas
                res['total'] = total
    
        return res
#from netsvc import Service
#del Service._services['report.sale.order']

report_sxw.report_sxw('report.cotizacion','sale.order',
                      'addons/cyg_sale/reportes/cotizacion.rml',parser=cotizacion,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

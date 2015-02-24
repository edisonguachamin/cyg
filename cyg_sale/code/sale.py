# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today Jonathan Finlay <jfinlay@riseup.net>.
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
import datetime

from dateutil.relativedelta import *
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import re
from lxml.html.builder import INS

import tools


class proyecto_inmueble(osv.Model):
    #_name = 'sale.order'
    _inherit = 'cyg.proyecto_inmueble'
    
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
           
            ids = self.search(cr, user, [('numero','ilike',name)]+ args, limit=limit, context=context)
            
            if not ids:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                ids = set()
                ids.update(self.search(cr, user, args + [('name',operator,name)], limit=limit, context=context))
                if len(ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    ids.update(self.search(cr, user, args + [('numero',operator,name)], limit=(limit-len(ids)), context=context))
                ids = list(ids)
            if not ids:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(cr, user, [('numero','=', res.group(2))] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result
    _columns = {
                'partner_id':fields.many2one('res.partner','Propietario'),
                'sale_id':fields.many2one('sale.order','Orden de Venta'),
                'fecha_entrega': fields.date('Fecha de entrega')
                }
proyecto_inmueble()


class sale_order(osv.Model):
    #_name = 'sale.order'
    _inherit = 'sale.order'
    
    def _format_date(self, date):
        if date:
            campos = date.split('-')
            date = datetime.date(int(campos[0]), int(campos[1]), int(campos[2]))
            return date
    
    def _get_inmuebles(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.inmueble.line').browse(cr, uid, ids, context=context):
            result[line.sale_id.id] = True
        return result.keys()
    
    def _get_extras(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('cyg.inmuebles.extras').browse(cr, uid, ids, context=context):
            result[line.sale_id.id] = True
        return result.keys()
    
    def _get_cuotas(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('cyg.inmueble.cuota').browse(cr, uid, ids, context=context):
            result[line.sale_id.id] = True
        return result.keys()
    
    
    def _cuota_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            #print 'order', order.poreserva
            res[order.id] = {
                'cuota_cliente': 0.00,
                'cuota_promotor': 0.00,
            }
            val = val1 = 0.00
            cur = order.pricelist_id.currency_id
            for line in order.cuotas_ids:
                val1 += line.promotor
                val += line.cliente
            res[order.id]['cuota_cliente'] = val
            res[order.id]['cuota_promotor'] = val1
        return res
    
    def _inmueble_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        #cur_obj = self.pool.get('res.currency')
        #cur = order.pricelist_id.currency_id
        cur = cur_obj.browse(cr, uid, 3)
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            #print 'order', order.poreserva
            res[order.id] = {
                'inmueble_total': 0.00,
                'extra_total': 0.00,
                'cuotas_total': 0.00,
                'reserva':0.00,
                'entrada':0.00,
                'financiamiento':0.00,
                'capital':0.00,
                'solca':0.00,
                'creserva':0.00,
                'centrada':0.00,
                'cfinanciamiento':0.00,
            }
            val = val1 = val2 = 0.00
            
            for line in order.inmuebles_ids:
                val1 += line.precio
            for line in order.extras_ids:
                val += line.price_subtotal
            for line in order.cuotas_ids:
                if line.concepto in ('penalizacion', 'extraordinaria') and line.state in ('done', 'paid', 'desistido'):
                    val2 += line.cliente
                
            res[order.id]['inmueble_total'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['extra_total'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['cuotas_total'] = cur_obj.round(cr, uid, cur, val2)
            res[order.id]['total'] = val1 + val
            
            res[order.id]['reserva'] = cur_obj.round(cr, uid, cur,(order.poreserva * res[order.id]['total'])/100)
            res[order.id]['entrada'] = cur_obj.round(cr, uid, cur,(order.poentrada * res[order.id]['total']) /100)
            res[order.id]['financiamiento'] = cur_obj.round(cr, uid, cur,(order.pofinanciamiento * res[order.id]['total'])/100)
            
            res[order.id]['creserva'] = cur_obj.round(cr, uid, cur,(order.pocreserva * res[order.id]['total'])/100)
            res[order.id]['centrada'] = cur_obj.round(cr, uid, cur,(order.pocentrada * res[order.id]['total']) /100)
            res[order.id]['cfinanciamiento'] = cur_obj.round(cr, uid, cur,(order.pocfinanciamiento * res[order.id]['total'])/100)
            
            res[order.id]['capital'] = res[order.id]['cfinanciamiento']
            res[order.id]['solca'] = res[order.id]['cfinanciamiento'] * 0.5/100
            
        return res
    
    def onchange_fechas(self, cr, uid, ids, entrega,inicial):
        #print '##########onchange_fecha_entrega', entrega
        #print '##########onchange_field_name2', inicial
        res = {'value':{}}
        now = datetime.date.today()
        if entrega and inicial:
            fecha_inicial = self._format_date(inicial)
            fecha_entrega = self._format_date(entrega)
            if fecha_entrega > fecha_inicial:
                dias = (fecha_entrega - fecha_inicial).days
                meses = dias/30 
                res['value']['meses'] = meses
            else:
                return {'value':{'meses':0,'fecha_entrega':''},
                        'warning':{'title': "Error", "message": "La fecha inicial debe ser menor que la fecha final"}}
        return res
    
    def onchange_meses(self, cr, uid, ids, field_name,fecha_inicial):
        #print '##########', ids
        res = {'value':{}}
        now = datetime.date.today()
        
        cuota_obj = self.pool.get('cyg.inmueble.cuota')
        lineas = []
        if field_name and fecha_inicial:
            fecha_inicial = self._format_date(fecha_inicial)
            date = (fecha_inicial + relativedelta(months=+field_name)).strftime('%Y-%m-%d')
            res['value']['fecha_entrega'] = date
            res['value']['cuotas_ids'] = []
            for item in self.browse(cr, uid, ids):
                for line in item.cuotas_ids:
                    lineas.append(line.id)
                cuota_obj.unlink(cr, uid,lineas)
                    
        return res
    
    def valida_porcentaje(self,valor):
        if valor:
            if valor < 0 or valor > 100:
                return False
            else:
                return True
    
    def onchange_porcentaje_cliente(self, cr, uid,ids,p1,p2,p3,amount):
        suma = 0
        res = {'value':{}}
        if p1:
            if self.valida_porcentaje(p1):
                suma += p1
                res['value']['creserva'] = amount * p1 * 0.01
            else:
                res['value']['pocreserva'] = 0
                res['warning'] = {'title': "Aviso", "message": "El valor del porcentaje debe estar entre 0 y 100"}
        
        if p2:
            if self.valida_porcentaje(p2):
                suma += p2
                res['value']['centrada'] = amount * p2 * 0.01
            else:
                #res['value'] = {c2:0, 'porcentaje_total': suma}
                res['value']['pocentrada'] = 0
                res['warning'] = {'title': "Aviso", "message": "El valor del porcentaje debe estar entre 0 y 100"}
        
        if p3:
            if self.valida_porcentaje(p3):
                suma += p3
                res['value']['cfinanciamiento'] = amount * p3 * 0.01
                res['value']['capital'] = amount * p3 * 0.01
                res['value']['solca'] = amount * p3  * 0.05
            else:
                #res['value'] = {c3:0, 'porcentaje_total': suma}
                res['value']['pocfinanciamiento'] = 0
                res['warning'] = {'title': "Aviso", "message": "El valor del porcentaje debe estar entre 0 y 100"}
        
        if suma > 100:
            res['value']['pocfinanciamiento'] = 0
            res['warning'] = {'title': "Aviso", "message": "La suma de los porcentajes suma mas de 100"}
        
        #print 'res', res
        return res
    
    def onchange_porcentaje_propuesto(self, cr, uid,ids,p1,p2,p3,amount):
        suma = 0
        res = {'value':{}}
        if p1:
            if self.valida_porcentaje(p1):
                suma += p1
                res['value']['reserva'] = amount * p1 * 0.01
            else:
                res['value']['poreserva'] = 0
                res['value']['reserva'] = 0
                res['warning'] = {'title': "Aviso", "message": "El valor del porcentaje debe estar entre 0 y 100"}
        
        if p2:
            if self.valida_porcentaje(p2):
                suma += p2
                res['value']['entrada'] = amount * p2 * 0.01
            else:
                #res['value'] = {c2:0, 'porcentaje_total': suma}
                res['value']['poentrada'] = 0
                res['value']['entrada'] = 0
                res['warning'] = {'title': "Aviso", "message": "El valor del porcentaje debe estar entre 0 y 100"}
        
        if p3:
            if self.valida_porcentaje(p3):
                suma += p3
                res['value']['financiamiento'] = amount * p3 * 0.01
                #res['value']['capital'] = amount * p3 * 0.01
                #res['value']['solca'] = amount * p3  * 0.05
            else:
                #res['value'] = {c3:0, 'porcentaje_total': suma}
                res['value']['pocfinanciamiento'] = 0
                res['value']['financiamiento'] = 0
                res['warning'] = {'title': "Aviso", "message": "El valor del porcentaje debe estar entre 0 y 100"}
        
        if suma > 100:
            res['value']['pofinanciamiento'] = 0
            res['warning'] = {'title': "Aviso", "message": "La suma de los porcentajes suma mas de 100"}
        
        #print 'res', res
        return res
    
    def button_porcentage(self, cr, uid, ids, context={}):
        cur_obj = self.pool.get('res.currency')
        cur = cur_obj.browse(cr, uid, 3)
        cuota_obj = self.pool.get('cyg.inmueble.cuota')
        
        creserva = centrada = cfinanciamiento = 0.00
        
        for item in self.browse(cr, uid, ids):
            lineas = []
            for line in item.cuotas_ids:
                lineas.append(line.id)
            cuota_obj.unlink(cr, uid,lineas)
            sum = cur_obj.round(cr, uid, cur,item.pocreserva + item.pocentrada + item.pocfinanciamiento)
            if sum > 100:
                raise osv.except_osv(('Aviso !'), u'El valor de porcentajes del Plan de Pagos Propuesto supera el 100%')
            if sum < 100:
                raise osv.except_osv(('Aviso !'), u'El valor de porcentajes del Plan de Pagos Propuesto no suma 100%')
        return True
    
    def get_dia_habil(self,fecha_pago):
        dia_pago =self._format_date(fecha_pago)
        if dia_pago.weekday()==5:
            dia_pago=dia_pago + relativedelta(days=+2)
        elif dia_pago.weekday()==6:
            dia_pago= dia_pago + relativedelta(days=+1)
        return dia_pago
    
    def button_table(self, cr, uid,ids,context={}):
        #print 'button_table', context
        dict ={}
        cuota_obj = self.pool.get('cyg.inmueble.cuota')
        valor_cliente = 0.00
        valor_promotor = 0.00
        ultima_id = False
        cur_obj = self.pool.get('res.currency')
        cur = cur_obj.browse(cr, uid, 3)
        amount_original = amount_cliente = 0.00
        
        self.button_porcentage(cr, uid, ids, context=context)
        total = 0.00
        for item in self.browse(cr, uid, ids,context=context):
            inmueble_id = False
            project_id = item.proyecto_id and item.proyecto_id.id or False 
            etapa_id = item.etapa_id and item.etapa_id.id or False 
            for line in item.inmuebles_ids:
                inmueble_id = line.inmueble_id.id
                #print 'etapa',etapa_id 
                break
            now = self._format_date(item.fecha_inicial)
            n = item.meses
            i = 1
            if item.cuotas_ids:
                break
            if item.meses:
                valor_cliente = item.centrada + item.creserva + item.cfinanciamiento
                valor_promotor = item.entrada + item.reserva + item.financiamiento
                cuota = cur_obj.round(cr, uid, cur,round(item.entrada / item.meses,2))
                cuota2 = cur_obj.round(cr, uid, cur,round(item.centrada / item.meses,2))
                #print 'cuota2', cuota2
                dia_pago = self.get_dia_habil(item.fecha_inicial)
                amount_original += item.reserva
                amount_cliente += item.creserva
                dict = {'cuota': '1',
                        'name':dia_pago.strftime('%A, %d de %B del %Y'),
                        'sale_id':item.id,
                        'fecha':dia_pago.strftime('%Y-%m-%d'),
                        'concepto':'reserva',
                        'partner_id':item.partner_id.id,
                        'inmueble_id':inmueble_id,
                        'project_id':project_id,
                        'etapa_id':etapa_id,
                        'promotor':cur_obj.round(cr, uid, cur,item.reserva),
                        'cliente':cur_obj.round(cr, uid, cur,item.creserva),
                        'pendiente':cur_obj.round(cr, uid, cur,item.creserva),
                        'pagado':0.0,
                        'user_id':uid}
                #print 'valores 1', dict
                cuota_obj.create(cr, uid, dict,context=context)
            else:
                raise osv.except_osv(('Aviso !'), u'En número de meses debe ser mayor a 0 para continuar')
            
            if not item.total:
                raise osv.except_osv(('Aviso !'), ('El total de cotizacion debe ser mayor a 0 para continuar elija un inmueble!'))
            else:
                total = item.total
            
            while  i <= n:
                fecha_pago = (now + relativedelta(months=+i)).strftime('%Y-%m-%d')
                dia_pago = self.get_dia_habil(fecha_pago)
                amount_original += cuota 
                amount_cliente += cuota2
                dict = {'cuota':i,
                        'name':dia_pago.strftime('%A, %d de %B del %Y'),
                        'partner_id':item.partner_id.id,
                        'sale_id':item.id,
                        'fecha':dia_pago.strftime('%Y-%m-%d'),
                        'concepto':'entrada',
                        'inmueble_id':inmueble_id,
                        'project_id':project_id,
                        'etapa_id':etapa_id,
                        'promotor':cur_obj.round(cr, uid, cur,cuota),
                        'cliente':cur_obj.round(cr, uid, cur,cuota2),
                        'pendiente':cur_obj.round(cr, uid, cur,cuota2),
                        'pagado':0.0,
                        'user_id':uid}
                #print 'valores 2', dict
                ultima_id = cuota_obj.create(cr, uid, dict,context=context)
                if i==n:#Financiamiento
                    fecha_pago = (now + relativedelta(months=+i+1)).strftime('%Y-%m-%d')
                    dia_pago = self.get_dia_habil(fecha_pago)
                    amount_original += item.financiamiento
                    amount_cliente += item.cfinanciamiento
                    dict = {'cuota':i+1,
                            'name':dia_pago.strftime('%A, %d de %B del %Y'),
                            'partner_id':item.partner_id.id,
                            'sale_id':item.id,
                            'fecha':dia_pago.strftime('%Y-%m-%d'),
                            'concepto':'financiamiento',
                            'inmueble_id':inmueble_id,
                            'project_id':project_id,
                            'etapa_id':etapa_id,
                            'promotor':cur_obj.round(cr, uid, cur,item.financiamiento),
                            'cliente':cur_obj.round(cr, uid, cur,item.cfinanciamiento),
                            'pendiente':cur_obj.round(cr, uid, cur,item.cfinanciamiento),
                            'pagado':0.00,
                            'user_id':uid}
                    #print 'valores 3', dict
                    cuota_obj.create(cr, uid, dict,context=context)
                i += 1
                
            #print "amount_original",amount_original
            #print "amount_cliente",amount_cliente
            diff_cliente = abs(amount_cliente-total)
            diff_promotor = abs(amount_original-total)
            #print "diff_cliente",diff_cliente
            #print "diff_promotor",diff_promotor
            #print "item", total
            if amount_cliente > total:
                cuota_obj.write(cr, uid, [ultima_id],{'cliente':cuota2-diff_cliente,'pendiente':cuota2-diff_cliente})
            else:
                cuota_obj.write(cr, uid, [ultima_id],{'cliente':cuota2+diff_cliente,'pendiente':cuota2+diff_cliente})
        
            if amount_original > total:
                cuota_obj.write(cr, uid, [ultima_id],{'promotor':cuota-diff_promotor})
            else:
                cuota_obj.write(cr, uid, [ultima_id],{'promotor':cuota+diff_promotor})
        #self.write(cr, uid,ids,{'is_generate':True,'cuota_cliente':valor_cliente,'cuota_promotor':valor_promotor})            
        return True
    
    def fnt_cuota(self, k,im,t):
        #k=capital
        #im= tasa de interes mensual
        #t=tiempo
        c = k * ( im*pow(1+im,t)/(pow(1+im,t)-1))
        return c + 30
    
    def button_credito (self, cr, uid, ids, context={}):
        plazo= [10,15,20,25]
        for item in self.browse(cr, uid, ids):
            if not item.plazo:
                raise osv.except_osv(('Aviso !'), ('El plazo debe ser mayor a 0'))
            
            if not item.taza:
                raise osv.except_osv(('Aviso !'), ('La taza debe ser mayor a 0'))
            
            if not item.cfinanciamiento:
                raise osv.except_osv(('Aviso !'), ('El financiamiento de ser mayor a 0'))
            
            financiamiento = item.cfinanciamiento or item.financiamiento
            
            solca = financiamiento * 0.5/100
            capital = financiamiento + solca
            im = (item.taza/100)/12
            diez =self.fnt_cuota(capital,im, 10*12)
            quince =self.fnt_cuota(capital,im, 15*12)
            veinte =self.fnt_cuota(capital,im, 20*12)
            veinte_cinco =self.fnt_cuota(capital,im, 25*12)
            cuota_mensual = self.fnt_cuota(capital,im, item.plazo*12)
            ingreso_mensual = cuota_mensual/0.33 
        return self.write(cr, uid, ids, {'diez':diez,'quince':quince,'veinte':veinte,'veinte_cinco':veinte_cinco,
                                         'cuota_mensual':cuota_mensual,'ingreso_mensual':ingreso_mensual})
    
    def onchange_capital(self, cr, uid, ids, field_name):
        res = {'value':{}}
        if field_name:
            res['value']['solca'] = field_name * 0.5/100 
        return res
    
    def attachment_tree_view(self, cr, uid, ids, context):
        """ View a list of projects attachments """

        domain = [
            ('res_model', '=', 'sale.order'),
            ('res_id', 'in', ids),
            ]
        res_id = ids and ids[0] or False
        return {
            'name': 'Adjuntos',
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, res_id)
        }
    
    def cuotas_tree_view(self, cr, uid, ids, context):
        """ View a list of cuotas """

        domain = [
            ('sale_id', 'in', ids),
            ]
        res_id = ids and ids[0] or False
        return {
            'name': 'Cuotas',
            'domain': domain,
            'res_model': 'cyg.inmueble.cuota',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, res_id)
        }
    
    def pagos_tree_view(self, cr, uid, ids, context):
        """ View a list of cuotas """

        domain = [
            ('sale_order_id', 'in', ids),
            ]
        res_id = ids and ids[0] or False
        return {
            'name': 'Pagos',
            'domain': domain,
            'res_model': 'cyg.payment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, res_id)
        }
        
    def button_send_to_approval(self, cr, uid, ids,context={}):
        #print 'button_send_to_approval',context
        cuota_obj = self.pool.get('cyg.inmueble.cuota')
        unlink_ids = []
        write_ids = []
        primera_cuota =''
        ultima_cuota =''
        total_inmuebles = total_extras = total_cuotas=0.00
        meses =0
        for item in self.browse(cr, uid, ids):
            inmueble_id =False
            for im in item.inmuebles_ids:
                inmueble_id = im.inmueble_id.id
                self.pool.get('cyg.proyecto_inmueble').write(cr, uid,[im.inmueble_id.id],{'state':'disponible'})
                self.pool.get('sale.inmueble.line').write(cr, uid,[im.id],{'state':'disponible'})
            for line in item.cuotas_ids:
                if not line.cliente:
                    unlink_ids.append(line.id)
                else:
                    write_ids.append(line.id)
            #print 'write_ids', write_ids
            self.pool.get('cyg.inmueble.cuota').unlink(cr, uid, unlink_ids)
            n = 1
            for x in write_ids:
                if n==1:
                    cuota_info = cuota_obj.browse(cr, uid,x)
                    primera_cuota = self._format_date(cuota_info.fecha)
                    ultima_cuota = self._format_date(cuota_info.fecha)
                else:
                    cuota_info = cuota_obj.browse(cr, uid,x)
                    ultima_cuota = self._format_date(cuota_info.fecha)
                dict ={'state':'sent','cuota':n}
                info_cuota = cuota_obj.browse(cr,uid,x)
                if not info_cuota.inmueble_id:
                    dict.update({'inmueble_id':inmueble_id})
                #print 'dict', dict    
                cuota_obj.write(cr, uid,[x],dict,context=context)
                n+=1
            #print 'primera_cuota',primera_cuota
            #print 'ultima_cuota',ultima_cuota
            if ultima_cuota and primera_cuota:
                if ultima_cuota > primera_cuota:
                    dias = (ultima_cuota - primera_cuota).days
                    meses = dias/30
                else:
                    dias = (primera_cuota - ultima_cuota).days
                    meses = dias/30
            else:
                 raise osv.except_osv(('Aviso !'), u'No existe cuotas con valor en el cliente llene correctamente las cuotas!')
                
        return self.write(cr,uid,ids,{'state':'sent','fecha_inicial':primera_cuota,'fecha_entrega':ultima_cuota,'meses':meses})
    
    def button_approval(self, cr, uid, ids,context={}):
        for item in self.browse(cr, uid, ids):
            for im in item.inmuebles_ids:
                self.pool.get('cyg.proyecto_inmueble').write(cr, uid,[im.inmueble_id.id],{'state':'reservado',
                                                                                          'partner_id':item.partner_id.id,
                                                                                          'sale_id':item.id,
                                                                                          #'precio_actual':item.total
                                                                                          })
                self.pool.get('sale.inmueble.line').write(cr, uid,[im.id],{'state':'reservado'})
            for line in item.cuotas_ids:
                self.pool.get('cyg.inmueble.cuota').write(cr, uid, [line.id],{'state':'reservado'})
        return self.write(cr,uid,ids,{'state':'approval','amount_pending':item.total})
    
    def button_confirm_sale(self, cr, uid, ids,context={}):
        inmueble_obj = self.pool.get('cyg.proyecto_inmueble')
        historial_obj = self.pool.get('cyg.historico_precios_inmueble')
        for item in self.browse(cr, uid, ids):
            for im in item.inmuebles_ids:
                info_inmueble = inmueble_obj.browse(cr, uid,im.inmueble_id.id)
                inmueble_obj.write(cr, uid,[im.inmueble_id.id],{'state':'vendido','partner_id':item.partner_id.id,
                                                                'sale_id':item.id})
                self.pool.get('sale.inmueble.line').write(cr, uid,[im.id],{'state':'vendido'})
                if im.precio != info_inmueble.precio_actual:
                    precio_nuevo = im.precio 
                    historial_obj.create(cr, uid, {'inmueble_id': im.inmueble_id.id,
                                               'precio_anterior': im.inmueble_id.precio_actual,
                                               'precio_actual': precio_nuevo,
                                               'usuario_cambio': uid,
                                               'date': time.strftime('%Y-%m-%d %H:%M:%S')
                                               })
                    inmueble_obj.write(cr, uid, [im.inmueble_id.id], {'precio_actual': precio_nuevo})
            for line in item.cuotas_ids:
                self.pool.get('cyg.inmueble.cuota').write(cr, uid, [line.id],{'state':'done'})
        #return self.write(cr,uid,ids,{'state':'done','date_order': time.strftime('%Y-%m-%d'),'amount_pending':item.total})
        return self.write(cr,uid,ids,{'state':'done','date_order':item.date_order or time.strftime('%Y-%m-%d'),'amount_pending':item.total})
    
    def button_draft_sale(self, cr, uid, ids,context={}):
        for item in self.browse(cr, uid, ids):
            for im in item.inmuebles_ids:
                self.pool.get('cyg.proyecto_inmueble').write(cr, uid,[im.inmueble_id.id],{'state':'disponible'})
                self.pool.get('sale.inmueble.line').write(cr, uid,[im.id],{'state':'draft'})
            for line in item.cuotas_ids:
                self.pool.get('cyg.inmueble.cuota').write(cr, uid, [line.id],{'state':'draft'})
        return self.write(cr,uid,ids,{'state':'draft','amount_pending':0.00})
    
    def button_no_approval_sale(self, cr, uid, ids,context={}):
        for item in self.browse(cr, uid, ids):
            for im in item.inmuebles_ids:
                self.pool.get('cyg.proyecto_inmueble').write(cr, uid,[im.inmueble_id.id],{'state':'disponible'})
                self.pool.get('sale.inmueble.line').write(cr, uid,[im.id],{'state':'draft'})
            for line in item.cuotas_ids:
                self.pool.get('cyg.inmueble.cuota').write(cr, uid, [line.id],{'state':'draft'})
        return self.write(cr,uid,ids,{'state':'no_approval'})
    
    def button_cancel_sale(self, cr, uid, ids,context={}):
        for item in self.browse(cr, uid, ids):
            for im in item.inmuebles_ids:
                self.pool.get('cyg.proyecto_inmueble').write(cr, uid,[im.inmueble_id.id],{'state':'disponible'})
                self.pool.get('sale.inmueble.line').write(cr, uid,[im.id],{'state':'cancel'})
            for line in item.cuotas_ids:
                self.pool.get('cyg.inmueble.cuota').write(cr, uid, [line.id],{'state':'cancel'})
        return self.write(cr,uid,ids,{'state':'cancel'})
    
    
    def button_desistir_sale(self, cr, uid, ids, context=None):
        if not ids: return []
        inmueble_id = False
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'cyg_sale', 'view_cyg_inmueble_desistimiento_form')

        inv = self.browse(cr, uid, ids[0], context=context)
        for item in inv.inmuebles_ids:
            inmueble_id = item.inmueble_id.id
        return {
            'name':_("Desistimiento"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'cyg.inmueble.desistimiento',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_residual': inv.amount_pending,
                'default_total': inv.total,
                'default_valor_recaudado': inv.total - inv.amount_pending,
                'default_inmueble_id':inmueble_id,
                'default_sale_id':inv.id,
                
            }
        }
    
    def onchage_simulacion(self, cr, uid,ids,field_name):
        res = {'value':{}}
        #now = datetime.date.today()
        cuota_obj = self.pool.get('cyg.inmueble.cuota')
        lineas = []
        if field_name:
            #res['value']['fecha_entrega'] = date
            res['value']['cuotas_ids'] = []
            for item in self.browse(cr, uid, ids):
                for line in item.cuotas_ids:
                    lineas.append(line.id)
                    
                cuota_obj.unlink(cr, uid,lineas)
        return res
    
    def _name_inmueble(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        
        for order in self.browse(cr, uid, ids, context=context):
            #print 'order', order.poreserva
            name = ''
            if len(order.inmuebles_ids) > 1:
                inmuebles = [str(item.inmueble_id.numero) for item in order.inmuebles_ids if item.inmueble_id and item.inmueble_id.numero ]
                print 'inmuebles', inmuebles 
                name = ' - '.join(inmuebles)
                
            if len(order.inmuebles_ids) == 1:
                for line in order.inmuebles_ids:
                    if line.inmueble_id:
                        name = line.inmueble_id and line.inmueble_id.numero or '/' 
            res[order.id]= name
        return res
    
    def _fnt_valor_cliente(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        
        for order in self.browse(cr, uid, ids, context=context):
            #print 'order', order.poreserva
            res[order.id] = {
                'creserva': 0.00,
                'centrada': 0.00,
                'cfinanciamiento': 0.00,
                'capital':0.00,
                'solca':0.00,
            }
            res[order.id]['creserva']= order.total * order.pocreserva * 0.01
            res[order.id]['centrada']= order.total * order.pocentrada * 0.01
            res[order.id]['cfinanciamiento']= order.total * order.pocfinanciamiento * 0.01
            res[order.id]['capital']= res[order.id]['cfinanciamiento']
            res[order.id]['solca']= res[order.id]['cfinanciamiento'] * 0.5*0.01
        return res
    
    def _fnt_valor_propuesto(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        
        for order in self.browse(cr, uid, ids, context=context):
            #print 'order', order.poreserva
            res[order.id] = {
                'reserva': 0.00,
                'entrada': 0.00,
                'financiamiento': 0.00,
                #'capital':0.00,
                #'solca':0.00,
            }
            res[order.id]['reserva']= order.total * order.poreserva * 0.01
            res[order.id]['entrada']= order.total * order.poentrada * 0.01
            res[order.id]['financiamiento']= order.total * order.pofinanciamiento * 0.01
            #res[order.id]['capital']= res[order.id]['cfinanciamiento']
            #res[order.id]['solca']= res[order.id]['cfinanciamiento'] * 0.5*0.01
            
        return res
    
    selection_list = [('draft', 'Borrador'),('sent', 'Enviada a Aprobacion'),
                                            ('approval', 'Aprobada'),
                                            ('no_approval', 'No Aprobada'),
                                            ('cancel', 'Cancelled'),
                                            ('waiting_date', 'Waiting Schedule'),
                                            ('progress', 'Sales Order'),
                                            ('manual', 'Sale to Invoice'),
                                            ('invoice_except', 'Invoice Exception'),
                                            ('done', 'Venta Realizada'),
                                            ('desistido', 'Desistida'),
                                            ('paid','Pagada'),
                                            ('overpaid','Sobrepagada'),
                                            
                                            ]
    def create(self, cr, uid, vals, context={}):
        #print 'create vals', vals
        cur_obj = self.pool.get('res.currency')
        cur = cur_obj.browse(cr, uid, 3)
        cliente = promotor = 0.00
        if 'cuotas_ids' in vals:
            val = [ s[2] for s in vals.get('cuotas_ids') if s[0] == 0]
            if val:
                for x in val:
                    #print 'x', x
                    cliente += cur_obj.round(cr, uid, cur,x.get('cliente',0.00))
                    promotor += cur_obj.round(cr, uid, cur,x.get('promotor',0.00))
        
        amount = cur_obj.round(cr, uid, cur,promotor - cliente)
        #print 'amount',amount
        if abs(amount):
            raise osv.except_osv(('Aviso !'), u'El Total de Cuotas Promotor difiere del Total de Cuotas Cliente en '+str(amount)+' en el plan de'\
                                 ' pagos. Para continuar ajuste el valor en la linea de cuotas')
                
        res_id = super(sale_order, self).create(cr, uid, vals, context)
        return res_id
    
    
    
    def write(self, cr, uid, ids, vals, context=None):
        #TODO: process before updating resource
        #print 'vals write cabecera', vals
        #print 'contexte', context
        cur_obj = self.pool.get('res.currency')
        cuotas_obj = self.pool.get('cyg.inmueble.cuota')
        cur = cur_obj.browse(cr, uid, 3)

        promotor = cliente = total = 0.00
        org = []
        mod = []
        rm = []
        state = ''
        #val=dp.get_precision('Account')
        #print "digits_compute=dp.get_precision('Account')",val
        if 'cuotas_ids' in vals:
            val = [ s[2] for s in vals.get('cuotas_ids') if s[0] == 0]
            
            rw = [ s for s in vals.get('cuotas_ids') if s[0] == 1]
            
            mod = [ s[1] for s in vals.get('cuotas_ids') if s[0] == 1]
            
            rm = [ s[1] for s in vals.get('cuotas_ids') if s[0] == 2]
            #Valores Nuevos 
            if val:
                for x in val:
                    #print '##############x', x
                    cliente += cur_obj.round(cr, uid, cur,x.get('cliente',0.00))
                    promotor += cur_obj.round(cr, uid, cur,x.get('promotor',0.00))
                    
            #Valores rescritos [1, 1325, {'cliente': 66.67}]
            if rw:
                for x in rw:
                    #print 'x',x
                    if 'cliente' in x[2]: 
                        cliente += cur_obj.round(cr, uid, cur,x[2].get('cliente',0.00))
                    else:
                        info = cuotas_obj.browse(cr,uid,x[1])
                        cliente += cur_obj.round(cr, uid, cur,info.cliente)
                    if 'promotor' in x[2]:
                        promotor += cur_obj.round(cr, uid, cur,x[2].get('promotor',0.00))
                    else:
                        info = cuotas_obj.browse(cr,uid,x[1])
                        promotor += cur_obj.round(cr, uid, cur,info.promotor)
                        
        for item in self.browse(cr, uid, ids):
            total = item.total
            state = item.state
            cuotas_ids = [ x.id for x in item.cuotas_ids if x.id not in (mod + rm)]
            #print 'cuotas_ids', cuotas_ids
            for cuota in cuotas_obj.browse(cr, uid, cuotas_ids):
                promotor += cur_obj.round(cr, uid, cur,cuota.promotor)
                cliente += cur_obj.round(cr, uid, cur,cuota.cliente)
                
        #print 'promotor',round(promotor,2)
        #print 'cliente',round(cliente,2)
        amount = cur_obj.round(cr, uid, cur,promotor - cliente)
        #print 'amount',amount
        total_venta = cliente
        
        #print 'state', state
        
        band = True
        if state != 'draft' and vals.get('state') =='draft':
            #print 'entra donde no debe'
            state = 'done'
            band = False
        if 'state' in vals and band:
            state = vals.get('state')
        #print 'state final', state
        if abs(amount) and state=='draft':
            raise osv.except_osv(('Aviso !'),
                                 u'El Total de Cuotas Promotor difiere del Total de Cuotas Cliente en '+str(amount)+' en el plan de'\
                                 ' pagos. Para continuar ajuste el valor en la linea de cuotas')
        #print 'total_venta', total_venta  
        #print 'total', total
        
        res = super(sale_order, self).write(cr, uid, ids, vals, context)
        diff = cur_obj.round(cr, uid, cur,total_venta - total)
        #print 'diff', diff
        if vals.get('state','draft')=='sent':
            if diff:
                raise osv.except_osv(('Aviso !'),
                                     u'El total de las cuotas de cliente es diferente del total de inmuebles corrija para continuar')
        
        return res

    _columns = {
                'state': fields.selection(selection_list, 'Estado', readonly=True,select=True),
                'via_mail':fields.boolean('Via mail', required=False), 
                'via_telemarketing':fields.boolean('Telemarketing', required=False),
                'via_valla_proyecto':fields.boolean('Vallas Proyecto', required=False),
                'via_vallas_publicitarias':fields.boolean('Vallas Publicitarias', required=False),
                'via_feria':fields.boolean('Feria', required=False),
                'via_revista':fields.boolean('Revista', required=False),
                'via_referido_cliente':fields.boolean('Referido Cliente', required=False),
                'via_referido_empelado':fields.boolean('Referido empleado', required=False),
                'via_radio':fields.boolean('Radio', required=False),
                'via_volante':fields.boolean('Volante', required=False),
                'via_tv':fields.boolean('Tv', required=False),
                'via_internet':fields.boolean('Internet', required=False),
                'proyecto_id':fields.many2one('cyg.proyecto','Proyecto'),
                'etapa_id':fields.many2one('cyg.proyecto_etapa','Etapa'),
                'inmuebles_ids':fields.one2many('sale.inmueble.line','sale_id','Inmuebles'),
                'extras_ids':fields.one2many('cyg.inmuebles.extras','sale_id','Extras'),
                'canal_ids':fields.one2many('cyg.sale.canal','sale_id','Canales de Contacto'),
                'inmueble_total':fields.function(_inmueble_all, digits_compute=dp.get_precision('Account'), string='Inmueble',
                    store={
                        'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['inmuebles_ids'], 10),
                        'sale.inmueble.line': (_get_inmuebles, ['precio', 'cantidad'], 10),
                    },
                    multi='suma', help="Total de Inmueble."),
                'extra_total':fields.function(_inmueble_all, digits_compute=dp.get_precision('Account'), string='Extras',
                    store={
                        'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['extras_ids'], 10),
                        'cyg.inmuebles.extras': (_get_extras, ['precio','cantidad'], 10),
                    },
                    multi='suma', help="Total de Extras"),
                'cuotas_total':fields.function(_inmueble_all, digits_compute=dp.get_precision('Account'), string='Cuotas adicionales',
                    store={
                        'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['cuotas_ids'], 10),
                        'cyg.inmueble.cuota': (_get_cuotas, ['cliente'], 10),
                    },
                    multi='suma', help="Total de cuotas adicionales, penalizaciones, etc..."),
                'total':fields.function(_inmueble_all, digits_compute=dp.get_precision('Account'), string='Total',
                    store={
                        'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['extras_ids'], 10),
                        'cyg.inmuebles.extras': (_get_extras, ['precio','cantidad'], 10),
                        'sale.inmueble.line': (_get_inmuebles, ['precio', 'cantidad'], 10),
                        'cyg.inmueble.cuota': (_get_cuotas, ['cliente'], 10),
                    },
                    multi='suma', help="Total de Compra"),
                
                'cuota_cliente':fields.function(_cuota_all, digits_compute=dp.get_precision('Account'), string='Total Cliente',
                    store={
                        'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['cuotas_ids'], 10),
                        'cyg.inmueble.cuotas': (_get_cuotas, ['promotor','cliente'], 10),
                    },
                    multi='suma', help="Total de Cliente"),
                
                'cuota_promotor':fields.function(_cuota_all, digits_compute=dp.get_precision('Account'), string='Total Promotor',
                    store={
                        'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['cuotas_ids'], 10),
                        'cyg.inmueble.cuotas': (_get_cuotas, ['promotor','cliente'], 10),
                    },
                    multi='suma', help="Total de Promotor"),
                
                'fecha_entrega':fields.date('Entrega estimada'),
                'meses':fields.integer('Meses por transcurrir para entrega'),
                #Plan de Pagos original
                'poreserva':fields.float('Reserva (%)'),
                'reserva': fields.function(_fnt_valor_propuesto, string='Reserva', type='float', digits_compute=dp.get_precision('Account'),  method=True, store=False,multi='porcentage_propuesto'),
                'poentrada':fields.float('Entrada (%)'),
                'entrada': fields.function(_fnt_valor_propuesto, string='Entrada', type='float', digits_compute=dp.get_precision('Account'),  method=True, store=False,multi='porcentage_propuesto'),
                'pofinanciamiento':fields.float('Financiamiento (%)'),
                'financiamiento': fields.function(_fnt_valor_propuesto, string='Financiamiento', type='float', digits_compute=dp.get_precision('Account'),  method=True, store=False,multi='porcentage_propuesto'),
                #Plan de Pagos Cliente
                'pocreserva':fields.float('Reserva (%)'),
                'creserva': fields.function(_fnt_valor_cliente, string='Reserva', type='float', digits_compute=dp.get_precision('Account'),  method=True, store=False,multi='porcentage'),
                'pocentrada':fields.float('Entrada (%)'),
                'centrada': fields.function(_fnt_valor_cliente, string='Entrada', type='float', digits_compute=dp.get_precision('Account'),  method=True, store=False,multi='porcentage'),
                'pocfinanciamiento':fields.float('Financiamiento (%)'),
                'cfinanciamiento':fields.function(_fnt_valor_cliente, string='Financiamiento', type='float', digits_compute=dp.get_precision('Account'),  method=True, store=False,multi='porcentage'),
                #Totales
                'total_original': fields.float('Total'),
                'total_propuesto': fields.float('Total'),
                #Calculo de cuotas
                'fecha_inicial':fields.date('Primera Cuota'),
                'cuotas_ids':fields.one2many('cyg.inmueble.cuota', 'sale_id','Cuotas'),
                #Calculo de Credito Hipotecario
                'capital':fields.float('Capital'),
                'solca':fields.float('Solca 0.5%'),
                'plazo':fields.integer('Plazo en Años'),
                'taza':fields.float('Taza (%)'),
                'cuota_mensual':fields.float('Cuota Mensual'),
                'ingreso_mensual':fields.float('Ingreso'),
                'diez':fields.float('10 Años'),
                'quince':fields.float('15 Años'),
                'veinte':fields.float('20 Años'),
                'veinte_cinco':fields.float('25 Años'),
                'banco_preferencia':fields.text('Banco'),
                'doc_cedula':fields.binary('Doc. Cedula', filters=None),
                'doc_anexo':fields.binary('Doc. Anexo', filters=None),
                
                'amount_pending':fields.float('Valor Pendiente',digits_compute=dp.get_precision('Account')),
                'desistir_id':fields.many2one('cyg.inmueble.desistimiento','Desistimiento', readonly=True),
                'inmueble':fields.function(_name_inmueble, string='Inmueble', type='char', size=60, method=True, store=False),
                
                'is_generate':fields.boolean('tabla', help="Indica si genero una tabla"),
                #Cambios del Augusto
                'valor_devuelto':fields.float('Valor Devuelto'),
                'fecha_devolucion':fields.date('Fecha Devolución'),
                
    }
    _defaults = {  
        'currency_id': 3,
        'fecha_entrega': fields.date.context_today,
        'fecha_inicial': fields.date.context_today,
        'poreserva':5,
        'poentrada':25,
        'pofinanciamiento':70,
        'taza':10.75,
        'plazo':10,
        'is_generate':False,
        'meses':12
        }

sale_order()

class sale_inmueble_line(osv.osv):
    _name = 'sale.inmueble.line'
    _description = 'Clase que añade los inmuebles' 
    
    def onchange_inmueble(self, cr,uid, ids,field_name):
        #print 'field_name',field_name
        inmueble_obj = self.pool.get('cyg.proyecto_inmueble')
        res ={'value':{}}
        if field_name:
            inmueble_info = inmueble_obj.browse(cr, uid, field_name)
            res['value']['precio']= inmueble_info.precio_actual
            res['value']['precio_venta']= inmueble_info.precio_actual
            res['value']['precio_readonly']= inmueble_info.precio_actual
            res['value']['name']= inmueble_info.name
            res['value']['tipo']= inmueble_info.tipo_inmueble_id and inmueble_info.tipo_inmueble_id.name or 's/n' 
        return res
    
    def _check_name(self,cr,uid,ids):
        for idea in self.browse(cr, uid, ids):
            if 'spam' in idea.name: 
                return False # Can't create ideas with spam!
        return True
    
    def create(self, cr, uid, vals, context={}):
        res_id = super(sale_inmueble_line, self).create(cr, uid, vals, context)
        return res_id
    
    def write(self, cr, uid, ids, vals, context=None):
        #TODO: process before updating resource
        res = super(sale_inmueble_line, self).write(cr, uid, ids, vals, context)
        return res
    
    def _fnt_valor_inmueble(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        inmueble_obj = self.pool.get('cyg.proyecto_inmueble')
        for line in self.browse(cr, uid, ids, context=context):
            inmueble_info = inmueble_obj.browse(cr, uid, line.inmueble_id.id)
            res[line.id] = inmueble_info.precio_actual or 0.00
        return res
    
    def create(self, cr, uid, vals, context={}):
        if 'precio' in vals:
            vals['precio_readonly'] =vals.get('precio')
        res_id = super(sale_inmueble_line, self).create(cr, uid, vals, context)
        return res_id
    
    def write(self, cr, uid, ids, vals, context=None):
        #TODO: process before updating resource
        if 'precio' in vals:
            vals['precio_readonly'] =vals.get('precio')
        res = super(sale_inmueble_line, self).write(cr, uid, ids, vals, context)
        return res
    
    _columns = {
                'name': fields.char('Nro', size=64),
                'sale_id':fields.many2one('sale.order','Orden de Venta'),
                'project_id':fields.many2one('cyg.proyecto','Proyecto'),
                'etapa_id':fields.many2one('cyg.proyecto_etapa','Etapa'),
                'inmueble_id':fields.many2one('cyg.proyecto_inmueble','Inmueble'),
                'precio': fields.float('Precio Venta'),
                'precio_readonly': fields.float('Precio Venta'),
                'precio_venta': fields.function(_fnt_valor_inmueble, string='Precio', type='float', digits=(16,2),  method=True, store=True),
                'tipo': fields.char('Tipo', size=64),
                'cantidad':fields.integer('Cantidad'),
                'state': fields.selection([('draft', 'Borrador'),
                                           ('disponible', 'Disponible'),
                                           ('reservado', 'Reservado'),
                                           ('vendido', 'Vendido'),
                                           ('desistido', 'Desistido'),
                                           ('cancel', 'Cancelada'),], 'Estado'),
                }
    _defaults = {  
                 'cantidad': 1,
                 'state':'disponible'
        }
    #_sql_constraints = [('name_uniq', 'unique (inmueble_id,)', 'The Name of the OpenERPModel must be unique !'),     cr ]
sale_inmueble_line()   


class extras(osv.osv):
    """Clase para la administracion de extras"""
    _name = 'cyg.extras'
    _description = "Clase para la administración de extras"

    _columns = {
        'project_id':fields.many2one('cyg.proyecto','Proyecto'),
        'name': fields.char('Nombre', size=64),
        'precio': fields.float('Precio'),
        'description': fields.text('Descripción'),
        }
extras()

class sale_inmuebles_extras(osv.osv):
    """Clase para la administracion de extras"""
    _name = 'cyg.inmuebles.extras'
    _description = "Clase para la administración de extras"
    
    def onchange_extra(self, cr,uid, ids,field_name):
        print 'field_name',field_name
        extra_obj = self.pool.get('cyg.extras')
        res ={'value':{}}
        if field_name:
            extra_info = extra_obj.browse(cr, uid, field_name)
            res['value']['precio']= extra_info.precio
            #res['value']['name']= inmueble_info.name
            #res['value']['tipo']= inmueble_info.tipo_inmueble_id and inmueble_info.tipo_inmueble_id.name or 's/n' 
        return res
    
    def _amount_extras(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        subtotal =0.00
        for line in self.browse(cr, uid, ids, context=context):
            subtotal = line.precio * line.cantidad
            cur = line.sale_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, subtotal)
        return res
    
    _columns = {
        'sale_id':fields.many2one('sale.order','Orden de Venta'),
        'project_id':fields.many2one('cyg.proyecto','Proyecto'),
        'extra_id':fields.many2one('cyg.extras','Extra',
                                   domain="[('project_id','=',project_id)]"),
        'precio': fields.float('Precio'),
        'name': fields.char('Extra', size=64),
        'cantidad':fields.integer('Cantidad'),
        'price_subtotal': fields.function(_amount_extras, string='Subtotal', digits_compute= dp.get_precision('Account')),
        
        }
    
    _defaults = {  
                 'cantidad': 1
        }
sale_inmuebles_extras()

class sale_inmueble_cuota(osv.osv):
    _name = 'cyg.inmueble.cuota'
    
    def button_validar(self, cr, uid, ids, context={}):
        sale_obj = self.pool.get('sale.order')
        sale_inmueble_obj = self.pool.get('sale.inmueble.line')
        inmueble_obj = self.pool.get('cyg.proyecto_inmueble')
        historial_obj = self.pool.get('cyg.historico_precios_inmueble')
        for item in self.browse(cr, uid, ids, context=context):
            inmueble_id = item.inmueble_id
            if item.afecta_precio == 'si':
                precio_nuevo = inmueble_id.precio_actual + item.cliente
                historial_obj.create(cr, uid, {'inmueble_id': inmueble_id.id,
                                               'precio_anterior': inmueble_id.precio_actual,
                                               'precio_actual': precio_nuevo,
                                               'usuario_cambio': uid,
                                               'date': time.strftime('%Y-%m-%d %H:%M:%S')
                                               })
                inmueble_obj.write(cr, uid, [inmueble_id.id], {'precio_actual': precio_nuevo})
                sale_obj.write(cr, uid,[item.sale_id.id],{'total':item.sale_id.total + item.cliente,'amount_pending':(item.sale_id.total + item.cliente) - item.sale_id.amount_paid})
                inmueble_ids = sale_inmueble_obj.search(cr, uid, [('sale_id','=',item.sale_id.id),('inmueble_id','=',item.inmueble_id.id)])
                if inmueble_ids:
                    sale_inmueble_obj.write(cr, uid,[inmueble_ids[0]],{'precio':inmueble_id.precio_actual + item.cliente})
                
        return self.write(cr, uid, ids, {'state':'done'},context=context)
    
    def button_to_draft(self, cr, uid, ids, context={}):
        sale_obj = self.pool.get('sale.order')
        sale_inmueble_obj = self.pool.get('sale.inmueble.line')
        inmueble_obj = self.pool.get('cyg.proyecto_inmueble')
        historial_obj = self.pool.get('cyg.historico_precios_inmueble')
        for item in self.browse(cr, uid, ids, context=context):
            inmueble_id = item.inmueble_id
            if item.afecta_precio == 'si':
                precio_nuevo = inmueble_id.precio_actual - item.cliente
                historial_obj.create(cr, uid, {'inmueble_id': inmueble_id.id,
                                               'precio_anterior': inmueble_id.precio_actual,
                                               'precio_actual': precio_nuevo,
                                               'usuario_cambio': uid,
                                               'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                                               #'detalle':'Cambios desde cuota'
                                               })
                inmueble_obj.write(cr, uid, [inmueble_id.id], {'precio_actual': precio_nuevo})
                sale_obj.write(cr, uid,[item.sale_id.id],{'total':item.sale_id.total - item.cliente,'amount_pending':(item.sale_id.total - item.cliente) - item.sale_id.amount_paid})
                inmueble_ids = sale_inmueble_obj.search(cr, uid, [('sale_id','=',item.sale_id.id),('inmueble_id','=',item.inmueble_id.id)])
                if inmueble_ids:
                    sale_inmueble_obj.write(cr, uid,[inmueble_ids[0]],{'precio':inmueble_id.precio_actual - item.cliente})
        
        return self.write(cr, uid, ids, {'state':'draft'},context=context)
    
    def get_dia_habil(self,fecha_pago):
        dia_pago =self._format_date(fecha_pago)
        if dia_pago.weekday()==5:
            dia_pago=dia_pago + relativedelta(days=+2)
        elif dia_pago.weekday()==6:
            dia_pago= dia_pago + relativedelta(days=+1)
        return dia_pago
    
    def _format_date(self, date):
        if date:
            campos = date.split('-')
            date = datetime.date(int(campos[0]), int(campos[1]), int(campos[2]))
            return date
    
    def onchange_sale_order(self, cr, uid, ids, sale_id, context=None):
        sale_obj = self.pool.get('sale.order')
        res = {}
        if sale_id:
            sale = sale_obj.browse(cr, uid, sale_id, context=context)
            res['partner_id'] = sale.partner_id.id
            res['project_id'] = sale.proyecto_id.id
            res['etapa_id'] = sale.etapa_id.id
            res['inmueble_id'] = sale.inmuebles_ids[0].inmueble_id.id
        return {'value':res}

    
    def unlink(self, cr, uid, ids, context=None):
        #TODO: process before delete resource
        list=[]
        for item in self.browse(cr, uid, ids):
            if item.state != 'draft':
                raise osv.except_osv(('Aviso !'),u'No se permite eliminar las cuotas')
            else:
                list.append(item.id)
        res = super(sale_inmueble_cuota, self).unlink(cr, uid, list, context)
        return res
    
    def _fnt_vencida(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for cuota in self.browse(cr, uid, ids, context=context):
            if cuota.state =='done':
                now = self._format_date(time.strftime('%Y-%m-%d')) #fecha actual
                f1 = self._format_date(cuota.fecha)
                r = (f1-now).days
                if r < 0:
                    res[cuota.id]= 'vencida '+ str(r)
                else:
                    res[cuota.id]= 'vence ' + str(r)
            else:
                res[cuota.id]= ''
        return res
    
    
    def on_change_valores(self, cr, uid, ids, cliente, promotor):
        #print 'on_change_valores', cliente
        #print 'on_change_promotor', promotor
        res = {}
        res['acumulado'] = promotor - cliente
        return {'value':res}
    
    def on_change_valores_cliente(self, cr, uid, ids, cliente, context):
        #print 'on_change_valores', cliente
        #print 'on_change_promotor', promotor
        res = {}
        #res['acumulado'] = promotor - cliente
        res['referencia'] = context.get('valor',0.00) -cliente
        return {'value':res}
    
    
    def _fnt_valor_acumulado(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        #print "Aqi"
        for cuota in self.browse(cr, uid, ids, context=context):
            res[cuota.id]= cuota.promotor - cuota.cliente
        return res
    
    def _fnt_pagado_acumulado(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        line_obj = self.pool.get('cyg.payment.line')
        for cuota in self.browse(cr, uid, ids, context=context):
            #sql = 'select sum(valor_)'
            amount = 0.00
            lineas_ids = line_obj.search(cr, uid,[('cuota_id','=',cuota.id)])
            if lineas_ids:
                for item in line_obj.browse(cr,uid,lineas_ids):
                    amount += item.valor_pagado_cliente
                res[cuota.id]= amount
            else:
                res[cuota.id]= 0.00
        return res
    
    def onchange_partner_id(self, cr, uid, ids, field_name,context):
        #print 'context onchange_partner_id', context
        res ={}
        if field_name and context:
            if 'create_cuota' in context:
                res['inmueble_id'] = False
                res['project_id'] = False
                res['etapa_id'] = False
                res['sale_id'] = False
        return {'value':res}
    
    def onchange_inmueble(self, cr , uid,ids, field_name):
        res = {}
        inmueble_obj = self.pool.get('cyg.proyecto_inmueble')
        if field_name:
            info = inmueble_obj.browse(cr, uid, field_name)
            #print 'info', info
            res['project_id'] = info.proyecto_id and info.proyecto_id.id or False
            res['tasa_id'] = info.proyecto_id and info.proyecto_id.tasa_id and info.proyecto_id.tasa_id.id or False
            res['etapa_id'] = info.etapa_id and info.etapa_id.id or False
            res['sale_id'] = info.sale_id and info.sale_id.id or False
            res['valor_total_venta'] = info.sale_id and info.sale_id.total or False
            sale_id = info.sale_id and info.sale_id.id or False
            sql = "select max(cuota) from cyg_inmueble_cuota where sale_id = "+str(sale_id)
            cr.execute(sql)
            result = cr.fetchall()
            res['cuota'] = result[0][0]+1 or 0
        #print 'res', res
        return {'value':res}
    
    def onchange_date(self, cr, uid, ids, field_name,context=None):
        #print 'field_name',field_name
        #print 'onchange_date', context
        res = {}
        if field_name and context:
            #fecha_pago = self._format_date(field_name)
            dia_pago = self.get_dia_habil(field_name)
            #print 'dia_pago',dia_pago
            
            name = dia_pago.strftime('%A, %d de %B del %Y')
            
            res['name'] = tools.ustr(name) 
            res['fecha'] = dia_pago.strftime('%Y-%m-%d')
            res['partner_id'] = context.get('partner_id',False)
            res['project_id'] = context.get('project_id',False)
            res['inmueble_id'] = context.get('inmueble_id',False)
            res['etapa_id'] = context.get('etapa_id',False)
        #print 'res', res
        return {'value':res}
    
    def create(self, cr, uid, vals, context={}):
        #print 'create cuota line',context
        inmueble_obj = self.pool.get('cyg.proyecto_inmueble')
        sale_obj = self.pool.get('sale.order')
        vals['pendiente'] = vals.get('cliente',0.00)
        if 'default_tree_cuota' in context:
            if 'inmueble_id' in vals:
                fecha = self.get_dia_habil(vals.get('fecha'))
                info = inmueble_obj.browse(cr, uid, vals.get('inmueble_id'))
                vals['name'] = fecha.strftime('%A, %d de %B del %Y')
                vals['project_id'] = info.proyecto_id and info.proyecto_id.id
                vals['etapa_id'] = info.etapa_id and info.etapa_id.id
                vals['sale_id'] = info.sale_id and info.sale_id.id
                vals['pendiente'] = vals.get('cliente',0.00)
                vals['promotor'] = vals.get('cliente',0.00)
                vals['state'] = 'done'
                #amount_pending = info.sale_id.amount_pending + vals['pendiente']
                #sale_obj.write(cr, uid, [vals['sale_id']], {'amount_pending': amount_pending})
        if 'default_cyg_cotizacion' in context:
            vals['pendiente'] = vals.get('cliente',0.00)
            vals['promotor'] = vals.get('promotor',0.00)
        if vals.get('code','/')=='/':
            vals['code'] = self.pool.get('ir.sequence').get(cr, uid, 'cyg.inmueble.cuota') or '/'
        res_id = super(sale_inmueble_cuota, self).create(cr, uid, vals, context)
        return res_id
    
    def write(self, cr, uid, ids, vals, context={}):
        if 'cliente' in vals:
            vals['pendiente'] = vals.get('cliente',0.00)
        if 'default_tree_cuota' in context:
            if 'cliente' in vals:
                vals['promotor'] =  vals.get('cliente',0.00)
                vals['pendiente'] = vals.get('cliente',0.00)
        res = super(sale_inmueble_cuota, self).write(cr, uid, ids, vals, context)
        return res
    
    def _function_nro(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for cuota in self.browse(cr, uid, ids, context=context):
            if cuota.state =='done':
                now = self._format_date(time.strftime('%Y-%m-%d')) #fecha actual
                f1 = self._format_date(cuota.fecha)
                r = (f1-now).days
                if r < 0:
                    res[cuota.id]= 'vencida '+ str(r)
                else:
                    res[cuota.id]= 'vence ' + str(r)
            else:
                res[cuota.id]= ''
        return res
    
    def _fnt_valor_vencido(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for cuota in self.browse(cr, uid, ids, context=context):
            res[cuota.id] = {
                'vencido': 0.00,
                'amount_interes_mora': 0.00,
            }
            if cuota.state =='done' and not cuota.mora_paid and not cuota.mora:
                now = self._format_date(time.strftime('%Y-%m-%d')) #fecha actual
                f1 = self._format_date(cuota.fecha)
                r = (f1-now).days
                if r < 0:
                    res[cuota.id]['vencido']= cuota.pendiente
                    tasa = cuota.project_id and  cuota.project_id.tasa_id and cuota.project_id.tasa_id.tasa or 0.00
                    res[cuota.id]['amount_interes_mora']= cuota.pendiente * (tasa / 360) * r *-1
                else:
                    res[cuota.id]['vencido']= 0.00
                    res[cuota.id]['amount_interes_mora']= 0.00
            else:
                res[cuota.id]['vencido']= 0.00
                res[cuota.id]['amount_interes_mora']= 0.00
        return res
    
    def onchange_mostrar_extra(self, cr, uid, ids, field_name):
        res = {}
        if field_name=='no':
            res['mostrar_extra'] = True
        else:
            res['mostrar_extra'] = False
        return {'value':res}
    
    _columns = {
                'name':fields.char('Fecha de Vencimiento',size=256),
                'user_id': fields.many2one('res.users', 'Usuario'),
                'code':fields.char('Code',size=500),
                'sale_id':fields.many2one('sale.order', 'Cotización'),
                'partner_id':fields.many2one('res.partner', 'Cliente'),
                'project_id':fields.many2one('cyg.proyecto', 'Proyecto'),
                'tasa_id': fields.many2one('cyg.tasa.interes','Tasa de Interes'),
                'inmueble_id':fields.many2one('cyg.proyecto_inmueble','Inmueble'),
                'etapa_id':fields.many2one('cyg.proyecto_etapa','Etapa'),
                'cuota':fields.integer('Cuota'),
                #'nro_cuota':fields.
                #'is_vencida':fields.function(_fnt_vencida, string='Vencida', type='char', size=60, method=True, store=False),
                'nro_cuota': fields.function(_function_nro, type='char', string='New', size=60,store=False,method=True),
                 
                'fecha':fields.date('Fecha de Vencimiento'),
                'concepto':fields.selection([('reserva','Reserva'),
                                            ('entrada','Entrada'),
                                            ('financiamiento','Financiamiento'),
                                            ('extraordinaria','Cuota Extraordinaria'),
                                            ('descuento','Descuento'),
                                            ('penalizacion','Penalización'),
                                            ('desistido','Desistido'),
                                            ('saldo_reserva','Saldo reserva 10%'),
                                            ('bono_vivienda','Bono de vivienda'),
                                            ('cuota_extra','Cuota por extras'),
                                            ],'Concepto'),
                
                'promotor':fields.float('Valor Promotor',digits_compute=dp.get_precision('Account')),
                'cliente':fields.float('Valor Cliente',digits_compute=dp.get_precision('Account')),
                
                'state': fields.selection([ ('draft', 'Borrador'),
                                            ('sent', 'Proforma Enviada'),
                                            ('reservado', 'Reservado'),
                                            ('cancel', 'Cancelada'),
                                            ('desistido', 'Desistido'),
                                            ('done', 'Pendiente'),
                                            ('paid', 'Pagada'),
                                            ], 'Estado', readonly=True,select=True),
                'fecha_pago':fields.date('Fecha de Pago'),
                'comprobante':fields.char('Comprobante de Pago', size=500),
                'banco':fields.char('Banco', size=500),
                #'bank_id':fields.many2one('res.bank','Banco'),
                'bank_id':fields.many2one('res.partner.bank','Banco'),
                'pagado':fields.float('Valor Pagado',digits_compute=dp.get_precision('Account')),
                'pendiente':fields.float('Valor Pendiente',digits_compute=dp.get_precision('Account')), #Cambio a valor acumulado
                'is_vencida':fields.function(_fnt_vencida, string='Vencida', type='char', size=60, method=True, store=False),
                'vencido':fields.function(_fnt_valor_vencido, string='Vencido', type='float', digits_compute=dp.get_precision('Account'),  method=True, store=False,multi='vencido'),
                'valor_vencido':fields.float('Valor Vencido',digits_compute=dp.get_precision('Account')), 
                'amount_interes_mora':fields.function(_fnt_valor_vencido, string='Interes Mora', type='float', digits_compute=dp.get_precision('Account'),  method=True,store=False,multi='vencido'),
                'valor_interes_mora':fields.float('Interes por Mora',digits_compute=dp.get_precision('Account')),
                'acumulado':fields.function(_fnt_valor_acumulado, string='Diferencia', type='float', digits_compute=dp.get_precision('Account'), store=False),
                'pagado_acumulado':fields.function(_fnt_pagado_acumulado, string='Pagado', type='float', digits_compute=dp.get_precision('Account'), method=True, store=False),
                #Registro de Moras y Pagos de Abonos
                'valor_pagado_abono':fields.float('Valor Abonado',digits_compute=dp.get_precision('Account')),
                'valor_pagado_mora':fields.float('Valor Pagado Mora',digits_compute=dp.get_precision('Account')),
                'valor_pendiente_mora':fields.float('Valor Pendiente Mora',digits_compute=dp.get_precision('Account')),
                'valor_pendiente_abono':fields.float('Valor Pendiente Abono',digits_compute=dp.get_precision('Account')),
                'mora':fields.boolean('No cobrar interes por mora', help="Si marco esta opcion no se calculara ni cobrara interes por mora de la cuota"),
                'mora_paid':fields.boolean('Pagada Mora'),
                'mostrar_pagos':fields.boolean('Mostrar los Registros de Abonos y Moras'),
                'valor_mora':fields.float('Valor Mora',digits_compute=dp.get_precision('Account'), help="El valor de la mora hasta la fecha que cobro"),
                'valor_actual_pendiente':fields.float('Valor Abono',digits_compute=dp.get_precision('Account'), help="El valor pendiente hasta la fecha que hizo el abono"),
                'fecha_pago_mora':fields.date('Fecha de pago de Mora'),
                'fecha_pago_abono':fields.date('Fecha de Abono por Descuento'),
                ##############################################
                'observacion': fields.text('Observación'),
                'parcial':fields.boolean('Parcial'),
                'referencia':fields.float('Referencia'),
                ##############################################
                'mostrar_extra':fields.boolean('Mostrar Buton de pago extra'),
                'afecta_precio':fields.selection([('si','Si'),
                                                  ('no','No')],'Afecta al precio del inmueble'),
                'valor_extra':fields.float('Valor Extra'),
                'descripcion_extra':fields.text('Descripcion'),
                'fecha_pago_extra':fields.date('Fecha pago Extra'),
                'valor_total_venta':fields.float('Valor Venta'),
               }
    #Ordenado por fecha de vencimiento
    _order = 'fecha, cuota asc'
    
    _defaults = {  
        'state': 'draft',  
        'concepto':'extraordinaria',
        'code': lambda obj, cr, uid, context: '/',
        'user_id':lambda self, cr, uid, ctx: uid,
        'parcial':False,
        'mostrar_extra':False,
        }
    _sql_constraints = [('name_uniq', 'unique (fecha,cuota,inmueble_id,sale_id)', 'El numero de cuota se repite para una misma fecha de pago'),      ]
sale_inmueble_cuota()

class sale_inmueble_desistimiento(osv.osv):
    _name = 'cyg.inmueble.desistimiento'
    
    def onchage_valor(self, cr, uid, ids,residual,total,retenido):
        res = {}
        devuelto = 0.00
        if retenido:
            recaudado = total -residual
            devuelto = recaudado -retenido
            res['valor_devuelto'] = devuelto
        return {'value':res}
    
    def button_validar(self, cr, uid, ids, context={}):
        sale_order_obj =self.pool.get('sale.order')
        sale_cuota_obj = self.pool.get('cyg.inmueble.cuota')
        inmueble_id = False
        n = 0
        for item in self.browse(cr, uid,ids):
            #print 'item', item.sale_id
            if item.sale_id:
                for im in item.sale_id.inmuebles_ids:
                    self.pool.get('cyg.proyecto_inmueble').write(cr, uid,[im.inmueble_id.id],{'state':'disponible'})
                    inmueble_id = im.inmueble_id.id
                    self.pool.get('sale.inmueble.line').write(cr, uid,[im.id],{'state':'desistido'})
                for line in item.sale_id.cuotas_ids:
                    n += 1
                    self.pool.get('cyg.inmueble.cuota').write(cr, uid, [line.id],{'state':'desistido'})
                    
            sale_order_obj.write(cr,uid,[item.sale_id.id],{'state':'desistido','amount_pending':0.00,'desistir_id':item.id})
            
            dict = {'state':'desistido',
                    'cuota':n,
                    'name':item.date,
                    'partner_id':item.sale_id and item.sale_id.partner_id and item.sale_id.partner_id.id,
                    'sale_id': item.sale_id and item.sale_id.id,
                    'fecha':item.date,
                    'concepto':'desistido',
                    'inmueble_id':  inmueble_id,
                    'project_id':item.sale_id and item.sale_id.proyecto_id.id,
                    'cliente':item.valor_recaudado - item.valor_retenido,
                    'etapa_id':item.sale_id and item.sale_id.etapa_id and item.sale_id.etapa_id.id,
                    'pendiente':0.00  
                    }
            #print 'dict', dict
            sale_cuota_obj.create(cr, uid, dict)
        return self.write(cr, uid,ids,{'residual':item.residual,
                                       'tota':item.total,
                                       'valor_recaudado':item.valor_recaudado,
                                       'valor_retenido':item.valor_retenido,
                                       'valor_devuelto':item.valor_recaudado - item.valor_retenido,
                                       'state':'done'
                                       })
    
    def create(self, cr, uid, vals, context={}):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cyg.inmueble.desistimiento') or '/'
        res_id = super(sale_inmueble_desistimiento, self).create(cr, uid, vals, context)
        return res_id 
    _columns = {
                'name':fields.char('Nombre',size=50),
                'sale_id':fields.many2one('sale.order','Orden de Venta'),
                'motivo':fields.text('Motivo del Desistimiento'),
                'date':fields.date('Fecha de Desistimiento'),
                'residual':fields.float('Valor residual'),
                'total':fields.float('Valor Total Venta'),
                'valor_recaudado':fields.float('Valor recaudado'),
                'valor_retenido':fields.float('Valor retenido'),
                'valor_devuelto':fields.float('Valor devuelto'),
                'state':fields.selection([
                    ('draft','Draft'),
                    ('done','Done'),
                    ],'State', select=True, readonly=True),
                }
    _defaults = {  
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'state':'draft',
        'name':'/',
        
        }
sale_inmueble_desistimiento()
    
    
class historico_comisiones_inmueble(osv.osv):
    """Clase historico de comisiones de inmuebles"""

    _name = 'cyg.historico_comisiones_inmueble'
    _description = "Clase historico de comisiones de inmuebles"

    def onchange_sale_order(self, cr, uid, id, sale_order_id, context=None):
        sale = self.pool.get('sale.order').browse(cr, uid, sale_order_id)
        return {'value': {'valor_venta': sale.total,'tercero':sale.user_id.partner_id.id}}

    def onchange_comision_porcentaje(self, cr, uid, id, sale_order_id, comision_porcentaje, context=None):
        sale = self.pool.get('sale.order').browse(cr, uid, sale_order_id)
        return {'value': {'comision_valor': (sale.total * comision_porcentaje)/100}}

    _columns = {
        'inmueble_id': fields.many2one('cyg.proyecto_inmueble', 'Inmueble', required=True, ondelete='cascade'),
        'sale_order_id': fields.many2one('sale.order', 'Venta', domain="[('state','=','done')]",
                                         required=True),
        'usuario': fields.many2one('res.partner', 'Usuario'),
        'valor_venta': fields.float('Valor venta', required=True),
        'tercero': fields.many2one('res.partner', 'Venderador comisiona'),
        'comision_porcentaje': fields.float('% comisión'),
        'comision_valor': fields.float('$ comisión', required=True),
        }

historico_comisiones_inmueble()


class sale_shop(osv.osv):
    _inherit = 'sale.shop'

    _defaults = {
        'payment_default_id': 2
    }

sale_shop()

class cyg_sale_canal(osv.osv):
    _name = 'cyg.sale.canal'

    _columns = {
                'sale_id': fields.many2one('sale.order','Venta'),
                'canal_id': fields.many2one('cyg.canal','Canal'),
                'canal_nombre':fields.char('Nombre Canal', size=100),
                }

cyg_sale_canal()

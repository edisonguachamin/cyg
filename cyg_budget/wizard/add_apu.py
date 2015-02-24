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
from lxml import etree


class cyg_add_apu_wiz(osv.osv_memory):
    _name = 'cyg.add.apu.wiz'
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if not context: context = {}
        res = super(cyg_add_apu_wiz, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)
        if context and 'line_ids' in context:
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//field[@name='lines']")
            for node in nodes:
                node.set('domain', '[("id", "in", '+ str(context['line_ids'])+')]')
            res['arch'] = etree.tostring(doc)
        return res
    
    def search_entries(self, cr, uid, ids, context=None):
        line_ids = []
        presupuesto_obj = self.pool.get('cyg.presupuesto')
        mod_obj = self.pool.get('ir.model.data')
        
        if context is None:
            context = {}
        data = self.browse(cr, uid, ids, context=context)[0]
        
        remove = []
        sql = "select id from cyg_apu"
        cr.execute(sql)
        res = [aux[0] for aux in cr.fetchall()]
        line_ids = res
        #for x in presupuesto_obj.browse(cr, uid, context.get('active_ids',[])):
        #    if x.presupuesto_ids:
        #        remove += [ y.apu_id.id for y in x.presupuesto_ids if x.presupuesto_ids]
        
        #print 'line_ids', line_ids
        
        line_ids = [ x for x in line_ids if x not in remove]
        context.update({'line_ids': line_ids})
        context['capitulo_id']=data.capitulo_id.id
        model_data_ids = mod_obj.search(cr, uid,[('model', '=', 'ir.ui.view'), ('name', '=', 'view_create_apu_lines')], context=context)
        resource_id = mod_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
        return {'name': ('APU'),
                'context': context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'cyg.add.apu.wiz',
                'views': [(resource_id,'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
        }
        
    
    def add_apu(self, cr, uid, ids, context=None):
        print 'add_apu', context
        apu_obj = self.pool.get('cyg.apu')
        
        line_obj = self.pool.get('cyg.presupuesto.line')
        capitulo_obj = self.pool.get('cyg.apu.capitulo')
        if context is None:
            context = {}
        data = self.browse(cr, uid, ids, context=context)[0]
        apu_ids = [entry.id for entry in data.lines]
        capitulo_info = capitulo_obj.browse(cr, uid, context.get('capitulo_id'))
        #print 'active_id', context['active_id']
        if not apu_ids:
            return {'type': 'ir.actions.act_window_close'}
        
        for line in apu_obj.browse(cr, uid, apu_ids, context=context):
            repetidas_ids = line_obj.search(cr, uid,[('presupuesto_id','=',context['active_id']),
                                                   ('apu_id','=',line.id),
                                                   ('capitulo_id','=',context.get('capitulo_id', False))])
            if not repetidas_ids: 
                line_obj.create(cr, uid, {'presupuesto_id':context['active_id'],
                                           'apu_id':line.id,
                                            'capitulo_id':context.get('capitulo_id', False),
                                            'precio_escenario': 'escenario_uno',
                                            'price':line.amount_total,
                                            'uom_id':line.uom_id and line.uom_id.id,
                                            'code': line.code or '',
                                            'qty':1,
                                            'sequence_cap':capitulo_info.code or '',
                                            },context=context)
            
        return {'type': 'ir.actions.act_window_close'}



    _columns = {
        'capitulo_id': fields.many2one('cyg.apu.capitulo','Capitulo'),
        'lines': fields.many2many('cyg.apu', 'cyg_presupuesto_rel_apu', 'presupuesto_id', 'apu_id', 'Analisis de Precios')
        }

cyg_add_apu_wiz()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

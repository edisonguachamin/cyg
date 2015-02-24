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

CATEGORIAS = ['EQUIPOS Y HERRAMIENTAS','MATERIALES','TRANSPORTE','MANO DE OBRA']

class cyg_add_product_wiz(osv.osv_memory):
    _name = 'cyg.add.product.wiz'
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if not context: context = {}
        res = super(cyg_add_product_wiz, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)
        if context and 'line_ids' in context:
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//field[@name='lines']")
            for node in nodes:
                node.set('domain', '[("id", "in", '+ str(context['line_ids'])+')]')
            res['arch'] = etree.tostring(doc)
        return res
    
    def search_entries(self, cr, uid, ids, context=None):
        line_ids = []
        apu_obj = self.pool.get('cyg.apu')
        mod_obj = self.pool.get('ir.model.data')
        
        if context is None:
            context = {}
        data = self.browse(cr, uid, ids, context=context)[0]
        categoria_id = data.category_id and data.category_id.id or False
        if  categoria_id:
            sql = "select p.id from product_product as p, product_template t "\
              "where p.product_tmpl_id = t.id "\
              "and t.categ_id = "+str(categoria_id)
        else:
            sql = "select p.id from product_product as p, product_template t, product_category c "\
              "where p.product_tmpl_id = t.id and c.id =t.categ_id and c.name in ("+','.join("'"+str(x)+"'" for x in CATEGORIAS)+")"
              
        #print 'sql', sql

        cr.execute(sql)
        res = [aux[0] for aux in cr.fetchall()]
        line_ids = res
        print 'res', line_ids
        remove = []
        line_obj = self.pool.get('cyg.apu.line')
        for x in apu_obj.browse(cr, uid, context.get('active_ids',[])):
            if x.equipo_ids:
                remove += [ y.product_id.id for y in x.equipo_ids if x.equipo_ids]
            if x.materiales_ids:
                remove += [ y.product_id.id for y in x.materiales_ids if x.materiales_ids]
            if x.transporte_ids:
                remove += [ y.product_id.id for y in x.transporte_ids if x.transporte_ids]
            if x.mano_obra_ids:
                remove += [ y.product_id.id for y in x.mano_obra_ids if x.mano_obra_ids]
            
            if x.equipo2_ids:
                remove += [ y.product_id.id for y in x.equipo2_ids]
            if x.materiales2_ids:
                remove += [ y.product_id.id for y in x.materiales2_ids]
            if x.transporte2_ids:
                remove += [ y.product_id.id for y in x.transporte2_ids]
            if x.mano_obra2_ids:
                remove += [ y.product_id.id for y in x.mano_obra2_ids]

        print 'remove',remove        
        line_ids = [ x for x in line_ids if x not in remove]
        print 'line_ids', line_ids
        context.update({'line_ids': line_ids})
        
        model_data_ids = mod_obj.search(cr, uid,[('model', '=', 'ir.ui.view'), ('name', '=', 'view_create_product_apu_lines')], context=context)
        resource_id = mod_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
        return {'name': ('Entradas Productos'),
                'context': context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'cyg.add.product.wiz',
                'views': [(resource_id,'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
        }
        
    
    def add_product(self, cr, uid, ids, context=None):
        print 'add_product', context
        apu_obj = self.pool.get('cyg.apu')
        product_obj = self.pool.get('product.product')
        #Escenario 1
        line_obj = self.pool.get('cyg.apu.line')
        if context is None:
            context = {}
        data = self.browse(cr, uid, ids, context=context)[0]
        product_ids = [entry.id for entry in data.lines]
        #print 'product_ids', product_ids
        #print 'active_id', context['active_id']
        if not product_ids:
            return {'type': 'ir.actions.act_window_close'}
        
        for line in product_obj.browse(cr, uid, product_ids, context=context):
            apu_equipo_id = False
            apu_material_id = False
            apu_transporte_id = False
            apu_mano_id = False
            apu_otro_id = False
            categ = line.product_tmpl_id.categ_id.name
            #print 'categ', categ
            if categ  == 'EQUIPOS Y HERRAMIENTAS':
                apu_equipo_id = context['active_id']
                #print 'apu_equipo_id',apu_equipo_id 
            elif categ == "MATERIALES":
                apu_material_id = context['active_id']
                #print 'apu_material_id',apu_material_id
            elif categ == "TRANSPORTE":
                apu_transporte_id = context['active_id']
                #print 'apu_transporte_id',apu_transporte_id
            elif categ == "MANO DE OBRA":
                apu_mano_id = context['active_id']
            else:
                apu_otro_id = context['active_id']
                #print 'apu_mano_id',apu_mano_id
            
            line_obj.create(cr, uid,{
                    #Ambiente 1
                    'equipo_id': apu_equipo_id,
                    'material_id': apu_material_id,
                    'transporte_id': apu_transporte_id,
                    'mano_id': apu_mano_id,
                    'otro_id':apu_otro_id,
                    'name':line.name,
                    'product_id':line.id,
                    'qty':1.00,
                    'uom_id':line.product_tmpl_id.uom_id and line.product_tmpl_id.uom_id.id or False,
                    'price':line.list_price or line.standard_price or 0.00,
                    'rendimiento':line.rendimiento,
                    'desperdicio':line.desperdicio,
                    
                }, context=context)
            line_obj.create(cr, uid,{
                    #Ambiente 2
                    'equipo2_id': apu_equipo_id,
                    'material2_id': apu_material_id,
                    'transporte2_id':apu_transporte_id ,
                    'mano2_id': apu_mano_id,
                    'otro2_id':apu_otro_id,
                    'name':line.name,
                    'product_id':line.id,
                    'qty':1.00,
                    'uom_id':line.product_tmpl_id.uom_id and line.product_tmpl_id.uom_id.id or False,
                    'price':line.list_price or line.standard_price or 0.00,
                    'rendimiento':line.rendimiento,
                    'desperdicio':line.desperdicio,
                    
                }, context=context)
        #apu_obj.button_dummy(cr,uid,context.get('active_ids'),context=context)
        return {'type': 'ir.actions.act_window_close'}
        #return {'type': 'ir.actions.client', 'tag': 'reload',}



    _columns = {
        'category_id': fields.many2one('product.category','Categoria'),
        'lines': fields.many2many('product.product', 'cyg_apu_rel_product', 'apu_id', 'product_id', 'Productos')
        }

cyg_add_product_wiz()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

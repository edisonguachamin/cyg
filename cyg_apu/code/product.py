# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today
#    CyG xxxx
#    @autor: Edison Guachamin <edison.guachamin@gmail.com>
#
##############################################################################
import math
import re

from _common import ceiling

from openerp import tools, SUPERUSER_ID
from openerp.osv import osv, fields
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp


class product_category(osv.osv):
    _inherit = 'product.category' 
    #Do not touch _name it must be same as _inherit
    #_name = 'openerpmodel'
#     def onchange_type(self,cr, uid, ids, fielname,code):
#         res={}
#         if fielname=='view':
#             res['code']=
#         return {'value':res}
    _columns = {
                'prefix':fields.char('Prefijo', size=10),
                'rendimiento':fields.float('Rendimiento'),
               }
product_category()


class product_template(osv.osv):
    _inherit = 'product.template'
     
    def _default_category(self, cr, uid, context=None):
        print '_default_category', context
        if context is None:
            context = {}
        if 'categ_id' in context and context['categ_id']:
            return context['categ_id']
        if 'name_categ_id' in context and context['name_categ_id']:
            categoria_ids = self.pool.get('product.category').search(cr, uid, [('name','=',context['name_categ_id'])])
            return categoria_ids and categoria_ids[0] or False
        md = self.pool.get('ir.model.data')
        res = False
        try:
            res = md.get_object_reference(cr, uid, 'product', 'product_category_all')[1]
        except ValueError:
            res = False
        return res
    
    _defaults = {
        
        'categ_id' : _default_category,
        
    }
product_template()


class product_product(osv.osv):
    _inherit = 'product.product' 
    #Do not touch _name it must be same as _inherit
    #_name = 'openerpmodel'
#     def onchange_type(self,cr, uid, ids, fielname,code):
#         res={}
#         if fielname=='view':
#             res['code']=
#         return {'value':res}
    
    def create(self, cr, uid, vals, context={}):
        print 'create product context#######', context
        print 'create product vals $$$$$$$$$', vals
        if vals.get('code','/')=='/':
            if 'categ_id' in vals and 'name_categ_id' not in context:
                info = self.pool.get('product.category').browse(cr, uid,vals.get('categ_id'))
                if info.name =='EQUIPOS Y HERRAMIENTAS':
                    sequence = self.pool.get('ir.sequence').get(cr, uid, 'cyg.categoria.equipo') or '/'
                elif info.name =='MANO DE OBRA':
                    sequence = self.pool.get('ir.sequence').get(cr, uid, 'cyg.categoria.mano_obra') or '/'
                elif info.name =='MATERIALES':
                    sequence = self.pool.get('ir.sequence').get(cr, uid, 'cyg.categoria.materiales') or '/'
                elif info.name =='TRANSPORTE':
                    sequence = self.pool.get('ir.sequence').get(cr, uid, 'cyg.categoria.transporte') or '/'
                elif info.name =='OTROS':
                    sequence = self.pool.get('ir.sequence').get(cr, uid, 'cyg.categoria.transporte') or '/'
                else:
                    sequence = False
                vals['code'] = sequence
                vals['default_code'] = sequence   
            if 'name_categ_id' in context and context['name_categ_id']:
                if context['name_categ_id']=='EQUIPOS Y HERRAMIENTAS':
                    sequence = self.pool.get('ir.sequence').get(cr, uid, 'cyg.categoria.equipo') or '/'
                elif context['name_categ_id']=='MANO DE OBRA':
                    sequence = self.pool.get('ir.sequence').get(cr, uid, 'cyg.categoria.mano_obra') or '/'
                elif context['name_categ_id']=='MATERIALES':
                    sequence = self.pool.get('ir.sequence').get(cr, uid, 'cyg.categoria.materiales') or '/'
                elif context['name_categ_id']=='TRANSPORTE':
                    sequence = self.pool.get('ir.sequence').get(cr, uid, 'cyg.categoria.transporte') or '/'
                elif context['name_categ_id']=='OTROS':
                    sequence = self.pool.get('ir.sequence').get(cr, uid, 'cyg.categoria.otros') or '/'
                    
                vals['code'] = sequence
                vals['default_code'] = sequence
        res_id = super(product_product, self).create(cr, uid, vals, context)
        return res_id 
    
    _columns = {
                'code':fields.char('Code', size=10),
                'rendimiento':fields.float('Rendimiento', digits=(16,6)),
                'desperdicio':fields.float('Desperdicio', digits=(16,6)),
               }
    _defaults = {
        
        'code' : lambda obj, cr, uid, context: '/',
        
    }
     
    
product_product()

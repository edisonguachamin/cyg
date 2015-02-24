# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today
#    CyG xxxx
#    @author: Jonathan Finlay <jfinlay@riseup.net>
#
##############################################################################

__author__ = 'Edison Guachamin'
import time
from osv import osv
from osv import fields
from lxml import etree



class importar_actividades_wiz(osv.osv_memory):
    _name = 'cyg.import_actividades_wiz'
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False,  submenu=False):
        res = super(importar_actividades_wiz, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar,submenu=submenu)
        if context and 'history_ids' in context:
            domain = '[("id", "in", '+ str(context['history_ids'])+')]'
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//field[@name='cyg_actividad_ids']")
            for node in nodes:
                node.set('domain', domain)
            res['arch'] = etree.tostring(doc)
        return res
    
    
    def search_actividades(self, cr, uid, ids, context={}):
        wiz = self.read(cr, uid, ids)[0]
        transferencia_obj = self.pool.get('cyg.transferencia_dominio')
        actividades_obj = self.pool.get('cyg.actividad')
        repetidos = []
        for item in transferencia_obj.browse(cr, uid, context.get('active_ids',[])):
            if item.actividades_ids:
                repetidos = [ x.actividad_id.id for x in item.actividades_ids]
        where = ''
        if wiz.get('tipo_actividad_id', False):
            where += " and group_id="+str(wiz.get('tipo_actividad_id', False)[0])
            
        sql = " select id from cyg_actividad where 1=1" + where
        cr.execute(sql)
        actividades = [aux[0] for aux in cr.fetchall()]
        
        s = [x for x in actividades if x not in repetidos]
        context.update({'history_ids': list(set(s))})
        mod_obj = self.pool.get('ir.model.data')
        model_data_ids = mod_obj.search(cr, uid,[('model', '=', 'ir.ui.view'), ('name', '=', 'cyg_import_actividades_wiz_lines')], context=context)
         
        resource_id = mod_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
        
        return {'name': ('Actividades'),
                'context': context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'cyg.import_actividades_wiz',
                'views': [(resource_id,'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
        }

    def add_actividades(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        line_ids = data['cyg_actividad_ids']
        
        if not line_ids:
            return {'type': 'ir.actions.act_window_close'}
        
        cyg_actividades = self.pool.get('cyg.actividad')
        
        cyg_dominio_actividades = self.pool.get('cyg.trans_dominio_actividad')
        
        for item in cyg_actividades.browse(cr,uid,line_ids):
                cyg_dominio_actividades.create(cr, uid,{'tranferencia_id':context.get('active_id'),
                       'grupo_id': item.group_id.id,
                       'actividad_id': item.id,
                       'dias_programados': item.dias,
                       #'fecha_ini': time.strftime('%Y-%m-%d')
                       },context=context)
        
        return {'type': 'ir.actions.client', 'tag': 'reload',}

    _columns = {
        'precio': fields.float('Precio', digits=(10,10)),
        'tipo_actividad_id':fields.many2one('cyg.actividad_grupo','Grupo'),
        'cyg_actividad_ids':fields.many2many('cyg.actividad','actividad_rel_import','wizard_id','actividad_id','Actividades'),
        
        #'asset_ids':fields.many2many('account.asset.asset','asset_rel_descargo','wizard_id','asset_id','Activos Fijos'),
        }

importar_actividades_wiz()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

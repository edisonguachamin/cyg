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

class importar_inmueble_act_wiz(osv.osv_memory):
    _name = 'cyg.import_inmueble_act_wiz'
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False,  submenu=False):
        #print "fields_view_get",context
        res = super(importar_inmueble_act_wiz, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar,submenu=submenu)
        if context and 'history_ids' in context:
            domain = '[("id", "in", '+ str(context['history_ids'])+')]'
            #print 'domain', domain
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//field[@name='cyg_actividad_ids']")
            for node in nodes:
                node.set('domain', domain)
            res['arch'] = etree.tostring(doc)
        return res
    
    
    def search_actividades(self, cr, uid, ids, context={}):
        print 'context', context
        wiz = self.read(cr, uid, ids)[0]
        print 'wiz', wiz
        inmueble_obj = self.pool.get('cyg.proyecto_inmueble')
        actividades_obj = self.pool.get('cyg.actividad')
        repetidos = []
        for item in inmueble_obj.browse(cr, uid, context.get('active_ids',[])):
            if item.actividades_ids:
                repetidos = [ x.actividad_id.id for x in item.actividades_ids]
        print 'repetidos', repetidos
        where = ''
        if wiz.get('tipo_actividad_id', False):
            where += " and group_id="+str(wiz.get('tipo_actividad_id', False)[0])
            
        sql = " select id from cyg_actividad where 1=1" + where
        cr.execute(sql)
        actividades = [aux[0] for aux in cr.fetchall()]
        
        s = [x for x in actividades if x not in repetidos]
        print "##################", s
        context.update({'history_ids': list(set(s))})
        mod_obj = self.pool.get('ir.model.data')
        model_data_ids = mod_obj.search(cr, uid,[('model', '=', 'ir.ui.view'), ('name', '=', 'cyg_importar_inmueble_ac_wiz_lines')], context=context)
         
        resource_id = mod_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
        
        return {'name': ('Actividades'),
                'context': context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'cyg.import_inmueble_act_wiz',
                'views': [(resource_id,'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
        }

    def add_actividades(self, cr, uid, ids, context=None):
       #print 'acta descargo act_anadir_activos', context
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        line_ids = data['cyg_actividad_ids']
        
        if not line_ids:
            return {'type': 'ir.actions.act_window_close'}
        
        sql = "select da.id, ga.sequence, da.secuencia from cyg_actividad as da , cyg_actividad_grupo as ga where da.group_id = ga.id and da.id in ("+','.join([str(x) for x in line_ids])+") order by ga.sequence"
        #print 'sql', sql
        cr.execute(sql)
        line_ids = [aux[0] for aux in cr.fetchall()]
        #print "line_ids", line_ids
        cyg_actividades = self.pool.get('cyg.actividad')
        
        cyg_inmueble_actividades = self.pool.get('cyg.proyecto_inmueble_actividad')
        #order_lines = cyg_inmueble_actividades.search(cr, uid, )
        for item in cyg_actividades.browse(cr,uid,line_ids):
                cyg_inmueble_actividades.create(cr, uid,{'inmueble_id':context.get('active_id'),
                       'grupo_id':item.group_id.id,
                       'actividad_id':item.id,
                       'dias_programados':item.dias,
                       #'fecha_ini':time.strftime('%Y-%m-%d'),
                       'sequence_grupo':item.group_id.sequence,
                       'sequence_actividad':item.secuencia,
                       },context=context)
        
        return {'type': 'ir.actions.client', 'tag': 'reload',}

    _columns = {
        'precio': fields.float('Precio', digits=(10,10)),
        'tipo_actividad_id':fields.many2one('cyg.actividad_grupo','Grupo'),
        'cyg_actividad_ids':fields.many2many('cyg.actividad','inmueble_actividad_rel_import','wizard_id','actividad_id','Actividades'),
        }

importar_inmueble_act_wiz()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

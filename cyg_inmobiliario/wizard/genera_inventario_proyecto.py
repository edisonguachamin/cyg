# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today
#    CyG xxxx
#    @author: Jonathan Finlay <jfinlay@riseup.net>
#
##############################################################################

from openerp.osv import fields, osv

class genera_inventario_proyecto_wiz(osv.osv):
    _name = 'cyg.genera_inventario_proyecto'

    def _check_etapas(self, cr, uid, ids, context=None):
        for wiz in self.browse(cr, uid, ids, context=context):
            if wiz.proyecto_id.num_etapas < len(wiz.etapa_ids):
                return False
        return True

    def _check_inmuebles(self, cr, uid, ids, context=None):
        for wiz in self.browse(cr, uid, ids, context=context):
            if wiz.proyecto_id.num_unidades < len(wiz.inmueble_ids):
                return False
        return True

    def _check_inmuebles_piso(self, cr, uid, ids, context=None):
        for wiz in self.browse(cr, uid, ids, context=context):
            unidades = 0
            for piso in wiz.piso_ids:
                unidades += piso.num_inmuebles
            if wiz.proyecto_id.num_unidades < unidades:
                return False
        return True

    def _check_inmuebles_etapa(self, cr, uid, ids, context=None):
        for wiz in self.browse(cr, uid, ids, context=context):
            unidades = 0
            for etapa in wiz.etapa_ids:
                unidades += etapa.unidades
            if wiz.proyecto_id.num_unidades < unidades:
                return False
        return True

    def default_get(self, cr, uid, fields, context=None):
        data = super(genera_inventario_proyecto_wiz, self).default_get(cr, uid, fields, context=context)
        print 'data', data
        data['pagina'] = 1
        data['proyecto_id'] = context['active_id']
        data['etapas'] = 0
        data['pisos'] = 0
        data['inmuebles'] = 0
        return data

    def genera_etapas(self, cr, uid, id, context=None):
        id = id[0]
        siguiente_pagina = 1
        proy_obj = self.pool.get('cyg.proyecto')
        etapa_obj = self.pool.get('cyg.proyecto_etapa')
        res = {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_type': 'wizard',
                'res_model': 'cyg.genera_inventario_proyecto',
                'nodestroy': 'true',
                'res_id': id,
                'views': [(False, 'form')],
                'target': 'new',
                'context': context,
            }
        if 'active_id' in context:
            proy_obj = proy_obj.browse(cr, uid, context['active_id'], context=context)
            etapas = proy_obj.num_etapas
            if not proy_obj.etapa_ids:
                for etapa in range(etapas):
                    etapa_obj.create(cr, uid, {'name': etapa + 1,
                                               'proyecto_id': context['active_id'],
                                               'wiz_id': id})
        self.write(cr, uid, id, {'pagina': siguiente_pagina, 'etapas': 1}, context=context)
        return res

    def etapa_ir_siguiente(self, cr, uid, id, context=None):
        id = id[0]
        proy_obj = self.pool.get('cyg.proyecto')
        siguiente_pagina = 2
        if 'active_id' in context:
            proy_obj = proy_obj.browse(cr, uid, context['active_id'], context=context)
            if not proy_obj.tiene_pisos:
                siguiente_pagina = 3
        res = {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_type': 'wizard',
                'res_model': 'cyg.genera_inventario_proyecto',
                'nodestroy': 'true',
                'res_id': id,
                'views': [(False, 'form')],
                'target': 'new',
            }
        self.write(cr, uid, id, {'pagina': siguiente_pagina}, context=context)
        return res

    def genera_pisos(self, cr, uid, id, context=None):
        id = id[0]
        siguiente_pagina = 2
        wiz_obj = self.browse(cr, uid, id, context=context)
        proy_obj = self.pool.get('cyg.proyecto')
        piso_obj = self.pool.get('cyg.proyecto_piso')
        res = {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_type': 'wizard',
                'res_model': 'cyg.genera_inventario_proyecto',
                'nodestroy': 'true',
                'res_id': id,
                'views': [(False, 'form')],
                'target': 'new',
                'context': context,
            }
        if 'active_id' in context:
            etapas = wiz_obj.etapa_ids
            proy_obj = proy_obj.browse(cr, uid, wiz_obj.proyecto_id.id, context=context)
            if proy_obj.tiene_pisos and not proy_obj.piso_ids:
                for etapa in etapas:
                    for piso in range(etapa.pisos):
                        piso_obj.create(cr, uid, {'proyecto_id': etapa.proyecto_id.id,
                                                  'etapa_id': etapa.id,
                                                  'wiz_id': id,
                                                  'name': piso + 1,
                                                  'numero': piso +1})
        self.write(cr, uid, id, {'pagina': siguiente_pagina, 'pisos': 1}, context=context)
        return res

    def piso_ir_siguiente(self, cr, uid, id, context=None):
        id = id[0]
        proy_obj = self.pool.get('cyg.proyecto')
        siguiente_pagina = 3
        res = {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'wizard',
            'res_model': 'cyg.genera_inventario_proyecto',
            'nodestroy': 'true',
            'res_id': id,
            'views': [(False, 'form')],
            'target': 'new',
        }
        self.write(cr, uid, id, {'pagina': siguiente_pagina}, context=context)
        return res

    def genera_inmuebles(self, cr, uid, id, context=None):
        id = id[0]
        siguiente_pagina = 3
        wiz_obj = self.browse(cr, uid, id, context=context)
        proy_obj = self.pool.get('cyg.proyecto')
        inmueble_obj = self.pool.get('cyg.proyecto_inmueble')
        res = {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_type': 'wizard',
                'res_model': 'cyg.genera_inventario_proyecto',
                'nodestroy': 'true',
                'res_id': id,
                'views': [(False, 'form')],
                'target': 'new',
                'context': context,
            }
        if 'active_id' in context:
            proy_obj = proy_obj.browse(cr, uid, wiz_obj.proyecto_id.id, context=context)
            if not proy_obj.inmueble_ids:
                if proy_obj.tiene_pisos:
                    pisos = wiz_obj.piso_ids
                    secuencial = 1
                    for piso in pisos:
                        if piso.num_inmuebles:
                            for inmueble in range(piso.num_inmuebles):
                                inmueble_obj.create(cr, uid, {'proyecto_id': piso.proyecto_id.id,
                                                              'etapa_id': piso.etapa_id.id,
                                                              'piso_id': piso.id,
                                                              'wiz_id': id,
                                                              'name': secuencial,
                                                              'numero': inmueble +1})
                                secuencial += 1
                else:
                    etapas = wiz_obj.etapa_ids
                    for etapa in etapas:
                        if etapa.unidades:
                            secuencial = 1
                            for inmueble in range(etapa.unidades):
                                inmueble_obj.create(cr, uid, {'proyecto_id': etapa.proyecto_id.id,
                                                              'etapa_id': etapa.id,
                                                              'wiz_id': id,
                                                              'name': secuencial,
                                                              'numero': inmueble +1})
                                secuencial += 1

        self.write(cr, uid, id, {'pagina': siguiente_pagina, 'inmuebles': 1}, context=context)
        return res

    def inmueble_ir_siguiente(self, cr, uid, id, context=None):
        id = id[0]
        wiz_obj = self.browse(cr, uid, id, context=context)
        proy_obj = self.pool.get('cyg.proyecto')
        proy_obj.write(cr, uid, wiz_obj.proyecto_id.id, {'state':'inventory'}, context=context)
        siguiente_pagina = 4
        res = {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'cyg.proyecto',
            'nodestroy': 'true',
            'res_id': wiz_obj.proyecto_id.id,
            'views': [(False, 'form')],
            'target': 'parent',
            'context': context,
            }

        self.write(cr, uid, id, {'pagina': siguiente_pagina}, context=context)
        return res

    def cancel(self, cr, uid, id, context=None):
        id = id[0]
        wiz_obj = self.browse(cr, uid, id, context=context)
        proyecto_id = wiz_obj.proyecto_id.id
        self.unlink(cr, uid, id, context=context)
        res = {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'cyg.proyecto',
            'nodestroy': 'true',
            'res_id': proyecto_id,
            'views': [(False, 'form')],
            'target': 'parent',
            'context': context,
            }
        return res

    _columns = {
        'proyecto_id': fields.many2one('cyg.proyecto', 'Proyecto', ondelete='cascade'),
        'pagina': fields.integer('Página'),
        'etapa_ids': fields.one2many('cyg.proyecto_etapa', 'wiz_id', 'Etapas'),
        'etapas': fields.boolean('Etapas'),
        'piso_ids': fields.one2many('cyg.proyecto_piso', 'wiz_id', 'Pisos'),
        'pisos': fields.boolean('Pisos'),
        'inmueble_ids': fields.one2many('cyg.proyecto_inmueble', 'wiz_id', 'Inmuebles'),
        'inmuebles': fields.boolean('Inmuebles'),
    }

    _default = {
        'pagina': lambda *x: 1,
    }


    _constraints = [
        (_check_etapas,'El número de etapas no puede superar el definido en la ficha General', ['etapa_ids']),
        (_check_inmuebles_etapa,'La suma de inmuebles por etapa no puede superar el definido en la ficha General', ['etapa_ids', 'unidades']),
        (_check_inmuebles,'El número de inmuebles no puede superar el definido en la ficha General', ['inmueble_ids']),
        (_check_inmuebles_piso,'La suma de inmuebles por piso no puede superar el definido en la ficha General', ['etapa_ids', 'unidades']),

    ]

genera_inventario_proyecto_wiz()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

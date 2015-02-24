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

class res_partner(osv.osv):
    """Herencia para extension de la clase res.partner """
    _name = 'res.partner'
    _inherit = 'res.partner'

    def name_get(self, cr, uid, ids, context=None):
        print 'context name_get', context
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            if context.get('show_address'):
                name = name + "\n" + self._display_address(cr, uid, record, without_company=True, context=context)
                name = name.replace('\n\n','\n')
                name = name.replace('\n\n','\n')
            if context.get('show_email') and record.email:
                name = "%s <%s>" % (name, record.email)
            res.append((record.id, name))
        return res

    def complete_name(self, cr, uid, id, nombre, apellido, context=None):
        if apellido:
            return {'value': {'name': "%s %s" % (apellido, nombre)}}
        return {'value': {'name': "%s" % (nombre)}}

    def onchange_type(self, cr, uid, ids, is_company, context=None):
        value = {}
        value['title'] = False
        if is_company:
            value['apellido'] = False
            domain = {'title': [('domain', '=', 'partner')]}
        else:
            domain = {'title': [('domain', '=', 'contact')]}
        return {'value': value, 'domain': domain}

    _columns = {
        'nombre': fields.char('Nombre', size=128, required=True),
        'apellido': fields.char('Apellido', size=128),
        'tercero': fields.boolean('Es tercero'),
        'licencia_profesional': fields.char('Licencia/matrícula Profesional',
                                            size=128),
        'estado_civil': fields.selection([('soltera', 'Soltero/a'),
                                          ('casada', 'Casado/a'),
                                          ('divorciada', 'Divorciado/a'),
                                          ('viuda', 'Viudo/a'),
                                          ('unida', 'Unión libre'),
                                          ], 'Estado civil'),
        'conyuge_id': fields.many2one('res.partner', 'Conyuge'),
        'separacion_bienes': fields.boolean('Separación de bienes'),
        'nro_tramite': fields.char('Número de tramite',
                                   size=128),
        'nacionalidad': fields.many2one('res.country', 'Nacionalidad'),
        'fecha_nacimiento': fields.date('Fecha de nacimiento'),
        'genero': fields.selection([('m', 'Masculino'),
                                    ('f', 'Femenino')], 'Genero'),
        'cargas_familiares': fields.integer('Cargas familiaries'),
        'nivel_educacion': fields.many2one('res.partner.education',
                                           'Nivel de educación'),
        'profesion': fields.many2one('res.partner.profession',
                                     'Profesión'),
        'vendedor': fields.boolean('Es empleado'),
    }

    def onchange_conyuge(self, cr, uid, id, estado_civil, conyuge, separacion, context=None):
        """Unir y separar a conyuges"""
        vals = {}
        if isinstance(id, list):
            id = id[0]
        partner = self.browse(cr, uid, id, context=context)
        if conyuge:
            vals['estado_civil'] = estado_civil
            vals['conyuge_id'] = id
            vals['separacion_bienes'] = separacion
        else:
            vals['estado_civil'] = estado_civil
            vals['separacion_bienes'] = separacion
        if partner.conyuge_id:
            self.write(cr, uid, partner.conyuge_id.id, vals, context=context)
        return {}


    _sql_constraints = [('unique_ref', 'unique(ref)', 'Ya existe un tercero con este documento')]

res_partner()


class res_partner_education(osv.osv):
    """Nivel de educación para res.partner """
    _name = 'res.partner.education'
    _description = 'Nivel de educación para res.partner'

    _columns = {
        'name': fields.char('Nivel de educación', size=64)
    }

res_partner_education()


class res_partner_profession(osv.osv):
    """Nivel de educación para res.partner """
    _name = 'res.partner.profession'
    _description = 'Nivel de educación para res.partner'

    _columns = {
        'name': fields.char('Profesión')
    }

res_partner_profession()
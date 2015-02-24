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
import time
import datetime

class proyecto(osv.osv):
    """Clase para la administración de proyectos inmobiliarios"""
    _name = 'cyg.proyecto'
    _description = "Clase para la administración de proyectos inmobiliarios"

    def _check_etapas(self, cr, uid, ids, context=None):
        for proyecto in self.browse(cr, uid, ids, context=context):
            if proyecto.num_etapas < len(proyecto.etapa_ids):
                return False
        return True

    def _check_inmuebles(self, cr, uid, ids, context=None):
        for proyecto in self.browse(cr, uid, ids, context=context):
            if proyecto.num_unidades < len(proyecto.inmueble_ids):
                return False
        return True

    def _check_inmuebles_etapa(self, cr, uid, ids, context=None):
        for proyecto in self.browse(cr, uid, ids, context=context):
            unidades = 0
            for etapa in proyecto.etapa_ids:
                unidades += etapa.unidades
            if proyecto.num_unidades < unidades:
                return False
        return True

    def _check_inmuebles_piso(self, cr, uid, ids, context=None):
        for proyecto in self.browse(cr, uid, ids, context=context):
            unidades = 0
            for piso in proyecto.piso_ids:
                unidades += piso.num_inmuebles
            if proyecto.num_unidades < unidades:
                return False
        return True

    def _calc_objetivos(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for proyecto in self.browse(cr, uid, ids, context=context):
            obj_logrado = 0.0
            obj_vigente = 0.0
            unidades_vendidas = 0
            for inmueble in proyecto.inmueble_ids:
                if inmueble.state == 'vendido':
                    unidades_vendidas += 1
                    obj_logrado += inmueble.precio_actual
                obj_vigente += inmueble.precio_actual
            cr.execute("""
select state, sum(cliente)
from cyg_inmueble_cuota
where state in ('paid','done') and
concepto in ('extraordinaria','descuento','penalizacion') and
project_id = %s
group by state""" % proyecto.id)
            data = cr.fetchall()
            for row in data:
                obj_vigente += row[1]
                obj_logrado += row[1]
            res[proyecto.id] = {
                'num_unidades_vendidas': unidades_vendidas,
                'objectivo_comercial': obj_logrado,
                'objectivo_comercial_vigente': obj_vigente
            }
        return res

    def _calc_m2(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for proyecto in self.browse(cr, uid, ids, context=context):
            m2_comunales = 0.0
            m2_comunales += proyecto.comunales_construidas_m2
            m2_comunales += proyecto.comunales_abiertas_m2
            m2_comunales += proyecto.porteria_construidas_m2
            m2_comunales += proyecto.porteria_abiertas_m2
            m2_comunales += proyecto.depositos_construidas_m2
            m2_comunales += proyecto.depositos_abiertas_m2
            m2_comunales += proyecto.vias_construidas_m2
            m2_comunales += proyecto.vias_abiertas_m2
            m2_comunales += proyecto.peatonal_construidas_m2
            m2_comunales += proyecto.peatonal_abiertas_m2
            m2_comunales += proyecto.estacionamientos_construidas_m2
            m2_comunales += proyecto.estacionamientos_abiertas_m2
            m2_comunales += proyecto.estac_visitas_construidas_m2
            m2_comunales += proyecto.estac_visitas_abiertas_m2
            m2_comunales += proyecto.otras_construidas_m2
            m2_comunales += proyecto.otras_abiertas_m2
            res[proyecto.id] = {
                'm2_construccion': proyecto.m2_vendibles + m2_comunales,
                'm2_comunales': m2_comunales,
            }
        return res

    def onchange_country(self, cr, uid, id, context=None):
        """ Return a dict to empty the relational fields """
        return {
            'value': {
                'state_id': False,
                'city_id': False,
                'parroquia_id': False,
            }
        }

    def onchange_state(self, cr, uid, id, context=None):
        """ Return a dict to empty the relational fields """
        return {
            'value': {
                'city_id': False,
                'parroquia_id': False,
            }
        }

    def onchange_city(self, cr, uid, id, context=None):
        """ Return a dict to empty the relational fields """
        return {
            'value': {
                'parroquia_id': False,
            }
        }

    def do_with_inventory(self, cr, uid, id, context=None):
        if isinstance(id, list):
            id = id[0]
        proy_obj = self.browse(cr, uid, id, context=context)
        etapas = len(proy_obj.etapa_ids)
        unidades = len(proy_obj.inmueble_ids)
        if etapas != proy_obj.num_etapas:
            raise osv.except_osv(u'Error de usuario!', u'El número de etapas definido no corresponde al creado')
        if unidades != proy_obj.num_unidades:
            raise osv.except_osv(u'Error de usuario!', u'El número de unidades (inmuebles) definido no corresponde al creado')
        self.write(cr, uid, id, {'state': 'inventory'}, context=context)
        return {}


    def delete_inventory(self, cr, uid, id, context=None):
        if isinstance(id, list):
            id = id[0]
        proy_obj = self.browse(cr, uid, id, context=context)
        etapa_obj = self.pool.get('cyg.proyecto_etapa')
        piso_obj = self.pool.get('cyg.proyecto_piso')
        inmueble_obj = self.pool.get('cyg.proyecto_inmueble')
        for etapa in proy_obj.etapa_ids:
            etapa_obj.unlink(cr, uid, etapa.id, context=context)
        for piso in proy_obj.piso_ids:
            piso_obj.unlink(cr, uid, piso.id, context=context)
        for inmueble in proy_obj.inmueble_ids:
            inmueble_obj.unlink(cr, uid, inmueble.id, context=context)
        self.write(cr, uid, id, {'state': 'draft'}, context=context)
        return {}

    def attachment_tree_view(self, cr, uid, ids, context):
        """ View a list of projects attachments """

        domain = [
            ('res_model', '=', 'cyg.proyecto'),
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

    _columns = {
        'image': fields.binary('Imagen'),
        'code': fields.char('Código', size=64, required=True),
        'name': fields.char('Nombre', size=64, required=True),
        'web_page': fields.char('Web', size=64),
        'country_id': fields.many2one('res.country', 'Pais'),
        'state_id': fields.many2one('res.country.state', 'Provincia'),
        'city_id': fields.many2one('res.country.city', 'Ciudad'),
        'parroquia_id': fields.many2one('res.country.parish', 'Parroquia'),
        'barrio': fields.char('Barrio', size=64),
        'address': fields.text('Dirección'),
        'long': fields.float('Longitud', digits=(10, 10)),
        'lat': fields.float('Latitud', digits=(10, 10)),
        'tipo_proyecto_id': fields.many2one('cyg.tipo_proyecto',
                                            'Tipo de proyecto'),
        'tasa_id':fields.many2one('cyg.tasa.interes','Interes'),
        'num_unidades': fields.integer('Unidades totales'),
        'm2_vendibles': fields.float('Construcción vendible (m2)',
                                     digits=(10, 2)),
        'm2_comunales': fields.function(_calc_m2, string='Áreas comunales (m2)',
                                        type='float', multi='m2'),
        'm2_construccion': fields.function(_calc_m2, string='Construcción total (m2)',
                                        type='float', multi='m2'),
        'num_estacionamientos': fields.integer('Estacionamientos para propietarios'),
        'num_estacionamientos_visitas': fields.integer('Estacionamientos para visitas'),
        'num_etapas': fields.integer('N° Etapas/torres/bloque'),
        'num_unidades_vendidas': fields.function(_calc_objetivos, string='Unidades vendidas',
                                        type='integer', multi='objetivos', store=False),
        'objectivo_comercial': fields.function(_calc_objetivos, string='Objectivo comercial logrado (USD)',
                                        type='float', multi='objetivos', store=False),
        'objectivo_comercial_planeado': fields.float('Objectivo comercial planeado (USD)',
                                            digits=(10, 2)),
        'objectivo_comercial_vigente': fields.function(_calc_objetivos, string='Objectivo comercial vigente (USD)',
                                        type='float', multi='objetivos', store=False),
        'especificacion_ids': fields.one2many('cyg.especificaciones_proyecto',
                                               'proyecto_id',
                                               'Especificaciones'),
        'arquitecto_id': fields.many2one('res.partner', 'Arquitecto/a'),
        'matricula_arquitecto_id': fields.related('arquitecto_id',
                                                  'licencia_profesional',
                                                  type='char',
                                                  relation='res.partner',
                                                  string='Matrícula/Licencia',
                                                  store=False, readonly=True),
        'fono_arquitecto_id': fields.related('arquitecto_id',
                                             'phone',
                                             type='char',
                                             relation='res.partner',
                                             string='Teléfono',
                                             store=False, readonly=True),
        'mail_arquitecto_id': fields.related('arquitecto_id',
                                             'email',
                                             type='char',
                                             relation='res.partner',
                                             string='E-mail',
                                             store=False, readonly=True),
        'estructural_id': fields.many2one('res.partner',
                                          'Diseño estructural'),
        'matricula_estructural_id': fields.related('estructural_id',
                                                   'licencia_profesional',
                                                   type='char',
                                                   relation='res.partner',
                                                   string='Matrícula/Licencia',
                                                   store=False, readonly=True),
        'fono_estructural_id': fields.related('estructural_id',
                                              'phone',
                                              type='char',
                                              relation='res.partner',
                                              string='Teléfono',
                                              store=False, readonly=True),
        'mail_estructural_id': fields.related('estructural_id',
                                              'email',
                                              type='char',
                                              relation='res.partner',
                                              string='E-mail',
                                              store=False, readonly=True),
        'electrico_id': fields.many2one('res.partner',
                                        'Diseño electrico'),
        'matricula_electrico_id': fields.related('electrico_id',
                                                 'licencia_profesional',
                                                 type='char',
                                                 relation='res.partner',
                                                 string='Matrícula/Licencia',
                                                 store=False, readonly=True),
        'fono_electrico_id': fields.related('electrico_id',
                                            'phone',
                                            type='char',
                                            relation='res.partner',
                                            string='Teléfono',
                                            store=False, readonly=True),
        'mail_electrico_id': fields.related('electrico_id',
                                            'email',
                                            type='char',
                                            relation='res.partner',
                                            string='E-mail',
                                            store=False, readonly=True),
        'hidrosanitario_id': fields.many2one('res.partner',
                                             'Diseño hidrosanitario'),
        'matricula_hidrosanitario_id': fields.related('hidrosanitario_id',
                                                      'licencia_profesional',
                                                      type='char',
                                                      relation='res.partner',
                                                      string='Matrícula/Licencia',
                                                      store=False, readonly=True),
        'fono_hidrosanitario_id': fields.related('hidrosanitario_id',
                                                 'phone',
                                                 type='char',
                                                 relation='res.partner',
                                                 string='Teléfono',
                                                 store=False, readonly=True),
        'mail_hidrosanitario_id': fields.related('hidrosanitario_id',
                                                 'email',
                                                 type='char',
                                                 relation='res.partner',
                                                 string='E-mail',
                                                 store=False, readonly=True),
        'interior_id': fields.many2one('res.partner',
                                       'Diseño interior'),
        'matricula_interior_id': fields.related('interior_id',
                                                'licencia_profesional',
                                                type='char',
                                                relation='res.partner',
                                                string='Matrícula/Licencia',
                                                store=False, readonly=True),
        'fono_interior_id': fields.related('interior_id',
                                           'phone',
                                           type='char',
                                           relation='res.partner',
                                           string='Teléfono',
                                           store=False, readonly=True),
        'mail_interior_id': fields.related('interior_id',
                                           'email',
                                           type='char',
                                           relation='res.partner',
                                           string='E-mail',
                                           store=False, readonly=True),
        'suelos_id': fields.many2one('res.partner',
                                     'Estudio de suelos'),
        'matricula_suelos_id': fields.related('suelos_id',
                                              'licencia_profesional',
                                              type='char',
                                              relation='res.partner',
                                              string='Matrícula/Licencia',
                                              store=False, readonly=True),
        'fono_suelos_id': fields.related('suelos_id',
                                         'phone',
                                         type='char',
                                         relation='res.partner',
                                         string='Teléfono',
                                         store=False, readonly=True),
        'mail_suelos_id': fields.related('suelos_id',
                                         'email',
                                         type='char',
                                         relation='res.partner',
                                         string='E-mail',
                                         store=False, readonly=True),
        'topografico_id': fields.many2one('res.partner',
                                          'Levantamiento topográfico'),
        'matricula_topografico_id': fields.related('topografico_id',
                                                   'licencia_profesional',
                                                   type='char',
                                                   relation='res.partner',
                                                   string='Matrícula/Licencia',
                                                   store=False, readonly=True),
        'fono_topografico_id': fields.related('topografico_id',
                                              'phone',
                                              type='char',
                                              relation='res.partner',
                                              string='Teléfono',
                                              store=False, readonly=True),
        'mail_topografico_id': fields.related('topografico_id',
                                              'email',
                                              type='char',
                                              relation='res.partner',
                                              string='E-mail',
                                              store=False, readonly=True),
        'constructor_id': fields.many2one('res.partner',
                                          'Constructor/a'),
        'matricula_constructor_id': fields.related('constructor_id',
                                                   'licencia_profesional',
                                                   type='char',
                                                   relation='res.partner',
                                                   string='Matrícula/Licencia',
                                                   store=False, readonly=True),
        'fono_constructor_id': fields.related('constructor_id',
                                              'phone',
                                              type='char',
                                              relation='res.partner',
                                              string='Teléfono',
                                              store=False, readonly=True),
        'mail_constructor_id': fields.related('constructor_id',
                                              'email',
                                              type='char',
                                              relation='res.partner',
                                              string='E-mail',
                                              store=False, readonly=True),
        'gerente_id': fields.many2one('res.partner',
                                      'Gerente/a de proyecto'),
        'matricula_gerente_id': fields.related('gerente_id',
                                               'licencia_profesional',
                                               type='char',
                                               relation='res.partner',
                                               string='Matrícula/Licencia',
                                               store=False, readonly=True),
        'fono_gerente_id': fields.related('gerente_id',
                                          'phone',
                                          type='char',
                                          relation='res.partner',
                                          string='Teléfono',
                                          store=False, readonly=True),
        'mail_gerente_id': fields.related('gerente_id',
                                          'email',
                                          type='char',
                                          relation='res.partner',
                                          string='E-mail',
                                          store=False, readonly=True),
        'fiscalizador_id': fields.many2one('res.partner',
                                           'Fiscalizador/a'),
        'matricula_fiscalizador_id': fields.related('fiscalizador_id',
                                                    'licencia_profesional',
                                                    type='char',
                                                    relation='res.partner',
                                                    string='Matrícula/Licencia',
                                                    store=False, readonly=True),
        'fono_fiscalizador_id': fields.related('fiscalizador_id',
                                               'phone',
                                               type='char',
                                               relation='res.partner',
                                               string='Teléfono',
                                               store=False, readonly=True),
        'mail_fiscalizador_id': fields.related('fiscalizador_id',
                                               'email',
                                               type='char',
                                               relation='res.partner',
                                               string='E-mail',
                                               store=False, readonly=True),
        'contador_id': fields.many2one('res.partner', 'Contador/a'),
        'matricula_contador_id': fields.related('contador_id',
                                                'licencia_profesional',
                                                type='char',
                                                relation='res.partner',
                                                string='Matrícula/Licencia',
                                                store=False, readonly=True),
        'fono_contador_id': fields.related('contador_id',
                                           'phone',
                                           type='char',
                                           relation='res.partner',
                                           string='Teléfono',
                                           store=False, readonly=True),
        'mail_contador_id': fields.related('contador_id',
                                           'email',
                                           type='char',
                                           relation='res.partner',
                                           string='E-mail',
                                           store=False, readonly=True),
        'lote_ids': fields.one2many('cyg.lote', 'proyecto_id', 'Lotes'),
        'agua_potable': fields.boolean('Agua potable'),
        'obs_agua_potable': fields.char('Observaciones', size=64),
        'alcantarillado': fields.boolean('Alcantarillado'),
        'obs_alcantarillado': fields.char('Observaciones', size=64),
        'electricidad': fields.boolean('Electricidad'),
        'obs_electricidad': fields.char('Observaciones', size=64),
        'telefono': fields.boolean('Teléfono'),
        'obs_telefono': fields.char('Observaciones', size=64),
        'tvcable': fields.boolean('Televisión por cable'),
        'obs_tvcable': fields.char('Observaciones', size=64),
        'bordillos': fields.boolean('Bordillos'),
        'obs_bordillos': fields.char('Observaciones', size=64),
        'calzada': fields.boolean('Calzada'),
        'obs_calzada': fields.char('Observaciones', size=64),
        'acera': fields.boolean('Acera'),
        'obs_acera': fields.char('Observaciones', size=64),
        'residencial': fields.boolean('Residencial'),
        'educacion': fields.boolean('Educación'),
        'iglesia': fields.boolean('Iglesia'),
        'espacio_deportivo': fields.boolean('Espacios deportivos'),
        'espacio_recreacion': fields.boolean('Espacios de recreación'),
        'municipio': fields.boolean('Gestión municipal'),
        'gobierno': fields.boolean('Gestión gubernamental'),
        'comercial': fields.boolean('Comercial'),
        'transporte': fields.boolean('Transporte'),
        'otros': fields.boolean('Otros'),
        'linea_presupuesto_ids': fields.one2many('cyg.proyecto_linea_presupuesto',
                                                 'proyecto_id',
                                                 'Línea de presupuesto'),
        'obs_residencial': fields.char('Observaciones', size=64),
        'obs_educacion': fields.char('Observaciones', size=64),
        'obs_iglesia': fields.char('Observaciones', size=64),
        'obs_espacio_deportivo': fields.char('Observaciones', size=64),
        'obs_espacio_recreacion': fields.char('Observaciones',
                                              size=64),
        'obs_municipio': fields.char('Observaciones', size=64),
        'obs_gobierno': fields.char('Observaciones', size=64),
        'obs_comercial': fields.char('Observaciones', size=64),
        'obs_transporte': fields.char('Observaciones', size=64),
        'obs_otros': fields.char('Observaciones', size=64),
        'num_regulacion': fields.char('N° IRM',
                                      size=64),
        'fecha_irm': fields.date('Fecha IRM'),
        'afectacion': fields.text('Afectación'),
        'clave_catastral': fields.char('Clave catastral',
                                       size=64),
        'num_predio': fields.char('N° predio',
                                  size=64),
        'altura_max': fields.float('Altura máxima edificaciones (m)',
                                   digits=(10, 2)),
        'retiro_frontal': fields.float('Retiro frontal (m)',
                                       digits=(10, 2)),
        'retiro_lateral': fields.float('Retiro lateral (m)',
                                       digits=(10, 2)),
        'retiro_posterior': fields.float('Retiro posterior (m)',
                                         digits=(10, 2)),
        'porcentaje_cos_pb': fields.float('% Cos PB',
                                          digits=(10, 2)),
        'porcentaje_cos_total': fields.float('% Cos total',
                                             digits=(10, 2)),
        'num_pisos': fields.integer('N° pisos'),
        'zonificacion': fields.char('Zonificación',
                                    size=64),
        'observaciones_datos_tecnicos': fields.text('Observaciones'),
        'permiso_bomberos': fields.many2one('cyg.estado_permiso_proyecto',
                                            'Permiso bomberos'),
        'fecha_bomberos': fields.date('Fecha'),
        'num_registro_bomberos': fields.char('N° registro', size=64),
        'planos_arquitectonicos': fields.many2one('cyg.estado_permiso_proyecto',
                                                  'Planos arquitectónicos'),
        'fecha_arquitectonico': fields.date('Fecha'),
        'num_registro_arquitectonico': fields.char('N° registro', size=64),
        'licencia_construccion': fields.many2one('cyg.estado_permiso_proyecto',
                                                 'Licencia de construcción'),
        'fecha_licencia_construccion': fields.date('Fecha'),
        'num_licencia_construccion': fields.char('N° registro', size=64),
        'permiso_ambiental': fields.many2one('cyg.estado_permiso_proyecto',
                                             'Permiso ambiental'),
        'fecha_ambiental': fields.date('Fecha'),
        'num_registro_ambiental': fields.char('N° registro', size=64),
        'permiso_aceras': fields.many2one('cyg.estado_permiso_proyecto',
                                          'Permiso de ocupación aceras '),
        'fecha_aceras': fields.date('Fecha'),
        'num_registro_aceras': fields.char('N° registro', size=64),
        'licencia_habitabilidad': fields.many2one('cyg.estado_permiso_proyecto',
                                                  'Licencia habitabilidad'),
        'fecha_habitabilidad': fields.date('Fecha'),
        'num_registro_habitabilidad': fields.char('N° registro', size=64),
        'permiso_trabajos': fields.many2one('cyg.estado_permiso_proyecto',
                                            'Permiso trabajos varios'),
        'fecha_trabajos': fields.date('Fecha'),
        'num_registro_trabajos': fields.char('N° registro', size=64),
        'permiso_vallas': fields.many2one('cyg.estado_permiso_proyecto',
                                          'Permiso vallas publicitarias'),
        'fecha_vallas': fields.date('Fecha'),
        'num_registro_vallas': fields.char('N° registro', size=64),
        'declaratoria_propiedad_horiz': fields.many2one('cyg.estado_permiso_proyecto',
                                                        'Decl. propiedad horizontal'),
        'fecha_otorgamiento_ph': fields.date('Fecha otorgamiento'),
        'fecha_inscripcion_ph': fields.date('Fecha inscripción'),
        'seguros_garantias_ids': fields.one2many('cyg.proyecto_linea_seguro',
                                                 'proyecto_id',
                                                 'Seguros y garantías'),
        'datos_bancarios_ids': fields.one2many('res.partner.bank',
                                               'proyecto_id',
                                               'Datos bancarios'),

        'etapa_ids': fields.one2many('cyg.proyecto_etapa', 'proyecto_id', 'Etapas'),
        'tiene_pisos': fields.boolean('Se requiere gestión de pisos'),
        'piso_ids': fields.one2many('cyg.proyecto_piso', 'proyecto_id', 'Pisos'),
        'inmueble_ids': fields.one2many('cyg.proyecto_inmueble', 'proyecto_id', 'Inmuebles'),
        'state': fields.selection([('draft', 'Borrador'),
                                   ('inventory', 'Con inventario'),
                                   ('process', 'En proceso'),
                                   ('done', 'Terminado'),
                                   ('cancel', 'Cancelado')], 'Estado'),
        'comunales_construidas_m2': fields.float('Construidas (m2)', digits=(10, 2)),
        'comunales_abiertas_m2': fields.float('Abiertas (m2)', digits=(10, 2)),
        'porteria_construidas_m2': fields.float('Construidas (m2)', digits=(10, 2)),
        'porteria_abiertas_m2': fields.float('Abiertas (m2)', digits=(10, 2)),
        'depositos_construidas_m2': fields.float('Construidas (m2)', digits=(10, 2)),
        'depositos_abiertas_m2': fields.float('Abiertas (m2)', digits=(10, 2)),
        'vias_construidas_m2': fields.float('Construidas (m2)', digits=(10, 2)),
        'vias_abiertas_m2': fields.float('Abiertas (m2)', digits=(10, 2)),
        'peatonal_construidas_m2': fields.float('Construidas (m2)', digits=(10, 2)),
        'peatonal_abiertas_m2': fields.float('Abiertas (m2)', digits=(10, 2)),
        'estacionamientos_construidas_m2': fields.float('Construidas (m2)', digits=(10, 2)),
        'estacionamientos_abiertas_m2': fields.float('Abiertas (m2)', digits=(10, 2)),
        'estac_visitas_construidas_m2': fields.float('Construidas (m2)', digits=(10, 2)),
        'estac_visitas_abiertas_m2': fields.float('Abiertas (m2)', digits=(10, 2)),
        'otras_construidas_m2': fields.float('Construidas (m2)', digits=(10, 2)),
        'otras_abiertas_m2': fields.float('Abiertas (m2)', digits=(10, 2)),
        'tipo_inmueble_ids': fields.one2many('cyg.tipo_inmueble', 'proyecto_id', 'Tipos de inmuebles'),
        'sequence_id': fields.many2one('ir.sequence', 'Secuencia para presupuestos')
        }

    def create(self, cr, uid, values, context=None):
        # Crear secuencia para lineas de presupuestos
        #print 'vals', vals
        seq_obj = self.pool.get('ir.sequence')
        seq_values = {'name': values['code'], 'padding': 3, 'implementation': 'no_gap'}
        values['sequence_id'] = seq_obj.create(cr, uid, seq_values)
        proyecto_id = super(proyecto, self).create(cr, uid, values, context=context)
        especificaciones_obj = self.pool.get('cyg.plantilla_especificaciones_proyecto')
        especificaciones_ids = especificaciones_obj.search(cr, uid, [], context=context)
        especificacion_proy_obj = self.pool.get('cyg.especificaciones_proyecto')
        for especificacion in especificaciones_obj.browse(cr, uid, especificaciones_ids, context=context):
            vals = {'proyecto_id': proyecto_id, 'name': especificacion.id}
            especificacion_proy_obj.create(cr, uid, vals, context=context)
        return proyecto_id
    
    def write(self, cr, uid, ids, vals, context=None):
        #TODO: process before updating resource
        print '###################', vals
        res = super(proyecto, self).write(cr, uid, ids, vals, context)
        return res 

    _constraints = [
        (_check_etapas,'El número de etapas no puede superar el definido en la ficha General', ['etapa_ids', 'num_etapas']),
        (_check_inmuebles_etapa,'La suma de inmuebles por etapa no puede superar el definido en la ficha General', ['etapa_ids', 'unidades']),
        (_check_inmuebles,'El número de inmuebles no puede superar el definido en la ficha General', ['inmueble_ids','num_unidades']),
        (_check_inmuebles_piso,'La suma de inmuebles por piso no puede superar el definido en la ficha General', ['inmueble_ids','num_unidades']),

    ]

    _sql_constraints = [('unique_code', 'unique(code)', u'Ya existe un proyecto con este código')]

    _defaults = {
        'country_id': 64,
        'state': 'draft',
        }

proyecto()


class proyecto_etapa(osv.osv):
    """Clase de administración de etapas"""

    _name = 'cyg.proyecto_etapa'
    _description = "Clase de administración de etapas"

    def _check_pisos(self, cr, uid, ids, context=None):
        for etapa in self.browse(cr, uid, ids, context=context):
            if etapa.pisos < len(etapa.piso_ids):
                return False
        return True
    
    def write(self, cr, uid, ids, vals, context=None):
        print 'write etapa',vals
        #TODO: process before updating resource
        res = super(proyecto_etapa, self).write(cr, uid, ids, vals, context)
        return res

    _columns = {
        'name': fields.char('Nombre', size=64, required=True),
        'pisos': fields.integer('Pisos'),
        'unidades': fields.integer('Inmuebles'),
        'proyecto_id': fields.many2one('cyg.proyecto', 'Proyecto', required=True, ondelete='cascade'),
        'wiz_id': fields.many2one('cyg.genera_inventario_proyecto', 'Wizard de creación', ondelete='cascade'),
        'piso_ids': fields.one2many('cyg.proyecto_piso', 'etapa_id', 'Pisos'),
        'presupuesto_id': fields.many2one('cyg.proyecto_linea_presupuesto', 'Presupuesto',
                                          domain=[('codigo', '=', 'cartera')]),
        }

    _sql_constraints = [('unique_name_proyecto', "unique(name, proyecto_id)",
                         'Ya existe una etapa con este nombre en el proyecto')]

    _constraints = [
        (_check_pisos,'El número de inmuebles no debe superar el definido en la ficha del piso', ['name', 'inmueble_ids']),
    ]

proyecto_etapa()


class proyecto_piso(osv.osv):
    """Clase para la administración de pisos inmuebles"""
    _name = 'cyg.proyecto_piso'
    _description = 'Clase para la administración de pisos inmuebles'

    def _check_inmuebles(self, cr, uid, ids, context=None):
        for piso in self.browse(cr, uid, ids, context=context):
            if piso.num_inmuebles < len(piso.inmueble_ids):
                return False
        return True

    _columns = {
        'proyecto_id': fields.many2one('cyg.proyecto', 'Proyecto', required=True, ondelete='cascade'),
        'name': fields.char('Nombre de piso', help="Ej. Mezannine, PB.", required=True),
        'numero': fields.char('Número del piso', required=True),
        'num_inmuebles': fields.integer('Número de inmuebles'),
        'inmueble_ids': fields.one2many('cyg.proyecto_inmueble', 'piso_id', 'Inmuebles'),
        'etapa_id': fields.many2one('cyg.proyecto_etapa', 'Etapa', required=True, ondelete='cascade'),
        'wiz_id': fields.many2one('cyg.genera_inventario_proyecto', 'Wizard de creación', ondelete='cascade'),
    }

    #_sql_constraints = [('unique_name_proyecto', "unique(name, proyecto_id)",
    #                     'Ya existe un piso con este nombre en el proyecto')]
    _constraints = [
        (_check_inmuebles, u'El número de inmuebles no debe superar el definido en la ficha del piso', ['name', 'inmueble_ids']),
    ]

proyecto_piso()


class proyecto_inmueble(osv.osv):
    """Clase para la administración de inmuebles"""
    _name = 'cyg.proyecto_inmueble'
    _description = 'Clase para la administración de inmuebles'

    def change_precio(self, cr, uid, ids, context=None):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'res.partner',
            'views': [('','form')],
            'type': 'ir.actions.act_window',
            }

    def onchange_tipo_inmueble(self, cr, uid, id, tipo_inmueble, context=None):
        value = {
            'area_terraza': 0,
            'area_balcon': 0,
            'area_cubierta': 0,
            'area_patio_privado': 0,
            'rooms': 0,
            'bathrooms': 0,
            'precio_actual': 0
        }
        if tipo_inmueble:
            tipo_inmueble = self.pool.get('cyg.tipo_inmueble').browse(cr, uid, tipo_inmueble, context=context)
            value = {
                'area_terraza': tipo_inmueble.area_terraza,
                'area_balcon': tipo_inmueble.area_balcon,
                'area_cubierta': tipo_inmueble.area_cubierta,
                'area_patio_privado': tipo_inmueble.area_patio_privado,
                'rooms': tipo_inmueble.rooms,
                'bathrooms': tipo_inmueble.bathrooms,
                'precio_actual': tipo_inmueble.precio
            }
        return {'value': value}
    
    def attachment_tree_view(self, cr, uid, ids, context):
        """ View a list of projects attachments """

        domain = [
            ('res_model', '=', 'cyg.proyecto_inmueble'),
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
        
    def name_get(self, cr, uid, ids, context=None):
        res = []
        name = ''
        for line in self.browse(cr, uid, ids, context=context):
            name = line.numero or '/'
            res.append((line.id, name))
            
        return res
    
    

    _columns = {
        'proyecto_id': fields.many2one('cyg.proyecto', 'Proyecto', ondelete='cascade'),
        'etapa_id': fields.many2one('cyg.proyecto_etapa', 'Etapa', ondelete='cascade'),
        'piso_id': fields.many2one('cyg.proyecto_piso', 'Piso', ondelete='cascade'),
        'parent_id': fields.many2one('cyg.proyecto_inmueble', 'Inmueble padre', ondelete='cascade'),
        'name': fields.char('Código', size=64, required=True),
        'numero': fields.char('Número', required=True),
        'tipo_inmueble_id': fields.many2one('cyg.tipo_inmueble', 'Tipo'),
        'historico_precio_ids': fields.one2many('cyg.historico_precios_inmueble',
                                                'inmueble_id',
                                                'Historico de precios'),
        'precio_actual': fields.float('Precio de venta', digits=(10, 2)),
        'area_cubierta': fields.float('Área cubierta (m2)', digits=(10, 2)),
        'area_terraza': fields.float('Área terraza (m2)', digits=(10, 2)),
        'area_balcon': fields.float('Área balcón (m2)', digits=(10, 2)),
        'area_patio_privado': fields.float('Área patio privado (m2)', digits=(10, 2)),
        'rooms': fields.integer('N° Habitaciones'),
        'bathrooms': fields.float('N° Baños'),
        'predio': fields.char('Predio', size=64),
        'linderos': fields.text('Linderos'),
        'certificado_gravamen': fields.char('Número certiicado gravamen',
                                            size=64),
        'fecha_gravamen': fields.date('Fecha emisión'),
        'state': fields.selection([('disponible', 'Disponible'),
                                   ('reservado', 'Reservado'),
                                   ('vendido', 'Vendido'),
                                   ('desistido', 'Desistido')], 'Estado'),
        'wiz_id': fields.many2one('cyg.genera_inventario_proyecto', 'Wizard de creación', ondelete='cascade'),
        'clase_inmueble': fields.selection([('base', 'Base'),
                                            ('parqueadero', 'Parqueadero'),
                                            ('bodega', 'Bodega')],
                                           'Clase de inmueble',
                                           help="Filtro aplicado para definir clase de inmueble. ej. Base tiene parqueaderos"),
        'parqueadero_ids': fields.one2many('cyg.proyecto_inmueble', 'parent_id', 'Parqueaderos',
                                           domain=[('clase_inmueble','=','parqueadero')]),
        'bodega_ids': fields.one2many('cyg.proyecto_inmueble', 'parent_id', 'Bodegas',
                                      domain=[('clase_inmueble','=','bodega')]),
        'tiene_precio': fields.boolean('Tiene precio'),
        'costo': fields.float('Precio de costo', digits=(10, 2)),
        'alicuota': fields.float('Alicuota (%)', digits=(10, 2)),
        'actividades_ids': fields.one2many('cyg.proyecto_inmueble_actividad', 'inmueble_id', 'Actividades'),
        'cash_management': fields.char('Código Cash management', size=128),
    }

    def create(self, cr, uid, vals, context=None):
        if 'precio_actual' in vals:
            vals['tiene_precio'] = True
        return super(proyecto_inmueble, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, values, context=None):
        if isinstance(ids, list):
            ids = ids[0]
        if 'precio_actual' in values:
            values['tiene_precio'] = True
        return super(proyecto_inmueble, self).write(cr, uid, ids, values, context=context)

    #_sql_constraints = [('unique_name_proyecto', "unique(name, proyecto_id)",
    #                     'Ya existe un inmueble con este nombre en el proyecto')]

    _defaults = {
        'state': 'disponible',
        'clase_inmueble': 'base'
    }

proyecto_inmueble()

class inmueble_actividad(osv.osv):
    """Clase para la administración de actividades en las transferencias
    de dominio"""
    _name = 'cyg.proyecto_inmueble_actividad'
    _description = 'Clase para la administración de actividades'
    _order = 'grupo_id asc, sequence_actividad asc'

    def onchange_grupo(self, cr, uid, id, context=None):
        return {'value': {'actividad_id': False}}
    
    def onchange_date(self, cr, uid, id, start, end, context=None):
        import time
        if start:
            self.write(cr, uid, id, {'state': 'open'})
        if start and start > time.strftime('%Y-%m-%d'):
            value = {
                'fecha_ini': False
            }
            return {
                'value': value,
                'warning': {
                    'title': 'Error de usuario',
                    'message': 'La fecha de inicio no puede ser futura'
                }
            }
        if start and end:
            if end > time.strftime('%Y-%m-%d'):
                value = {
                    'fecha_fin': False
                }
                return {
                    'value': value,
                    'warning': {
                        'title': 'Error de usuario',
                        'message': 'La fecha de fin no puede ser futura'
                    }
                }
            if start > end:
                value = {
                    'fecha_fin': False
                }
                return {
                    'value': value,
                    'warning': {
                        'title': 'Error de usuario',
                        'message': 'La fecha de inicio es mayor a la fin'
                    }
                }
        return {}

    def _dias_transcurridos(self, cr, uid, id, field_name, arg, context=None):
        res = {}
        for actividad in self.browse(cr, uid, id, context=context):
            if 'fecha_ini' in actividad and actividad.fecha_ini:
                y1, m1, d1 = (int(x) for x in actividad.fecha_ini.split('-'))
                if 'fecha_fin' in actividad and actividad.fecha_fin:
                    y2, m2, d2 = (int(x) for x in actividad.fecha_fin.split('-'))
                else:
                    now = datetime.datetime.now()
                    y2, m2, d2 = now.year, now.month, now.day
                datediff = datetime.date(y2, m2, d2) - datetime.date(y1, m1, d1)
                res[actividad.id] = datediff.days
            else:
                res[actividad.id] = 0
        return res


    def onchange_actividad(self, cr, uid, id, actividad_id, context=None):
        dias = 0
        grupo = False
        sequence_grupo = '1.00'
        sequence_actividad = '1.00'
        if actividad_id:
            actividad = self.pool.get('cyg.actividad').browse(cr, uid, actividad_id, context=context)
            dias = actividad.dias
            grupo = actividad.group_id.id
            sequence_grupo = actividad.group_id.sequence or '1.00'
            sequence_actividad = actividad.secuencia or '1.00'
        return {
            'value': {
                'dias_programados': dias,
                'grupo_id': grupo,
                'sequence_actividad':sequence_actividad,
                'sequence_grupo':sequence_grupo,
            }
        }

    _columns = {
        'inmueble_id': fields.many2one('cyg.proyecto_inmueble',
                                           'Inmuebles'),
        'grupo_id': fields.many2one('cyg.actividad_grupo',
                                    'Grupo'),
        'actividad_id': fields.many2one('cyg.actividad',
                                        'Actividad', required=True),
        'dias_programados': fields.integer('Días programados'),
        'fecha_ini': fields.date('Fecha inicio'),
        'fecha_fin': fields.date('Fecha fin'),
        'dias_diferencia': fields.function(_dias_transcurridos, string='Días transcurridos',
                                           type='integer'),
        'persona_entrega_id': fields.many2one('res.partner', 'Entrega'),
        'persona_recibe_id': fields.many2one('res.partner', 'Recibe'),
        'ubicacion': fields.char('Ubicación', size=64),
        'factura_ids': fields.one2many('cyg.actividad_factura', 'actividad_id',
                                       'Facturas'),
        'observacion': fields.text('Observaciones'),
        'state': fields.selection([('draft', 'Borrador'), ('open', 'Abierta'), ('close', 'Cerrada')], 'Estado'),
        'sequence_grupo': fields.char('Secuencia Grupo', size=5),
        'sequence_actividad': fields.char('Secuencia actividad', size=5)
    }

    def create(self, cr, uid, values, context=None):
        if 'fecha_fin' in values and values['fecha_fin']:
            values['state'] = 'close'
        return super(inmueble_actividad, self).create(cr, uid, values, context=context)

    def write(self, cr, uid, ids, values, context=None):
        if 'fecha_fin' in values and values['fecha_fin']:
            values['state'] = 'close'
        return super(inmueble_actividad, self).write(cr, uid, ids, values, context=context)

    _defaults = {
        'state': 'draft',
        'sequence_grupo':'1.00',
        'sequence_actividad':'1.00'
    }

inmueble_actividad()


class proyecto_linea_presupuesto(osv.osv):
    """Lineas de presupuestos en proyecto"""
    _name = 'cyg.proyecto_linea_presupuesto'
    _description = "Lineas de presupuestos en proyecto"

    def onchange_date(self, cr, uid, id, start, end, fields, context=None):
        if start and end and start > end:
            if fields == 'real':
                value = {
                    'ini_real_obra': False,
                    'fin_real_obra': False
                    }
            elif fields == 'prog':
                value = {
                    'ini_prog_obra': False,
                    'fin_prog_obra': False
                    }

            return {
                'value': value,
                'warning': {
                    'title': 'Error de usuario',
                    'message': 'La fecha de fin es mayor a la inicio'
                }
            }
        return {}

    def _get_next_code(self, cr, uid, context=None):
        proyecto_obj = self.pool.get('cyg.proyecto')
        sequence_obj = self.pool.get('ir.sequence')
        proyecto =proyecto_obj.browse(cr, uid, context['proyecto_id'])
        return sequence_obj.next_by_id(cr, uid, proyecto.sequence_id.id)
    
    def onchange_tipo_presupuesto(self, cr, uid, ids, field):
        res  = {'value':{}}
        type_obj = self.pool.get('cyg.type.presupuesto')
        if field:
            type_info = type_obj.browse(cr,uid,field)
            res['value']['codigo']=type_info.code
        return res

    _columns = {
        'code': fields.char('Código', size=64),
        'name': fields.char('Nombre', size=64),
        # 'tipo_presupuesto_id': fields.selection([('directo', 'Costos directos'),
                                                 # ('indirecto', 'Costos indirectos'),
                                                 #------ ('cartera', 'Cartera'),
                                                 # ('sala_ventas', 'Sala de ventas'),
                                                 #------ ('oficina', 'Oficina'),
                                                 #--- ], 'Tipo de presupuesto'),
        'tipo_presupuesto_id':fields.many2one('cyg.type.presupuesto','Tipo de Presupuesto'),
        'codigo':fields.char('Codigo',size=100),
        'director_id': fields.many2one('res.partner','Director/a o residente'),
        'bodeguero_id': fields.many2one('res.partner', 'Bodeguero/a'),
        'proyecto_id': fields.many2one('cyg.proyecto', 'Proyecto'),
        'ini_real_obra': fields.date('Inicio real de la obra'),
        'fin_real_obra': fields.date('Fin real de la obra'),
        'ini_prog_obra': fields.date('Inicio programado de la obra'),
        'fin_prog_obra': fields.date('Fin programado de la obra'),
        'punto_equi_real': fields.date('Punto de equilibrio real'),
        'punto_equi_prog': fields.date('Punto de equilibrio programado'),
        'venta_real': fields.date('Venta real'),
        'venta_prog': fields.date('Venta programada'),
        'ini_oficina': fields.date('Inicio'),
        'fin_oficina': fields.date('Fin'),
        }

    _defaults = {
        'ini_oficina': lambda *a: time.strftime('%Y-%m-%d'),
        'fin_oficina': lambda *a: time.strftime('%Y-%m-%d'),
        'code': _get_next_code,
    }

    _sql_constraints = [
        ('unique_name', "unique(name, proyecto_id)", u'Ya existe un presupuesto con ese nombre'),
        ('unique_code', "unique(code, proyecto_id)", u'Ya existe un presupuesto con ese código')
    ]

proyecto_linea_presupuesto()


class proyecto_linea_seguro(osv.osv):
    """Lineas de seguros y garantias en proyecto"""
    _name = 'cyg.proyecto_linea_seguro'
    _description = "Lineas de seguros y garantias en proyecto"

    _columns = {
        'proyecto_id': fields.many2one('cyg.proyecto',
                                       'Proyecto', ondelete='cascade'),
        'tipo_poliza_id': fields.many2one('cyg.tipo_poliza',
                                          'Tipo de poliza'),
        'name': fields.char('N° poliza', size=64),
        'proyecto': fields.char('Proyecto o beneficiario', size=64),
        'objeto': fields.char('Objeto', size=64),
        'estado': fields.selection([('vigente', 'Vigente'),
                                    ('terminado', 'Terminado'),
                                    ('liberado', 'Liberado')],
                                   'Estado'),
        'fecha_desde': fields.date('Fecha desde'),
        'fecha_hasta': fields.date('Fecha hasta'),
        'valor_asegurado': fields.float('Valor asegurado',
                                        digits=(10, 2)),
        'tasa': fields.float('Tasa %',
                             digits=(10, 2)),
        'prima': fields.float('Prima',
                              digits=(10, 2)),
        'partner_id': fields.many2one('res.partner', 'Tercero'),
        }

proyecto_linea_seguro()


class plantilla_especificaciones_proyecto(osv.osv):
    """Clase para la administración de la plantilla especificaciones"""
    _name = 'cyg.plantilla_especificaciones_proyecto'
    _description = "Clase para la administración de la plantilla"

    _columns = {
        'name': fields.char('Nombre', size=64),
        'description': fields.text('Descripción'),
        }

plantilla_especificaciones_proyecto()


class especificaciones_proyecto(osv.osv):
    """Clase para la administración de especificaciones de proyectos"""
    _name = 'cyg.especificaciones_proyecto'
    _description = "Clase para la administración de especificaciones"

    _columns = {
        'proyecto_id': fields.many2one('cyg.proyecto', 'Proyecto', readonly=True, ondelete='cascade'),
        'name': fields.many2one('cyg.plantilla_especificaciones_proyecto', 'Nombre'),
        'description': fields.text('Descripción'),
        }

especificaciones_proyecto()


class estado_permiso_proyecto(osv.osv):
    """Clase para la administración de los estados de aprobaciones y
    permisos"""
    _name = 'cyg.estado_permiso_proyecto'
    _description = "Clase para la administración de estados de aprobaciones"

    _columns = {
        'name': fields.char('Nombre', size=64),
        'description': fields.text('Descripción'),
        }

estado_permiso_proyecto()


class tipo_poliza(osv.osv):
    """Clase para la administración de los tipos de polizas"""
    _name = 'cyg.tipo_poliza'
    _description = "Clase para la administración de tipos de polizas"

    _columns = {
        'name': fields.char('Nombre', size=64),
        'description': fields.text('Descripción'),
        }

tipo_poliza()


class tipo_proyecto(osv.osv):
    """Clase para la administración de tipos de proyectos"""
    _name = 'cyg.tipo_proyecto'
    _description = "Clase para la administración de tipos de proyectos"

    _columns = {
        'name': fields.char('Nombre', size=64),
        'description': fields.text('Descripción'),
        }

    _sql_constraints = [('unique_name', 'unique(name)', 'Ya existe un tipo de proyecto con este nombre.')]

tipo_proyecto()


class tipo_inmueble(osv.osv):
    """Clase para la administración de tipos de inmuebles"""
    _name = 'cyg.tipo_inmueble'
    _description = "Clase para la administración de tipos de inmuebles"

    _columns = {
        'image': fields.binary('Imagen'),
        'proyecto_id': fields.many2one('cyg.proyecto', 'Proyecto', ondelete='cascade'),
        'name': fields.char('Nombre', size=64),
        'description': fields.text('Descripción'),
        'area_cubierta': fields.float('Área cubierta (m2)', digits=(10,2)),
        'area_terraza': fields.float('Área terraza (m2)', digits=(10,2)),
        'area_balcon': fields.float('Área balcón (m2)', digits=(10,2)),
        'area_patio_privado': fields.float('Área patio privado (m2)', digits=(10,2)),
        'rooms': fields.integer('N° Habitaciones'),
        'bathrooms': fields.float('N° Baños', digits=(10,2)),
        'precio': fields.float('Precio ($)', digits=(10,2)),
        }

    _sql_constraints = [('unique_name_proyecto', "unique(name, proyecto_id)",
                         'Ya existe un tipo de inmueble con este nombre en el proyecto')]

tipo_inmueble()


class historico_precios_inmueble(osv.osv):
    """Clase historico de precios de inmuebles"""

    _name = 'cyg.historico_precios_inmueble'
    _description = "Clase historico de precios de inmuebles"

    _columns = {
        'inmueble_id': fields.many2one('cyg.proyecto_inmueble', 'Inmueble', required=True, ondelete='cascade'),
        'precio_anterior': fields.float('Precio anterior', digits=(10, 2)),
        'precio_actual': fields.float('Precio nuevo', digits=(10, 2)),
        'usuario_cambio': fields.many2one('res.users', 'Usuario', required=True),
        'date': fields.datetime('Fecha', required=True),
        }

historico_precios_inmueble()



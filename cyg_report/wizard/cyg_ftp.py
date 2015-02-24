# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today
#    CyG xxxx
#    @autor: Edison Guachamin <edison.guachamin@gmail.com>
#
##############################################################################
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

from openerp.osv import fields, osv
import time
from lxml import etree


class cyg_ftp_report(osv.osv_memory):
    _name = 'cyg.ftp.report'
    _description = 'CYG FTP Browse'

    _columns = {
        'url' : fields.char('FTP Server', size=64, required=True),
        'modulo_id':fields.many2one('ir.module.module','Modulo')
    }

    def default_get(self, cr, uid, fields, context=None):
        print 'fields', fields
        res = {}
        if 'url' in fields:
            ftp_obj = self.pool.get('cyg.report.ftp')
            ftp_ids = ftp_obj.search(cr, uid,[('active','=',True)])
            if ftp_ids:
                ftp_info = ftp_obj.browse(cr, uid,ftp_ids[0])
                res['url'] = ftp_info.name
            else:
                ftp_ids = ftp_obj.search(cr, uid,[])
                if ftp_ids:
                    ftp_info = ftp_obj.browse(cr, uid,ftp_ids[0])
                    res['url'] = ftp_info.name
                else:
                    res['url'] = 'ftp://181.211.10.190'
        return res

    def browse_ftp(self, cr, uid, ids, context=None):
        data_id = ids and ids[0] or False
        data = self.browse(cr, uid, data_id, context=context)
        final_url = data.url
        return {
        'type': 'ir.actions.act_url',
        'url':final_url,
        'target': 'new'
        }

cyg_ftp_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

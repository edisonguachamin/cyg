from openerp.osv import osv, fields

class mail_message(osv.Model):
    """ Messages model: system notification (replacing res.log notifications),
        comments (OpenChatter discussion) and incoming emails. """
    _inherit = 'mail.message'

    _columns = {
        'to_read': fields.boolean('TO read')
    }

    _defaults = {
        'to_read': False
    }

mail_message()
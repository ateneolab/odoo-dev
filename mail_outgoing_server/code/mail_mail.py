# -*- coding: utf-8 -*-
##############################################################################
#
#    E-Invoice Module - Ecuador
#    Copyright (C) 2014 VIRTUALSAMI CIA. LTDA. All Rights Reserved
#    alcides@virtualsami.com.ec
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp
from openerp import models, fields, api, _, osv, tools

SUPERUSER_ID = 1

import base64
import psycopg2
from openerp.addons.base.ir.ir_mail_server import MailDeliveryException

import logging
_logger = logging.getLogger(__name__)


class email_template(models.Model):
    _inherit = 'email.template'

    @api.cr_uid_id_context
    def send_mail(self, cr, uid, template_id, res_id, force_send=False, raise_exception=False, server_id=False, context=None):
        """Generates a new mail message for the given template and record,
           and schedules it for delivery through the ``mail`` module's scheduler.

           :param int template_id: id of the template to render
           :param int res_id: id of the record to render the template with
                              (model is taken from the template)
           :param bool force_send: if True, the generated mail.message is
                immediately sent after being created, as if the scheduler
                was executed for this message only.
           :returns: id of the mail.message that was created
        """

        if context is None:
            context = {}
        mail_mail = self.pool.get('mail.mail')
        ir_attachment = self.pool.get('ir.attachment')

        # create a mail_mail based on values, without attachments
        values = self.generate_email(cr, uid, template_id, res_id, context=context)
        if not values.get('email_from'):
            raise osv.except_osv(_('Warning!'), _(
                "Sender email is missing or empty after template rendering. Specify one to deliver your message"))
        values['recipient_ids'] = [(4, pid) for pid in values.get('partner_ids', list())]
        attachment_ids = values.pop('attachment_ids', [])
        attachments = values.pop('attachments', [])
        msg_id = mail_mail.create(cr, uid, values, context=context)
        mail = mail_mail.browse(cr, uid, msg_id, context=context)

        # manage attachments
        for attachment in attachments:
            attachment_data = {
                'name': attachment[0],
                'datas_fname': attachment[0],
                'datas': attachment[1],
                'res_model': 'mail.message',
                'res_id': mail.mail_message_id.id,
            }
            context = dict(context)
            context.pop('default_type', None)
            attachment_ids.append(ir_attachment.create(cr, uid, attachment_data, context=context))
        if attachment_ids:
            values['attachment_ids'] = [(6, 0, attachment_ids)]
            mail_mail.write(cr, uid, msg_id, {'attachment_ids': [(6, 0, attachment_ids)]}, context=context)

        """if server_id in [2, 3]: # Cable
            server_id = 6"""

        if server_id:
            mail_mail.write(cr, uid, [mail.id], {'mail_server_id': server_id}, context=context)

        if force_send:
            mail_mail.send(cr, uid, [msg_id], raise_exception=raise_exception, context=context)
        return msg_id

class ir_mail_server(models.Model):
    _inherit = "ir.mail_server"

    company_id = fields.Many2one('res.company', string=u'Company')
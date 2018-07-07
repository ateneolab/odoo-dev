# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mail_attach_existing_attachment,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mail_attach_existing_attachment is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     mail_attach_existing_attachment is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with mail_attach_existing_attachment.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)
from openerp import tools
import base64

DOC_TYPE_NAME = {
    'out_invoice': 'Factura',
    'credit_note': 'Nota_Credito',
    'debit_note': 'Nota_Debito'
}


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def default_get(self, fields_list):
        res = super(MailComposeMessage, self).default_get(fields_list)
        if res.get('res_id') and res.get('model') and \
                res.get('composition_mode', '') != 'mass_mail' and\
                not res.get('can_attach_attachment'):
            res['can_attach_attachment'] = True
        return res

    can_attach_attachment = fields.Boolean(string='Can Attach Attachment')
    object_attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        relation='mail_compose_message_ir_attachments_object_rel',
        column1='wizard_id', column2='attachment_id', string='Attachments')

    @api.model
    def get_mail_values(self, wizard, res_ids):
        res = super(MailComposeMessage, self).get_mail_values(wizard, res_ids)
        _logger.info('RES-2: %s' % res)
        if wizard.object_attachment_ids.ids and wizard.model and\
                len(res_ids) == 1:
            for res_id in res_ids:
                if not res[res_id].get('attachment_ids'):
                    res[res_id]['attachment_ids'] = []
                res[res_id]['attachment_ids'] = wizard.object_attachment_ids.ids #.extend(wizard.object_attachment_ids.ids)
        _logger.info('RES-3: %s' % res)
        return res
        
    
    def default_get(self, cr, uid, fields, context=None):
        """ Handle composition mode. Some details about context keys:
            - comment: default mode, model and ID of a record the user comments
                - default_model or active_model
                - default_res_id or active_id
            - reply: active_id of a message the user replies to
                - default_parent_id or message_id or active_id: ID of the
                    mail.message we reply to
                - message.res_model or default_model
                - message.res_id or default_res_id
            - mass_mail: model and IDs of records the user mass-mails
                - active_ids: record IDs
                - default_model or active_model
        """
        if context is None:
            context = {}
        result = super(MailComposeMessage, self).default_get(cr, uid, fields, context=context)

        # v6.1 compatibility mode
        result['composition_mode'] = result.get('composition_mode', context.get('mail.compose.message.mode', 'comment'))
        result['model'] = result.get('model', context.get('active_model'))
        result['res_id'] = result.get('res_id', context.get('active_id'))
        result['parent_id'] = result.get('parent_id', context.get('message_id'))

        if not result['model'] or not self.pool.get(result['model']) or not hasattr(self.pool[result['model']], 'message_post'):
            result['no_auto_thread'] = True

        # default values according to composition mode - NOTE: reply is deprecated, fall back on comment
        if result['composition_mode'] == 'reply':
            result['composition_mode'] = 'comment'
        vals = {}
        if 'active_domain' in context:  # not context.get() because we want to keep global [] domains
            vals['use_active_domain'] = True
            vals['active_domain'] = '%s' % context.get('active_domain')
        if result['composition_mode'] == 'comment':
            vals.update(self.get_record_data(cr, uid, result, context=context))

        for field in vals:
            if field in fields:
                result[field] = vals[field]

        # TDE HACK: as mailboxes used default_model='res.users' and default_res_id=uid
        # (because of lack of an accessible pid), creating a message on its own
        # profile may crash (res_users does not allow writing on it)
        # Posting on its own profile works (res_users redirect to res_partner)
        # but when creating the mail.message to create the mail.compose.message
        # access rights issues may rise
        # We therefore directly change the model and res_id
        if result['model'] == 'res.users' and result['res_id'] == uid:
            result['model'] = 'res.partner'
            result['res_id'] = self.pool.get('res.users').browse(cr, uid, uid).partner_id.id

        if fields is not None:
            [result.pop(field, None) for field in result.keys() if field not in fields]
        
        if 'active_model' in context and context.get('active_model') == 'account.invoice':
            invoice = self.pool.get(context.get('active_model')).browse(cr, uid, context.get('active_ids'))
            
            if invoice.credit:
                doc_type = 'credit_note'
            elif invoice.debit:
                doc_type = 'debit_note'
            else:
                doc_type = invoice.type
                
            ruc = invoice.partner_id.ced_ruc
            number = invoice.number
            doc_type_name = DOC_TYPE_NAME[doc_type]
            
            dbname = cr.dbname
            company_ruc = invoice.company_id.partner_id.ced_ruc
    
            doc_xml_name = '/FE/%s/%s/Partner-%s/%s-%s-%s.xml' % (dbname, company_ruc, ruc, doc_type_name, ruc, number)
            doc_pdf_name = '/FE/%s/%s/Partner-%s/%s-%s-%s.pdf' % (dbname, company_ruc, ruc, doc_type_name, ruc, number)

            attchs = []
            
            try:
                f = open(doc_xml_name, 'r')
                xml_doc_content = f.read()
                base64_content = base64.b64encode(xml_doc_content)
                f.close()
                
                attachment_obj = self.pool.get('ir.attachment')
                attachment_xml_id = attachment_obj.create(cr, uid, {
                    'name': '%s-%s-%s.xml' % (doc_type_name, ruc, number),
                    'datas': base64_content,
                    'datas_fname': doc_xml_name,
                    'res_model': invoice._name,
                    'res_id': invoice.id,
                    'type': 'binary'
                })
                
                attchs.append(attachment_xml_id)
                
                f = open(doc_pdf_name, 'r')
                pdf_doc_content = f.read()
                base64_content = base64.b64encode(pdf_doc_content)
                f.close()
                
                attachment_pdf_id = attachment_obj.create(cr, uid, {
                    'name': '%s-%s-%s.pdf' % (doc_type_name, ruc, number),
                    'datas': base64_content,
                    'datas_fname': doc_pdf_name,
                    'res_model': invoice._name,
                    'res_id': invoice.id,
                    'type': 'binary'
                })
                
                attchs.append(attachment_pdf_id)
                result['attachment_ids'] = attchs
            except Exception as e:
                print('Error action_send_email: %s' % e)
        _logger.info('RESULT: %s' % result)
        return result

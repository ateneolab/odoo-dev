# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime


class email_trigger(models.Model):
    _name = 'email.send'

    @api.multi
    def create_send_mail(self, user):
        template_id = self.env.ref('birthday_mail_schedular.email_template_customer_form')
        email = user['work_email']
        # name = user['name']
        if template_id:
            template_id.write({
                'email_to': email,
                # 'record_name': name
            })

            company_id = user.company_id.id
            mail_server_id = self.env['ir.mail_server'].search([('company_id', '=', company_id)])

            message_id = False
            for server in mail_server_id:
                if not message_id:
                    try:
                        message_id = template_id.send_mail(user.id, force_send=True, server_id=server.id or False)
                    except Exception as e:
                        print (e)
                        message_id = False
        return True

    @api.model
    def email_trigger_action(self):
        today = datetime.datetime.now().date()  # .today().strftime('%Y-%m-%d')
        emp_data = self.env['hr.employee'].search([('id', '>', "0")])
        for val in emp_data:
            if val.birthday:
                birth_date = datetime.datetime.strptime(val.birthday, '%Y-%m-%d').date()
                if birth_date.month == today.month and birth_date.day == today.day:
                    self.create_send_mail(val)

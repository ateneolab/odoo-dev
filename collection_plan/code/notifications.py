# -*- coding: utf-8 -*-

from datetime import datetime

from openerp import models, api


class CollectionPlan(models.Model):
    _inherit = "collection_plan.collection_plan"

    @api.model
    def frozen_end(self):
        domain = [("state", "=", "frozen")]
        collections = self.search(domain)
        today = datetime.now().date()
        for record in collections:
            freezing = record.freezing_ids.sorted(
                key=lambda r: r.end_date, reverse=False
            )[-1]
            if freezing:
                day = datetime.strptime(freezing.end_date, "%Y-%m-%d").date() - today
                if day.days >= 20:
                    record.send_email()
        return True

    def send_email(self):
        template = self.env.ref("collection_plan.email_template_collections_form")
        user = self.user_id
        email = user["work_email"]
        if template:
            template.write({"email_to": email})
        company_id = user.company_id.id
        mail_server_id = self.env["ir.mail_server"].search(
            [("company_id", "=", company_id)]
        )
        for server in mail_server_id:
            template.send_mail(user.id, force_send=True, server_id=server.id or False)

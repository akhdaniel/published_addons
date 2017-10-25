from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class legal_document_type(models.Model):
    _name = 'dms.legal_document_type'

    name = fields.Char("Name")
    #template_automail = fields.Char('Template Automail')
    template_automail = fields.Many2one(comodel_name="mail.template", string="Template Automail", required=False, )
    rule_ids = fields.One2many(comodel_name="dms.legal_document_rule", inverse_name="document_type_id", string="Rules", required=False, )

class legal_document_rule(models.Model):
    _name = "dms.legal_document_rule"

    document_type_id        = fields.Many2one(comodel_name="dms.legal_document_type", string="Document Type", required=False, )
    level                   = fields.Integer(string="Level", required=False, )
    notification_start      = fields.Integer(string="Notification Start", required=False, help="Notification start (counted from document validity expired date)")
    notification_end        = fields.Integer(string="Notification End", required=False, help="Notification end (counted from document validity expired date)")

    receiver_ids            = fields.One2many(comodel_name="dms.rule_receiver", inverse_name="rule_id", string="Receivers", required=False, )

    def _get_to_users(self):
        for rec in self:
            rec.to_user_ids = [(4,1)]

    @api.depends("receiver_ids")
    def _get_cc_users(self):
        for rec in self:
            rec.cc_user_ids = [(4,1)]

    to_user_ids             = fields.Many2many(comodel_name="res.users",
                                               relation="to_rule_users",
                                               column1="role_id",
                                               column2="user_id", string="To Users",
                                               compute=_get_to_users,
                                               store=True)

    cc_user_ids             = fields.Many2many(comodel_name="res.users",
                                               relation="cc_rule_users",
                                               column1="role_id",
                                               column2="user_id", string="Cc Users",
                                               compute=_get_cc_users,
                                               store=True)


"""
level	
notification start (counted from document validity expired date )	
notification end (counted from document validity expired date)	
receiver to	
receiver cc
"""
class rule_receiver(models.Model):
    _name = 'dms.rule_receiver'
    rule_id         = fields.Many2one(comodel_name="dms.legal_document_rule", string="Rule", required=False, )
    role            = fields.Selection(string="To/ Cc", selection=[('to', 'To'), ('cc', 'Cc'), ], required=False, )
    group_id        = fields.Many2one(comodel_name="res.groups", string="Group", required=False, )


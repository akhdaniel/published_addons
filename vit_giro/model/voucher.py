from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
from openerp import netsvc

_logger = logging.getLogger(__name__)

####################################################################################
# periodic read dari ca_pembayaran
# if exists create payment voucher for the invoice
####################################################################################
class account_voucher(osv.osv):
    _name = "account.voucher"
    _inherit = "account.voucher"
    
    ####################################################################################
    # create payment
    # invoice_id: yang mau dibayar
    # journal_id: payment method
    ####################################################################################
    def create_payment(self, cr, uid, inv, partner_id, amount, journal, type, name, company_id, context=None):
        voucher_lines = []
        
        # cari move_line yang move_id nya = invoice.move_id
        move_line_id = self.pool.get('account.move.line').search(cr, uid, [('move_id.id', '=', inv.move_id.id)]);
        move_lines = self.pool.get('account.move.line').browse(cr, uid, move_line_id)
        move_line = move_lines[0]  # yang AR saja
        
        #payment supplier
        if type == 'payment':
            line_amount = amount
            line_type = 'dr'
            journal_account = journal.default_credit_account_id.id
        #receive customer
        else:
            line_amount = amount
            line_type = 'cr'
            journal_account = journal.default_debit_account_id.id
            
        
        voucher_lines.append((0, 0, {
            'move_line_id': move_line.id,
            'account_id': move_line.account_id.id,
            'amount_original': line_amount,
            'amount_unreconciled': line_amount,
            'reconcile': True,
            'amount': line_amount,
            'type': line_type,
            'name': move_line.name,
            'company_id': company_id
        }))
        
        voucher_id = self.pool.get('account.voucher').create(cr, uid, {
            'partner_id' : partner_id,
            'amount' 		: amount,
            'account_id'	: journal_account,
            'journal_id'	: journal.id,
            'reference' 	: 'Payment giro ' + name,
            'name' 			: 'Payment giro ' + name,
            'company_id' 	: company_id,
            'type'			: type,
            'line_ids'		: voucher_lines
        })
        _logger.info("   created payment id:%d" % (voucher_id) )
        return voucher_id
    
    ####################################################################################
    # set done
    ####################################################################################
    def payment_confirm(self, cr, uid, vid, context=None):
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'account.voucher', vid, 'proforma_voucher', cr)
        _logger.info("   confirmed payment id:%d" % (vid) )
        return True
    
    
    ####################################################################################
    # find invoice by number
    ####################################################################################
    def find_invoice_by_number(self, cr, uid, number, context=None):
        invoice_obj = self.pool.get('account.invoice')
        invoice_id = invoice_obj.search(cr, uid, [('number' ,'=', number)], context=context)
        invoice = invoice_obj.browse(cr, uid, invoice_id, context=context)
        return invoice
    
    ####################################################################################
    # find journal by code
    ####################################################################################
    def find_journal_by_code(self, cr, uid, code, context=None):
        journal_obj = self.pool.get('account.journal')
        journal_id = journal_obj.search(cr, uid, [('code', '=', code)], context=context)
        journal = journal_obj.browse(cr, uid, journal_id, context=context)
        return journal
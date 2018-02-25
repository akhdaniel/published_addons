from odoo import api, fields, models
import logging
import time
_logger = logging.getLogger(__name__)

class sale(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    def sale_auto_payment(self, order_lines=None, customer=None, journal_name=None):
        
        # create so
        _logger.info('create SO')
        partner = self.env['res.partner'].search([('name','=',customer)], limit=1)

        lines = []
        for l in order_lines:
            product = self.env['product.product'].search([('name','=', l['product'])], limit=1)
            lines.append((0,0,{'product_id': product.id, 'product_uom_qty': l['product_uom_qty']}))

        sale_data = {
            'partner_id': partner.id,
            'confirmation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'order_line': lines
        }
        so = self.env['sale.order'].create(sale_data)

        # confirm SO
        _logger.info('confirm SO')
        so.action_confirm()

        #validate delivery
        _logger.info('confirm Delivery')
        pickings = so.mapped('picking_ids')
        for picking in pickings:
            picking.do_transfer()


        # create invoice
        _logger.info('create Invoice')
        invoice_ids=so.action_invoice_create()

        # validate invoice
        _logger.info('validate Invoice')

        for inv in self.env['account.invoice'].browse(invoice_ids):
            inv.action_invoice_open()

            # paid invoice
            _logger.info('paid Invoice')

            journal=self.env['account.journal'].search([('name','=',journal_name)], limit=1)
            payment_method_id=self.env['account.payment.method'].search([('payment_type','=','inbound')],limit=1)
            payment = self.env['account.payment'].create({
                'partner_type':'customer',
                'partner_id':partner.id,
                'journal_id':journal.id ,
                'amount': inv.amount_total,
                'payment_method_id': payment_method_id.id, 
                'invoice_ids': [(4,inv.id)]
            })
            payment.post()

        _logger.info('Done!')

        return True 

import time
import datetime
from datetime import date, datetime, timedelta
from dateutil import relativedelta
from openerp.osv import fields, osv
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _
import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT


class contract(osv.osv):
	_inherit = "hr.contract"

	def cron_kontrak(self, cr, uid, ids=None,context=None):
		chat_obj        = self.pool.get('im_chat.message')
		conversation_obj= self.pool.get('im_chat.conversation_state')
		session_obj 	= self.pool.get('im_chat.session')

		date 			= fields.date.today()
		date_now 		= datetime.datetime.strptime(date,"%Y-%m-%d")

		lama_warning 		= datetime.timedelta(days=90)

		contract_expired = self.search(cr,uid,[()])
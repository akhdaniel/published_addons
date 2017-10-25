from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class legal(models.Model):
    _name = 'dms.legal'

    branch_id               = fields.Many2one(comodel_name='dms.legal_branch',string='Branch', required=True)
    jenis_dokumen_id        = fields.Many2one(comodel_name='dms.legal_document_type',string='Jenis Dokumen', required=True)

    name                    = fields.Char(string="Nomor", required=True, )
    tanggal_surat           = fields.Date(string="Tanggal", required=False, )
    alamat_surat            = fields.Char(string="Alamat", required=False, )

    masa_berlaku            = fields.Date(string="Masa Berlaku", required=False, )
    status                  = fields.Char(string="Status Dokumen", required=False, )
    keterangan              = fields.Char(string="Keterangan", required=False, )

    filename                = fields.Binary(string="File Name",  )

    def cron_cek_expired(self):
        """
        cek semua masa_berlaku document berdasarkan jenis_dokumen_id rule
        for each rule:
            jika today+rule.notification_start < masa_berlaku < today+rule.notification_end :
                send email to receivers 
        """

        for doc in self.search([]):
            if doc.masa_berlaku and doc.jenis_dokumen_id.rule_ids:
                for rule in doc.jenis_dokumen_id.rule_ids:
                    today = datetime.now()
                    masa_berlaku = datetime.strptime(doc.masa_berlaku, "%Y-%m-%d")
                    start = masa_berlaku + timedelta(days=rule.notification_start)
                    end = masa_berlaku + timedelta(days=rule.notification_end)

                    if start < today and today < end :
                        self.env['mail.template'].search([('name', '=', doc.jenis_dokumen_id.name)])[0].send_mail(rule.id, force_send=False)
                        print "*********** send %s, no=%s level=%s email to rule.receiver_ids" % \
                              (doc.jenis_dokumen_id.name, doc.name, rule.level)
        return


"""
Surat Konfirmasi Pindah Alamat
Alamat Kantor Surat Konfirmasi Pindah Alamat

Nomor SK Pembukaan / Surat Pencatatan
Tanggal SK Pembukaan / SK Pencatatan
Alamat SK Pembukaan

Nomor SK Pembukaan KC Usaha Syariah
Tanggal SK Pembukaan KC Usaha Syariah
Alamat SK Pembukaan KC Usaha Syariah

Nomor SKDP	Masa Berlaku SKDP
Status Dokumen SKDP
Rumus Keterangan SKDP
Alamat Dalam SKDP

Nomor SITU
Masa Berlaku SITU
Status Dokumen SITU
Keterangan SITU
Alamat Dalam SITU

Nomor WLTK
Masa Berlaku WLTK
Status Dokumen WLTK
Keterangan WLTK
Alamat Dalam WLTK

Nomor TDP
Masa Berlaku TDP
Status Dokumen TDP
Keterangan TDP
Alamat Dalam TDP

Nomor NPWP

Nomor HO
Masa Berlaku HO
Status Dokumen HO
Keterangan HO
Alamat Dalam HO

Nomor Izin Reklame
Masa Berlaku Ijin Reklame
Status Dokumen Ijin Reklame
Keterangan Ijin Reklame
Alamat Dalam Ijin Reklame

Nomor Akta Sewa
Akhir Masa Sewa
Keterangan Sewa

"""




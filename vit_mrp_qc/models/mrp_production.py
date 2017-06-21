# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 vitraining
# based on Deltatech addons
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import odoo.addons.decimal_precision as dp

from odoo import api
from odoo import models, fields


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi 
    def button_mark_done(self):
        """
        create stock.picking from Input to Stock
        if the production.location_dest_id == Input
        """
        input_location = self.env.ref('stock.stock_location_company', raise_if_not_found=True)
        import pdb; pdb.set_trace()
        if self.location_dest_id == input_location:
            move_list = []
            picking_type = self.env.ref('stock.picking_type_qc', raise_if_not_found=True)

            for move in self.move_finished_ids:
                move_list.append((0,0,{
                    'location_id' : picking_type.default_location_src_id.id,
                    'location_dest_id' : picking_type.default_location_dest_id.id,
                    'product_id' : move.product_id.id,
                    'product_uom_qty': move.product_uom_qty,
                    'product_uom': move.product_uom.id,
                    'name'  : move.name,
                    'date'  : move.date,
                    'origin' : move.origin,
                    'group_id': move.group_id.id
                }))

            if move_list:
                if picking_type:
                    picking = self.env['stock.picking'].create({'picking_type_id': picking_type.id,
                                                                'date': self.date_planned_start,
                                                                'location_id':picking_type.default_location_src_id.id,
                                                                'location_dest_id':picking_type.default_location_dest_id.id,
                                                                'move_lines' : move_list,
                                                                'origin': self.name})
                    picking.action_confirm()

        return super(MrpProduction, self).button_mark_done()
        

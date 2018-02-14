import simplejson
from odoo import  http
from odoo.http import request


class BaseWebsite(http.Controller):

    @http.route('/selectize/countries', type='http', auth="public", website=True)
    def countries(self, **kw):
        res = request.env['res.country'].search([('name','ilike',kw.get('q'))])
        countries = [{'id': str(r.id), 'name': r.name} for r in res]
        return simplejson.dumps(countries)

    @http.route('/selectize/states/<int:country_id>', type='http', auth="public", website=True)
    def states(self, country_id=None, **kw):
        res = request.env['res.country.state'].search([('country_id.id','=',country_id)])
        states = [{'id': str(r.id), 'name': r.name} for r in res]
        return simplejson.dumps(states)

    @http.route('/selectize/cities/<int:state_id>', type='http', auth="public", website=True)
    def cities(self, state_id=None, **kw):
        res = request.env['vit.kota'].search([('state_id','=',state_id)])
        cities = [{'id': str(r.id), 'name': r.name} for r in res]
        return simplejson.dumps(cities)

    @http.route('/selectize/kecamatans/<int:city_id>', type='http', auth="public", website=True)
    def kecamatans(self, city_id=None, **kw):
        res = request.env['vit.kecamatan'].search([('kota_id','=',city_id)])
        kecamatans = [{'id': str(r.id), 'name': r.name} for r in res]
        return simplejson.dumps(kecamatans)

    @http.route('/selectize/kelurahans/<int:kecamatan_id>', type='http', auth="public", website=True)
    def kelurahan(self, kecamatan_id=None, **kw):
        res = request.env['vit.kelurahan'].search([('kecamatan_id','=',kecamatan_id)])
        kelurahans = [{'id': str(r.id), 'name': r.name} for r in res]
        return simplejson.dumps(kelurahans)

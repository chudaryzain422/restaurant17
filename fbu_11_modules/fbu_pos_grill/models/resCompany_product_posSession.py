from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    arabic_name = fields.Char(string='Arabic Name')

class ResCompany(models.Model):
    _inherit = 'res.company'

    receipt_footer = fields.Text(string='Receipt Footer')
    grill_receipt_footer = fields.Text(string='Grill Receipt Footer')
    company_short_code = fields.Char(string='Company Short Code')

# Extend the session load with custom fields
class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].append('arabic_name')
        result['search_params']['fields'].append('grill_service')
        result['search_params']['fields'].append('consumable_bom')
        result['search_params']['fields'].append('ready_to_eat')
        result['search_params']['fields'].append('breakfast')
        result['search_params']['fields'].append('pos_grill_method_id')
        return result

    def _loader_params_res_company(self):
        result = super()._loader_params_res_company()
        result['search_params']['fields'].extend([
            'receipt_footer',
            'grill_receipt_footer',
            'company_short_code'
        ])
        return result

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.http import request
import json
import requests
from requests.auth import HTTPBasicAuth


class ProductProductInherit(models.Model):
    _inherit = "product.product"

    def action_import_products(self):

        url = "https://sams4sed.sam.ae:50201/sap/opu/odata/SAP/ZSH_MATNR_SRV/MATNR_SHSet?$filter=Werks eq '2100'&sap-client=130&$format=json"

        auth = HTTPBasicAuth('MISERVICE', 'welcome123')
        response = requests.get(url, auth=auth)
        if response.status_code == 200:
            materials_data = response.json()
            materials_list = materials_data.get('d', {}).get('results', [])
            count = 0
            for material in materials_list:
                default_code = material.get('Matnr')
                name = material.get('Maktg')
                spras = material.get('Spras')

                # Create or update the product in Odoo
                product = self.env['product.product'].search([('default_code', '=', default_code)], limit=1)
                if not product:
                    product = self.env['product.product'].create({
                        'default_code': default_code,
                        'name': name,
                        'description': f"{name} ({spras})",
                    })
                    print(product.name)
                    count +=1
                    if count % 5 == 0:
                        self.env.cr.commit()
        else:
            raise Exception("Failed to fetch materials")






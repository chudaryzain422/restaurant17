# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.http import request
import json
import requests
from requests.auth import HTTPBasicAuth
from odoo.exceptions import UserError, ValidationError

class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    sap_order_id = fields.Char()

    # def button_confirm(self):
    #     # token, cookies = self.get_auth_token()
    #     # cookies = cookies.get_dict()
    #     # session_id = cookies.get('SAP_SESSIONID_SED_130')
    #
    #     # po_status = self.get_sap_po_status(self.sap_order_id)
    #     # print(po_status)
    #
    #     # matrials_groups = self.get_sap_material_groups()
    #     # print(matrials_groups)
    #
    #     # sap_uoms = self.get_sap_uoms()
    #     # for sap_uom in sap_uoms:
    #     #     # uom_category = self.env['uom.category'].search([('name', '=', sap_uom.get('Txdim'))], limit=1)
    #     #     # if not uom_category:
    #     #     uom_category = self.env['uom.category'].create({
    #     #         'name': sap_uom.get('Txdim'),
    #     #     })
    #     #     uom_unit = self.env['uom.uom'].search([('name', '=', sap_uom.get('Msehi'))], limit=1)
    #     #     if not uom_unit:
    #     #         uom_unit = self.env['uom.uom'].create({
    #     #             'name': sap_uom.get('Msehi'),
    #     #             'category_id': uom_category.id,
    #     #             'factor_inv': 1.0,  # For reference unit
    #     #             'uom_type': 'reference',
    #     #             'rounding': 0.01,
    #     #             'active': True,
    #     #         })
    #     #         print(uom_unit.name)
    #
    #     # sap_cost_centers = self.get_sap_cost_centers()
    #     # print(sap_cost_centers)
    #
    #
    #     # url = "https://app.sam.ae:4432/api/CreatePO"
    #     url = "https://sams4sed.sam.ae:50201/sap/opu/odata/SAP/API_PURCHASEORDER_PROCESS_SRV/A_PurchaseOrder?sap-client=130"
    #
    #     # headers = {
    #     #     'Content-Type': 'application/json',
    #     #     # 'x-csrf-token': token,
    #     #     'x-csrf-token': '4U_SYHMxDMZob_tFSpkOhA==',
    #     #     'X-AppApiKey': "41guCToSR3:0T0VSM38OHhH0A3XuIK52v7oUzgxMzYM",
    #     #     'Authorization': 'Basic ' + 'VENDORPORTAL:Vendor@12345'.encode('ascii').decode('utf-8'),
    #     #     'Accept': 'application/json',
    #     #     # "SessionID": session_id
    #     # }
    #     headers = {
    #         'Content-Type': 'application/json',
    #         'Authorization': 'audio/basic',
    #         'x-csrf-token': '4U_SYHMxDMZob_tFSpkOhA==',
    #         'Cookie': 'MYSAPSSO2=AjQxMDMBABhWAEUATgBEAE8AUgBQAE8AUgBUAEEATAACAAYxADMAMAADABBTAEUARAAgACAAIAAgACAABAAYMgAwADIANAAxADIAMQAwADAANwAwADIABQAEAAAACAYAAlgACQACRQD%2fAPwwgfkGCSqGSIb3DQEHAqCB6zCB6AIBATELMAkGBSsOAwIaBQAwCwYJKoZIhvcNAQcBMYHIMIHFAgEBMBowDjEMMAoGA1UEAxMDU0VEAggKIBcCIRECATAJBgUrDgMCGgUAoF0wGAYJKoZIhvcNAQkDMQsGCSqGSIb3DQEHATAcBgkqhkiG9w0BCQUxDxcNMjQxMjEwMDcwMjA4WjAjBgkqhkiG9w0BCQQxFgQUSyl2bIqY8wgnTSeOnQGljAYXdtkwCQYHKoZIzjgEAwQvMC0CFDwKp4sROUBgNQBWzh43UhtKtdVaAhUAhohRCGgy08PteKwsgHAmfu%218Nyc%3d; SAP_SESSIONID_SED_130=fjH729Ghk1egRbJsOaxeHKwnete2xBHvoWFvP2e7MuI%3d; SPNegoTokenRequested=2024-12-10%2006%3a52%3a54; sap-usercontext=sap-language=EN&sap-client=130',
    #         'Accept': 'application/json',
    #     }
    #
    #     # Dynamic data extraction from purchase order and purchase order lines
    #     items = []
    #     count = 1
    #     for line in self.order_line:
    #         item = {
    #             "PurchaseOrder": "",
    #             "PurchaseOrderItem": str(count),
    #             "PurchaseOrderItemText": line.name,
    #             "Plant": "1100",
    #             "StorageLocation": "SM01",
    #             "MaterialGroup": "SA16",
    #             "OrderQuantity": str(line.product_qty),
    #             "OrderPriceUnit": 'PCS',
    #             "DocumentCurrency": self.currency_id.name,
    #             "NetPriceAmount": str(line.price_unit),
    #             "NetPriceQuantity": "1",
    #             "PurchaseOrderItemCategory": "0",
    #             "AccountAssignmentCategory": "K",
    #             "Material": line.product_id.default_code,
    #             "to_AccountAssignment": [
    #                 {
    #                     "PurchaseOrder": "",
    #                     "PurchaseOrderItem": str(count),
    #                     "AccountAssignmentNumber": "1",
    #                     "Quantity": str(line.product_qty),
    #                     "GLAccount": "5032103",
    #                     "CostCenter": "11000534"
    #                 }
    #             ]
    #         }
    #         items.append(item)
    #         count +=1
    #
    #     payload = {
    #         "PurchaseOrder": "",
    #         "CompanyCode": '1100',
    #         "PurchaseOrderType": "ZSTD",
    #         "Supplier": self.partner_id.supplier_code or '2016',
    #         "PurchasingOrganization": "1100",
    #         "PurchasingGroup": "110",
    #         "PurchaseOrderDate": f"/Date({int(self.date_order.timestamp() * 1000)})/",
    #         "DocumentCurrency": self.currency_id.name,
    #         "to_PurchaseOrderItem": items
    #     }
    #
    #     response = requests.post(url, headers=headers,data=json.dumps(payload))
    #
    #     if response.status_code == 200 or  response.status_code == 201:
    #         purchasOrder_response = response.json()
    #         sap_order = purchasOrder_response.get('d')
    #         self.name = sap_order.get('PurchaseOrder')
    #         print("order created in sap with no %s" % sap_order.get('PurchaseOrder'))
    #         message = f"Order create in SAP with order id {self.name}."
    #         self.message_post(body=message, subtype_xmlid="mail.mt_note")
    #     else:
    #         raise UserError(f"Failed to create purchase order: {response.text}")
    #
    #     res = super(PurchaseOrderInherit, self).button_confirm()
    #     return res


    def get_auth_token(self):
        url = "https://sams4sed.sam.ae:50201/sap/opu/odata/SAP/USERDEFAULTS?sap-client=130&$format=json&sap-language=EN"
        headers = {
                'x-csrf-token': 'fetch'
            }
        auth = HTTPBasicAuth('VENDORPORTAL', 'Vendor@12345')

        response = requests.get(url, headers=headers, auth=auth)
        if response.status_code == 200:
            token = response.headers.get('x-csrf-token')
            cookies = response.cookies
            return token, cookies
        else:
            raise Exception("Failed to fetch CSRF token")


    def get_sap_po_status(self,order_id):
        url = "https://sams4sed.sam.ae:50201/sap/opu/odata/SAP/API_PURCHASEORDER_PROCESS_SRV/A_PurchaseOrder('{}')/to_PurchaseOrderItem?sap-client=130".format(order_id)
        headers = {
            'Accept': 'application/json'
        }
        auth = HTTPBasicAuth('MISERVICE', 'welcome123')
        response = requests.get(url, auth=auth,headers=headers)
        if response.status_code == 200:
            po_data = response.json()
            sap_order = po_data.get('d', {}).get('results', [])
            print(sap_order)
        else:
            raise Exception("Order Not Found!")

    def get_sap_material_groups(self):

        url = "https://sams4sed.sam.ae:50201/sap/opu/odata/SAP/ZSH_MAT_GRP_SRV/MAT_GRP_SHSet?sap-client=130?&$format=json"

        auth = HTTPBasicAuth('MISERVICE', 'welcome123')
        response = requests.get(url, auth=auth)
        if response.status_code == 200:
            materials_group_data = response.json()
            material_group_list = materials_group_data.get('d', {}).get('results', [])
            return material_group_list
        else:
            raise Exception("Failed to fetch material groups")

    def get_sap_uoms(self):

        url = "https://sams4sed.sam.ae:50201/sap/opu/odata/SAP/ZSH_UOM_SRV/MOU_SHSet?sap-client=130?&$format=json&sap-language=EN"

        auth = HTTPBasicAuth('MISERVICE', 'welcome123')
        response = requests.get(url, auth=auth)
        if response.status_code == 200:
            uoms_data = response.json()
            uoms_list = uoms_data.get('d', {}).get('results', [])
            return uoms_list
        else:
            raise Exception("Failed to fetch uom")

    def get_sap_cost_centers(self):

        url = "https://sams4sed.sam.ae:50201/sap/opu/odata/SAP/ZSH_STORAGE_LOC_SRV/STORAGE_LOC_SHSet?$filter=Werks eq '2100'&sap-client=130&$format=json&sap-language=EN"
        auth = HTTPBasicAuth('MISERVICE', 'welcome123')
        response = requests.get(url, auth=auth)
        if response.status_code == 200:
            cost_center_data = response.json()
            cost_center_list = cost_center_data.get('d', {}).get('results', [])
            return cost_center_list
        else:
            raise Exception("Failed to fetch uom")


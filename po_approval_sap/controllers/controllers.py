from odoo import http
from odoo.http import request
import json
import base64
from werkzeug.exceptions import Unauthorized

class VendorAPIController(http.Controller):

    @http.route('/create_vendor', type='json', auth='none', methods=['POST'], csrf=False)
    def create_vendor(self, **kwargs):
        # Basic Authentication
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header:
            return {'status': 'error', 'message': 'Missing authentication header'}

        auth_type, credentials = auth_header.split(' ', 1)
        if auth_type.lower() != 'basic':
            return {'status': 'error', 'message': 'Invalid authentication type'}

        credentials = base64.b64decode(credentials).decode('utf-8')
        username, password = credentials.split(':', 1)

        # Authenticate user
        user = request.env['res.users'].sudo().search([('login', '=', username)], limit=1)
        if not user or not user.authenticate(request.db,username,password,user_agent_env=None):
            return {'status': 'error', 'message': 'Invalid credentials'}

        # Extract vendor data from the request
        if request.httprequest:
            All_data = request.httprequest.json
            sap_data = json.loads(All_data.get('DataFromSAP')).get('d')
            sam_data = All_data.get('DataFromVendorRegistration')
            sam_documents = All_data.get('documents')
            if sap_data and sam_data:
                supplier_code = sap_data.get('BusinessPartner')
                partner = request.env['res.partner'].sudo().search([('supplier_code', '=', supplier_code)], limit=1)
                if partner:  # If the vendor does not already exist
                    return {'status': 'Success', 'message': 'Supplier Already Exists with same supplier code'}
                country = request.env['res.country'].sudo().search([('code', '=',sam_data.get('CountryRegion'))],limit=1)
                state = request.env['res.country.state'].sudo().search([('name','=', sam_data.get('CityText').capitalize())],limit=1)
                industry = request.env['res.partner.industry'].sudo().search([('name','=', sam_data.get('ProcurementCategory'))],limit=1)
                if not industry:
                    industry = request.env['res.partner.industry'].sudo().create({
                        'name':sam_data.get('ProcurementCategory')
                    })
                # payment_term = request.env['account.payment.term'].sudo().search([('name','=', sam_data.get('PaymentTerms'))],limit=1)
                # if not payment_term:
                #     payment_term = request.env['account.payment.term'].sudo().create({
                #         'name':  sam_data.get('PaymentTerms')
                #     })
                new_vendor_data = {
                    'name': sam_data.get('Name'),  # Adjust according to actual response field
                    'supplier_code': supplier_code,
                    'email': sam_data.get('Email'),
                    'phone': sam_data.get('PrimaryContactNumber'),
                    'mobile': sam_data.get('SecondaryContactNumber'),
                    'vat': sam_data.get('VATTRN'),
                    'country_id': country.id if country else False,
                    'state_id': state.id if state else False,
                    'city':sam_data.get('CityText'),
                    'street':sam_data.get('Street'),
                    'street2': sam_data.get('StreetNo'),
                    'zip': sam_data.get('ZipCode'),
                    'website': sam_data.get('InternetAddress'),
                    'license_no': sam_data.get('TradeLicense'),
                    'industry_id': industry.id if industry else False,
                    'company_types': sam_data.get('OrganizationSector'),
                    'supplier_rank': 1,
                }
                try:
                    new_vendor = request.env['res.partner'].sudo().create(new_vendor_data)
                    attachment_ids = []
                    if new_vendor and sam_documents:
                        for doc in sam_documents:
                            attachment_data = {
                                'name': doc.get('FileName'),
                                'type': 'binary',
                                'datas': base64.b64decode(doc.get('Files')),
                                'res_model': 'res.partner',
                                'res_id': new_vendor.id,
                                'mimetype': 'image/jpeg',
                            }
                            attachment = request.env['ir.attachment'].sudo().create(attachment_data)
                            attachment_ids.append(attachment.id)
                    new_vendor.activity_ids.attachment_ids = [(4, attachment_id) for attachment_id in attachment_ids]
                    print(new_vendor.id)
                    print(new_vendor.name)
                    self._create_or_update_bank_details(new_vendor,sam_data)
                    return {'status': 'success', 'vendor_id': new_vendor.id}
                except Exception as e:
                    return {'status': 'error', 'message': str(e)}
        else:
            return {'status': 'error', 'message': 'No JSON data found in request'}

    def _create_or_update_bank_details(self, partner, bank_data):
        if bank_data:
            bank_account = bank_data.get('BankAccount')
            bank_name = bank_data.get('BankName')
            bank_account_holder_name = bank_data.get('OwnerName')
            iban = bank_data.get('IBAN')
            swift_code = bank_data.get('BankKey')
            bank_country = bank_data.get('BankCountry')
            country = request.env['res.country'].sudo().search([('code', '=',bank_country)],limit=1)
            bank_record = request.env['res.bank'].sudo().search([('name', '=', bank_name)], limit=1)
            if not bank_record:
                bank_record = request.env['res.bank'].sudo().create({'name': bank_name, 'bic': swift_code, 'country': country.id if country else False})

            # Create or update the bank account record for the partner
            existing_bank_account = request.env['res.partner.bank'].sudo().search([('acc_number', '=', bank_account), ('partner_id', '=', partner.id)], limit=1)
            bank_vals = {
                'acc_number': bank_account,
                'acc_holder_name': bank_account_holder_name,
                'partner_id': partner.id,
                'bank_id': bank_record.id,
                'partner_bank_iban': iban,
            }

            if existing_bank_account:
                existing_bank_account.write(bank_vals)
            else:
                request.env['res.partner.bank'].sudo().create(bank_vals)

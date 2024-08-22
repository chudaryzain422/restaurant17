from odoo import api, fields, models, _
from odoo.http import request
import json
import requests
from requests.auth import HTTPBasicAuth
from odoo.exceptions import UserError


class ResPartnerBankInherit(models.Model):
    _inherit = "res.partner.bank"

    partner_bank_iban = fields.Char(string='IBAN', help='Bank iban')

class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    supplier_code = fields.Char('SAP PartnerId')
    sap_user = fields.Boolean(default=False)
    company_types = fields.Selection([('EducationSector', 'Education Sector'), ('GovernmentSector', 'Government Sector'), ('PrivateSector', 'Private Sector'), ('SemiGovernmetSector', 'Semi-Government Sector')])
    license_no = fields.Char()


    def _create_or_update_bank_details(self, partner, bank_data):
        if bank_data:
            bank_account = bank_data.get('BankAccount')
            bank_name = bank_data.get('BankName')
            bank_account_holder_name = bank_data.get('BankAccountHolderName')
            iban = bank_data.get('IBAN')
            swift_code = bank_data.get('SWIFTCode')
            bank_country = bank_data.get('BankCountryKey')
            country = self.env['res.country'].search([('code', '=',bank_country)],limit=1)
            bank_record = self.env['res.bank'].search([('name', '=', bank_name)], limit=1)
            if not bank_record:
                bank_record = self.env['res.bank'].create({'name': bank_name, 'bic': swift_code, 'country': country.id if country else False})

            # Create or update the bank account record for the partner
            existing_bank_account = self.env['res.partner.bank'].search([('acc_number', '=', bank_account), ('partner_id', '=', partner.id)], limit=1)
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
                self.env['res.partner.bank'].create(bank_vals)


    def action_import_vendors(self):
        url = "https://sams4sed.sam.ae:50201/sap/opu/odata/SAP/API_BUSINESS_PARTNER/A_SupplierCompany?$filter=CompanyCode eq '2100'"
        auth = HTTPBasicAuth('MISERVICE', 'welcome123')
        headers = {
            'Accept': 'application/json'
        }

        response = requests.get(url, auth=auth, headers=headers)
        if response.status_code == 200:
            vendors_data = response.json()
            vendors_list = vendors_data.get('d', {}).get('results', [])
            count = 0  # Initialize the counter

            for vendor in vendors_list:
                new_url = "https://sams4sed.sam.ae:50201/sap/opu/odata/sap/API_BUSINESS_PARTNER/A_BusinessPartner('{}')?$expand=to_BusinessPartnerAddress/to_EmailAddress,to_BusinessPartnerAddress/to_FaxNumber,to_BusinessPartnerAddress/to_MobilePhoneNumber,to_BusinessPartnerAddress/to_PhoneNumber,to_BusinessPartnerAddress/to_URLAddress,to_BusinessPartnerBank,to_Supplier/to_SupplierPurchasingOrg".format(vendor.get('Supplier'))
                response = requests.get(new_url, auth=auth, headers=headers)
                if response.status_code == 200:
                    vendor_data = response.json()
                    vendor_detail = vendor_data.get('d', {})
                    if vendor_detail:
                        email = ''
                        phone = ''
                        mobile = ''
                        address_data = vendor_detail.get('to_BusinessPartnerAddress', {}).get('results', [])[0]
                        bank_data = vendor_detail.get('to_BusinessPartnerBank', {}).get('results', [])
                        if bank_data:
                            bank_data = bank_data[0]
                        if address_data and address_data.get('to_EmailAddress') and len(address_data.get('to_EmailAddress').get('results')):
                            email = address_data.get('to_EmailAddress').get('results')[0].get('EmailAddress')
                        if address_data and address_data.get('to_MobilePhoneNumber') and len(address_data.get('to_MobilePhoneNumber').get('results')):
                            phone = address_data.get('to_MobilePhoneNumber').get('results')[0].get('PhoneNumber')
                            mobile = address_data.get('to_MobilePhoneNumber').get('results')[0].get('InternationalPhoneNumber')

                        supplier_code = vendor_detail.get('Supplier')
                        partner = self.env['res.partner'].search([('supplier_code', '=', supplier_code)], limit=1)
                        if not partner:  # If the vendor does not already exist
                            country = self.env['res.country'].search([('code', '=',address_data.get('Country'))],limit=1)
                            new_vendor = self.env['res.partner'].create({
                                'name': vendor_detail.get('BusinessPartnerFullName'),  # Adjust according to actual response field
                                'supplier_code': supplier_code,
                                'email': email,
                                'phone': phone,
                                'mobile': mobile,
                                'vat': address_data.get('AddressIDByExternalSystem') if address_data else False,
                                'country_id': country.id if country else False,
                                'city':address_data.get('CityName'),
                                'street':address_data.get('AdditionalStreetPrefixName'),
                                'zip':address_data.get('POBoxPostalCode'),
                                'supplier_rank': 1,
                            })
                            self._create_or_update_bank_details(new_vendor,bank_data)
                            print(new_vendor.name)
                            count += 1  # Increment the counter
                            if count % 20 == 0:
                                self.env.cr.commit()  # Commit the transaction every 20 new vendors
        else:
            raise UserError("Failed to fetch vendors. Status Code: %s, Response: %s" % (response.status_code, response.text))

    def action_create_vendors_sap(self):
        for record in self:
            if not record.bank_ids:
                raise UserError('please update bank details to create supplier in SAP')
            token, cookies = self.env['purchase.order'].get_auth_token()
            url = "https://sams4sed.sam.ae:50201/sap/opu/odata/sap/API_BUSINESS_PARTNER/A_BusinessPartner"

            headers = {
                'Content-Type': 'application/json',
                'x-csrf-token': token,
                'Authorization': 'Basic ' + 'MISERVICE:welcome123'.encode('ascii').decode('utf-8'),
                'Accept': 'application/json',
            }
            payload = self.generate_vendor_payload(record)
            response = requests.request("POST", url, headers=headers,cookies=cookies, data=payload)
            if response.status_code == 201:
                sap_data = response.json()
                if sap_data and sap_data.get('d'):
                    record.supplier_code = sap_data.get('d').get('BusinessPartner')
                    record.sap_user = True
            else:
                response = response.json()
                raise UserError(response.get('error').get('message').get('value'))
            print(response.text)




    def generate_vendor_payload(self, record):
        payload = {
            "BusinessPartnerCategory": "2",
            "BusinessPartnerGrouping": "SUPL",
            "CorrespondenceLanguage": "EN",
            "FirstName": record.name,
            "FormOfAddress": "0003",
            "Language": "EN",
            "LastName": "",
            "OrganizationBPName1": record.name,
            "OrganizationBPName2": "",
            "SearchTerm1": record.name,
            "SearchTerm2": record.name,
            "to_BusinessPartnerAddress": {
                "results": [
                    {
                        "ValidityStartDate": "/Date(1721840556000)/",
                        "ValidityEndDate": "/Date(1735578139000)/",
                        "AdditionalStreetPrefixName": record.street or record.street2 or '',
                        "AdditionalStreetSuffixName": record.street or record.street2 or '',
                        "AddressTimeZone": "UTC+3",
                        "CityCode": "AD", #SHJ
                        "CityName": record.city or '',
                        "CompanyPostalCode": record.zip or "",
                        "Country": record.country_id.code or "AE",
                        "District": "AD",#SHJ
                        "HouseNumber": "85",
                        "HouseNumberSupplementText": '',
                        "Language": "EN",
                        "POBox": record.zip or "",
                        "Region": "AD",#SHJ
                        "StreetName": record.street or record.street2 or '',
                        "StreetPrefixName": record.street or record.street2 or '',
                        "StreetSuffixName": "",
                        "AddressIDByExternalSystem": record.vat or "",
                        "to_EmailAddress": {
                            "results": [
                                {
                                    "OrdinalNumber": "1",
                                    "IsDefaultEmailAddress": True,
                                    "EmailAddress": record.email or ''
                                },
                                {
                                    "OrdinalNumber": "2",
                                    "IsDefaultEmailAddress": False,
                                    "EmailAddress": record.email or ''
                                }
                            ]
                        },
                        "to_MobilePhoneNumber": {
                            "results": [
                                {
                                    "OrdinalNumber": "1",
                                    "DestinationLocationCountry": record.country_id.code or "AE",
                                    "IsDefaultPhoneNumber": True,
                                    "PhoneNumber": record.phone or '',
                                    "InternationalPhoneNumber": record.phone or '',
                                    "PhoneNumberType": "3",
                                    "AddressCommunicationRemarkText": "Contact Person Primary Contact"
                                },
                                {
                                    "OrdinalNumber": "2",
                                    "DestinationLocationCountry": record.country_id.code or "AE",
                                    "IsDefaultPhoneNumber": False,
                                    "PhoneNumber": record.phone or '',
                                    "InternationalPhoneNumber": record.phone or '',
                                    "PhoneNumberType": "3",
                                    "AddressCommunicationRemarkText": "Contact Person Secondary Contact"
                                }
                            ]
                        },
                        "to_PhoneNumber": {
                            "results": [
                                {
                                    "OrdinalNumber": "1",
                                    "DestinationLocationCountry": record.country_id.code or "AE",
                                    "IsDefaultPhoneNumber": True,
                                    "PhoneNumber": record.phone or '',
                                    "PhoneNumberExtension": "1234",
                                    "InternationalPhoneNumber": record.phone or '',
                                    "PhoneNumberType": "1"
                                }
                            ]
                        },
                        "to_URLAddress": {
                            "results": [
                                {
                                    "OrdinalNumber": "1",
                                    "ValidityStartDate": "/Date(1721840649000)/",
                                    "IsDefaultURLAddress": True,
                                    "SearchURLAddress": record.website or '',
                                    "WebsiteURL": record.website or ''
                                }
                            ]
                        }
                    }
                ]
            },
            "to_BusinessPartnerBank": {
                "results": [
                    {
                        "BankIdentification": "0001",
                        "BankCountryKey": record.bank_ids[0].bank_id.country.code if record.bank_ids else 'AE',
                        "BankNumber": record.bank_ids[0].bank_id.bic if record.bank_ids else '',
                        "BankAccountHolderName": record.bank_ids[0].acc_holder_name if record.bank_ids else '',
                        "BankAccountName": record.bank_ids[0].partner_id.name if record.bank_ids else '',
                        "ValidityStartDate": "/Date(1721840649000)/",
                        "ValidityEndDate": "/Date(1735578139000)/",
                        "IBAN": record.bank_ids[0].partner_bank_iban if record.bank_ids else '',
                        "IBANValidityStartDate": "/Date(1721840649000)/",
                        "BankAccount": record.bank_ids[0].acc_number if record.bank_ids else ''
                    }
                ]
            },
            "to_BusinessPartnerRole": {
                "results": [
                    {
                        "BusinessPartnerRole": "FLVN00",
                        "ValidFrom": "/Date(1721840736000)/",
                        "ValidTo": "/Date(1735578139000)/",
                        "AuthorizationGroup": ""
                    },
                    {
                        "BusinessPartnerRole": "FLVN01",
                        "ValidFrom": "/Date(1721840736000)/",
                        "ValidTo": "/Date(1735578139000)/",
                        "AuthorizationGroup": ""
                    },
                    {
                        "BusinessPartnerRole": "ZFLVNX",
                        "ValidFrom": "/Date(1721840736000)/",
                        "ValidTo": "/Date(1735578139000)/",
                        "AuthorizationGroup": ""
                    }
                ]
            },
            "to_Supplier": {
                "SupplierAccountGroup": "SUPL",
                "VATRegistration": "100065728123456",
                "to_SupplierCompany": {
                    "results": [
                        {
                            "CompanyCode": "2100",
                            "PaymentMethodsList": "C",
                            "PaymentTerms": "S004",
                            "CheckPaidDurationInDays": "0",
                            "Currency": record.property_purchase_currency_id.name or "AED",
                            "ReconciliationAccount": "2011101",
                            "LayoutSortingRule": "001",
                            "IsToBeCheckedForDuplicates": True,
                            "SupplierAccountGroup": "SUPL"
                        }
                    ]
                },
                "to_SupplierPurchasingOrg": {
                    "results": [
                        {
                            "PurchasingOrganization": "2100",
                            "CalculationSchemaGroupCode": "SA",
                            "IncotermsClassification": "FOB",
                            "IncotermsLocation1": "SAMH, Sharjah",
                            "InvoiceIsGoodsReceiptBased": True,
                            "PaymentTerms": "S004",
                            "PurchaseOrderCurrency": record.property_purchase_currency_id.name or "AED",
                            "SupplierPhoneNumber": "0502322358",
                            "SupplierRespSalesPersonName": record.buyer_id.name or "",
                            "to_PartnerFunction": {
                                "results": [
                                    {
                                        "PurchasingOrganization": "2100",
                                        "Plant": "2100",
                                        "PartnerFunction": "VN",
                                        "DefaultPartner": True
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }
        return json.dumps(payload)

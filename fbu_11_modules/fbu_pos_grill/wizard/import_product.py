import base64
import binascii
import logging
import tempfile

import xlrd

from odoo import models, api, fields, _
_logger = logging.getLogger(__name__)

class ImportProduct(models.TransientModel):
    _name = "souq.product.import"

    xlsx_file = fields.Binary(string="Excel files")


    def import_product(self):
        result = {}
        print("CALING")
        _logger.info("IMOPRT FILE CALLIMG")
        if self.xlsx_file:
            try:

                file_data = base64.b64decode(self.xlsx_file)
                print("CALID FILE FATA")
                _logger.info("FILE READ PROPERLY")

                workbook = xlrd.open_workbook(file_contents=file_data)
                sheet = workbook.sheet_by_index(0)
                sheet.cell_value(0, 0)

                for i in range(sheet.nrows):
                    _logger.info("FILE REad with sheets")
                    if not i <= 0:
                        row = sheet.row_slice(i)
                        print(row)
                        company = row[0].value
                        product = row[1].value
                        sale_price = row[2].value
                        pos_cate = row[3].value
                        parent_pos_cate = row[4].value
                        is_grill_qty = row[5].value
                        type = row[6].value
                        g_qty = row[7].value
                        g_price = row[8].value
                        g_categ = row[9].value
                        g_parent_categ = row[10].value
                        company_id = self.env['res.company'].sudo().search([("name", "=", company)])
                        print("COMPAN"+str(company_id))
                        parent_pos_cate_rec = self.env['pos.category'].sudo().search(
                            [("name", "=",parent_pos_cate)])
                        pos_cate_rec = self.env['pos.category'].sudo().search(
                            [("name", "=", pos_cate), ("parent_id", "=", parent_pos_cate_rec.id)])
                        if not pos_cate_rec:
                            pos_cate_rec = self.env['pos.category'].sudo().create({"name": pos_cate,
                                                                                   "parent_id": parent_pos_cate_rec.id})
                        general_cate_rec = self.env['product.category'].sudo().search([("name", "=", g_categ),
                                                                                       ("parent_id.name", "=",
                                                                                        g_parent_categ)])
                        if not general_cate_rec:
                            general_cate_rec = self.env['product.category'].sudo().create({"name": g_categ
                                                                                           })
                        product_rec = self.env['product.template'].sudo().search(
                            [("name", "=", product), ("company_id", "=", company_id.id)])
                        if not product_rec:
                            product_rec = self.env['product.template'].sudo().create({
                                "name": product,
                                "type": "consu",
                                "consumable_bom": True,
                                "pos_categ_id": pos_cate_rec.id,
                                "categ_id": general_cate_rec.id,
                                "available_in_pos": True,
                                "company_id":company_id.id
                            })

                        print("PRODUCTSFDS")
                        print(product_rec)
                        if is_grill_qty == "Y":
                            ids = []
                            ids.append(product_rec.id)
                            check_grill_qty = ""
                            check_rec_on_grill_qty = self.env['pos.grill.qty'].sudo().search(
                                [("product_tmpl_ids", "in", ids),
                                 ("company_id","=",company_id.id),
                                 ("name", "=", type),
                                 ("qty", "=", g_qty)],limit=1)
                            print("UNDER GIRLLL")


                            if not check_rec_on_grill_qty:
                                check_rec_on_grill_qty = self.env['pos.grill.qty'].sudo().search(
                                    [("name", "=", type),
                                     ("company_id","=",company_id.id),
                                     ("qty", "=", g_qty)],limit=1)
                                if not check_rec_on_grill_qty:
                                    grill_qty_create = {
                                        "name": type,
                                        "company_id":company_id.id,
                                        "product_tmpl_ids": [(6,0, ids)],
                                        "qty": g_qty,
                                        "price": g_price}
                                    g_r =self.env['pos.grill.qty'].sudo().create(grill_qty_create)
                                    existing_gril_qty = product_rec.pos_grill_qty_ids.ids if product_rec.pos_grill_qty_ids else []
                                    existing_gril_qty.append(g_r.id)
                                    product_rec.write({'pos_grill_qty_ids':[(6,0,existing_gril_qty)]})
                                else:
                                    if check_rec_on_grill_qty.product_tmpl_ids:
                                        exst_ids = check_rec_on_grill_qty.product_tmpl_ids.ids if check_rec_on_grill_qty.product_tmpl_ids else []
                                        exst_ids.append(product_rec.id)

                                    check_rec_on_grill_qty.write({"product_tmpl_ids": [(6,0, exst_ids)]})
                                    existing_gril_qty = product_rec.pos_grill_qty_ids.ids if product_rec.pos_grill_qty_ids else []
                                    existing_gril_qty.append(check_rec_on_grill_qty.id)
                                    product_rec.write({'pos_grill_qty_ids':[(6,0,existing_gril_qty)]})
                            print("UPATED GRILL QTY")
                            # else:
                            #         if check_rec_on_grill_qty.product_tmpl_ids:
                            #             ids.append(check_rec_on_grill_qty.product_tmpl_ids.ids)
                            #         check_rec_on_grill_qty.write({"product_tmpl_ids": [(4, ids)]})
                            #         existing_gril_qty = product_rec.pos_grill_qty_ids.ids if product_rec.pos_grill_qty_ids else []
                            #         product_rec.write({'pos_grill_qty_ids':[(6,0,existing_gril_qty)]})

                print("COMPLETED FOR LOOP")
                _logger.info("COMPLETED FOR LOOP")
            except Exception as e:
                print("--------------------------------------------------------")
                print("EXECTIPn on IMPORTP PRODUCT"+str(e))
                _logger.info("---------loooger------")
                _logger.info(e)

                _logger.info("=-======loggrt===")
                print("-------------------------------------------------------")
                print(e)
        print("Import donE")
        _logger.info("=-======IMPORT DONE===")
        return True

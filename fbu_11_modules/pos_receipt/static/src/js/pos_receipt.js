/** @odoo-module **/

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";


patch(Order.prototype, {
    export_for_printing() {
       const result = super.export_for_printing(...arguments);
       debugger;
       if (this.get_partner()) {
           result.headerData.partner = this.get_partner();
           debugger;
       }
       return result;
   },
    get_validation_date: function () {
    		var validation_date = this.formatted_validation_date ? this.formatted_validation_date.split(' ')[0] : '';
    		return validation_date;
    	},
    	get_validation_time: function () {
    		var validation_time = this.formatted_validation_date ? this.formatted_validation_date.split(' ').slice(-1)[0] : '';
    		return validation_time;
    	},
    	get_current_date: function () {
			var date=new Date();
			var day=("0" + date.getDate()).slice(-2);
			var month=("0" + (date.getMonth() + 1)).slice(-2);
			var year=date.getFullYear();
    		return month+"/"+day+"/"+year;
    	},
    	get_arabic_numbers: function (no) {
			var arabic_no = (no).toLocaleString('ar-SA');
			return arabic_no;
    	},
});





















//odoo.define('pos_receipt.pos_receipt', function (require) {
//"use strict";
//
//	var models = require('point_of_sale.models');
//	var core = require('web.core');
//
//	var _t = core._t;
//
//	models.load_fields('product.product','arabic_name');
//	models.load_fields('res.company', 'receipt_footer');
//	models.load_fields('res.company', 'grill_receipt_footer');
//    models.load_fields('res.company', 'company_short_code');
//
//    var _super_order = models.Order.prototype;
//    models.Order = models.Order.extend({
//    	get_validation_date: function () {
//    		var validation_date = this.formatted_validation_date ? this.formatted_validation_date.split(' ')[0] : '';
//    		return validation_date;
//    	},
//    	get_validation_time: function () {
//    		var validation_time = this.formatted_validation_date ? this.formatted_validation_date.split(' ').slice(-1)[0] : '';
//    		return validation_time;
//    	},
//    	get_current_date: function () {
//			var date=new Date();
//			var day=("0" + date.getDate()).slice(-2);
//			var month=("0" + (date.getMonth() + 1)).slice(-2);
//			var year=date.getFullYear();
//    		return month+"/"+day+"/"+year;
//    	},
//    	get_arabic_numbers: function (no) {
//			var arabic_no = (no).toLocaleString('ar-SA');
//			return arabic_no;
//    	},
//    });
//
//
//});
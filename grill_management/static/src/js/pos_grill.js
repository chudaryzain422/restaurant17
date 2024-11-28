/** @odoo-module */
import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
patch(Order.prototype, {
   export_for_printing() {
       const result = super.export_for_printing(...arguments);
       debugger;
       if (this.pos.config.module_pos_grill) {
           result.module_pos_grill = this.pos.config.module_pos_grill;
           result.partner = this.pos.get_order().get_partner();
       }
       return result;
   },
});
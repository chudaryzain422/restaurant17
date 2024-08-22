/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { Order } from "@custom_pos_preparation_display/app/models/order";

patch(Order.prototype, {
    setup(order) {
        super.setup(...arguments);
        this.table = order.table;
    },
});

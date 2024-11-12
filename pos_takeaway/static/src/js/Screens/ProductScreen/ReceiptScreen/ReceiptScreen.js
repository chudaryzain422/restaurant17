/** @odoo-module */

import { Order, Orderline } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    export_for_printing() {
        return {
            ...super.export_for_printing(...arguments),
            takeaway: this.pos.selectedOrder.is_take_away,
            token_number : this.pos.selectedOrder.token_number,
        };
    },

    init_from_JSON(json) {
        super.init_from_JSON(json);
        this.is_take_away = json.is_take_away;
        this.is_takeaway = json.is_takeaway;
    },
    export_as_JSON() {
        const json = super.export_as_JSON();
        json.is_take_away = this.is_take_away;
        json.is_takeaway = this.is_takeaway;
        return json;
    },
});

patch(Orderline.prototype, {

    init_from_JSON(json) {
        super.init_from_JSON(json);
        this.takeaway_pos_line = json.takeaway_pos_line;
    },

    export_as_JSON() {
        const json = super.export_as_JSON();
        json.takeaway_pos_line = this.takeaway_pos_line
        return json;
    },
});

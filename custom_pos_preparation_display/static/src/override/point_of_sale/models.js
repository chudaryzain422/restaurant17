/** @odoo-module **/
import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    // This function send order change to preparation display.
    // For sending changes to printer see printChanges function.
    setup() {
        super.setup(...arguments);
        this.noteHistory = {};
    },
                                 // new parameter added here
    async sendChanges(cancelled, isSplit = false) {
        debugger;
        for (const note of Object.values(this.noteHistory)) {
            for (const n of note) {
                const line = this.get_orderline(n.lineId);
                n.qty = line?.get_quantity();
            }
        }

        await this.pos.sendDraftToServer();
        debugger;
        await this.env.services.orm.call("custom_pos_preparation_display.order", "process_order", [
            this.server_id,
            cancelled,
            this.noteHistory,
            isSplit,  // new argument added here
        ]);
        debugger;

        // if (result && !this.finalized && this.pos.config.module_pos_restaurant) {
        //     // This avoids the need to copy logic from the frontend to the backend.
        //     // We send the "last_order_change" back to the server
        //     await this.pos.sendDraftToServer();
        // }
        debugger;

        this.noteHistory = {};
        return true;
    },
    setCustomerCount(count) {
        super.setCustomerCount(count);
        this.pos.ordersToUpdateSet.add(this);
    },
});

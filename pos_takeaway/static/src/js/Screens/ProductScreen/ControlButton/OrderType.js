/** @odoo-module **/
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { useRef } from "@odoo/owl";

export class TakeAwayLine extends ProductScreen {
    static template = "TakeAwayLine";
    setup() {
        this.pos = usePos();
        this.orm = useService("orm");
        this.TakeAway = useRef("TakeAway");
    }
    async onClick() {
        debugger;
        const order = this.pos.get_order();
        const selected_orderline = order.get_selected_orderline();
        debugger;
        if (selected_orderline) {
            selected_orderline.takeaway_pos_line = true;
            this.render();
        } else {
            alert('Please select a product!');
        }
    }
}
// Register the component
ProductScreen.addControlButton({
    component: TakeAwayLine,
    condition: function () {
        return this.pos.config.module_pos_restaurant && this.pos.config.is_pos_takeaway;
    },
});

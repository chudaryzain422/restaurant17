/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class TakeAwayLine extends Component {
    static template = "pos_takeaway.TakeAwayLine";

    setup() {
        this.pos = usePos();
    }

    get selectedOrderline() {
        return this.pos.get_order().get_selected_orderline();
    }

    // Method triggered on button click
    async click() {
        // Check if an order line is selected
        if (!this.selectedOrderline) {
            alert(_t("Please select a product!")); // Alert if no order line is selected
            return;
        }

        // Mark the order line as Takeaway
        this.selectedOrderline.takeaway_pos_line = true; // Set custom field to indicate takeaway
        this.selectedOrderline.setNote(_t("Takeaway")); // Set the note for the kitchen screen
        this.render();

    }
}

// Register the Takeaway button in the POS ProductScreen
ProductScreen.addControlButton({
    component: TakeAwayLine,
    condition: function () {
        // Display the button only if the POS config allows it
        return this.pos.config.module_pos_restaurant && this.pos.config.is_pos_takeaway;
    },
});





///** @odoo-module **/
//import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
//import { usePos } from "@point_of_sale/app/store/pos_hook";
//import { useService } from "@web/core/utils/hooks";
//import { useRef } from "@odoo/owl";
//
//export class TakeAwayLine extends ProductScreen {
//    static template = "TakeAwayLine";
//    setup() {
//        this.pos = usePos();
//        this.orm = useService("orm");
//        this.TakeAway = useRef("TakeAway");
//    }
//    async onClick() {
//        debugger;
//        const order = this.pos.get_order();
//        const selected_orderline = order.get_selected_orderline();
//        debugger;
//        if (selected_orderline) {
//            selected_orderline.takeaway_pos_line = true;
//            this.render();
//        } else {
//            alert('Please select a product!');
//        }
//    }
//}
//// Register the component
//ProductScreen.addControlButton({
//    component: TakeAwayLine,
//    condition: function () {
//        return this.pos.config.module_pos_restaurant && this.pos.config.is_pos_takeaway;
//    },
//});

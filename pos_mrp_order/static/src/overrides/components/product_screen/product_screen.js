/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";
/**
 * @props partner
 */

patch(ActionpadWidget.prototype, {

    createMRP() {
        debugger;
        const order = this.currentOrder;
        var order_line = order.get_orderlines()
        var due = order.get_due();
        for (var i in order_line){
            var list_product = []
            if (order_line[i].product){
                if (order_line[i].quantity>0){
                    var product_dict = {
                        'id': order_line[i].product.id,
                        'qty': order_line[i].quantity,
                        'product_tmpl_id': order_line[i].product.product_tmpl_id,
                        'pos_reference': order.name,
                        'uom_id': order_line[i].product.uom_id[0],
                    };
                    list_product.push(product_dict);
                }
            }
            if (list_product.length){
                debugger;
                this.pos.orm.call('mrp.production', 'create_mrp_from_pos', [1,list_product])
            }
        }
    },
    async submitOrder() {
        debugger;
        if (!this.clicked) {
            this.clicked = true;
            try {
                await this.pos.sendOrderInPreparationUpdateLastChange(this.currentOrder);
                this.createMRP();
            } finally {
                this.clicked = false;
            }
        }
        debugger;
    },


});
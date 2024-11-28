/** @odoo-module */
import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";
import { floatIsZero } from "@web/core/utils/numbers";
import { _t } from "@web/core/l10n/translation";

export class GrillOrderPopupWidget extends AbstractAwaitablePopup {
    static template = "fbu_pos_grill.GrillOrderPopupWidget";
    static components = { ProductCard };

    setup() {
        debugger;
        super.setup();
        this.pos = usePos();
    }

    areAllCombosSelected() {
        return Object.values(this.state.combo).every((x) => Boolean(x));
    }

    formattedComboPrice(comboLine) {
        const combo_price = comboLine.combo_price;
        if (floatIsZero(combo_price)) {
            return "";
        } else {
            const product = this.pos.db.product_by_id[comboLine.product_id[0]];
            return this.env.utils.formatCurrency(product.get_display_price({ price: combo_price }));
        }
    }

    /**
     * @returns {Object}
     */
    getPayload() {
        return Object.values(this.state.combo)
            .filter((x) => x) // we only keep the non-zero values
            .map((x) => {
                const combo_line = this.pos.db.combo_line_by_id[x];
                return {
                    ...combo_line,
                    configuration: this.state.configuration[combo_line.id],
                };
            });
    }

    async onClickProduct({ product, combo_line }, ev) {
        if (product.isConfigurable()) {
            const { confirmed, payload } = await product.openConfigurator({ initQuantity: 1 });
            if (confirmed) {
                this.state.configuration[combo_line.id] = payload;
            } else {
                // Do not select the product if configuration popup is cancelled.
                this.state.combo[combo_line.id] = 0;
            }
        }
    }
}
/** @odoo-module */

import { constructFullProductName, random5Chars, uuidv4, qrCodeSrc } from "@point_of_sale/utils";
// FIXME POSREF - unify use of native parseFloat and web's parseFloat. We probably don't need the native version.
import { parseFloat as oParseFloat } from "@web/views/fields/parsers";
import {
    formatDate,
    formatDateTime,
    serializeDateTime,
    deserializeDate,
    deserializeDateTime,
} from "@web/core/l10n/dates";
import {
    formatFloat,
    roundDecimals as round_di,
    roundPrecision as round_pr,
    floatIsZero,
} from "@web/core/utils/numbers";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { ProductConfiguratorPopup } from "@point_of_sale/app/store/product_configurator_popup/product_configurator_popup";
import { ComboConfiguratorPopup } from "./combo_configurator_popup/combo_configurator_popup";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { _t } from "@web/core/l10n/translation";
import { renderToElement } from "@web/core/utils/render";
import { ProductCustomAttribute } from "./models/product_custom_attribute";
import { omit } from "@web/core/utils/objects";

const { DateTime } = luxon;


// An Order contains zero or more Orderlines.
export class Orderline extends PosModel {
    setup(_defaultObj, options) {
        super.setup(...arguments);
        this.pos = options.pos;
        this.order = options.order;
        this.price_type = options.price_type;
        this.uuid = this.uuid || uuidv4();

        this.price_type = options.price_type || "original";
        if (options.json) {
            try {
                this.init_from_JSON(options.json);
            } catch (error) {
                console.error(
                    "ERROR: attempting to recover product ID",
                    options.json.product_id[0],
                    "not available in the point of sale. Correct the product or clean the browser cache."
                );
                throw error;
            }
            return;
        }
        this.product = options.product;
        this.tax_ids = options.tax_ids;
        this.set_product_lot(this.product);
        options.quantity ? this.set_quantity(options.quantity) : this.set_quantity(1);
        this.discount = 0;
        this.note = "";
        this.custom_attribute_value_ids = [];
        this.hasChange = false;
        this.skipChange = false;
        this.discountStr = "0";
        this.selected = false;
        this.price_extra = 0;
        this.full_product_name = "";
        this.id = orderline_id++;
        this.customerNote = this.customerNote || "";
        this.saved_quantity = 0;

        if (options.price) {
            this.set_unit_price(options.price);
        } else {
            this.set_unit_price(this.product.get_price(this.order.pricelist, this.get_quantity()));
        }
    }
    init_from_JSON(json) {
        this.product = this.pos.db.get_product_by_id(json.product_id);
        this.set_product_lot(this.product);
        this.price = json.price_unit;
        this.price_type = json.price_type || "original";
        this.set_discount(json.discount);
        this.set_quantity(json.qty, "do not recompute unit price");
        this.attribute_value_ids = json.attribute_value_ids || [];
        this.set_price_extra(json.price_extra);
        this.custom_attribute_value_ids = json.custom_attribute_value_ids.map((attr) => {
            if (attr.length > 0) {
                attr = attr[2];
            }
            return new ProductCustomAttribute(attr);
        });
        this.set_full_product_name();
        this.id = json.server_id || json.id || orderline_id++;
        orderline_id = Math.max(this.id + 1, orderline_id);
        var pack_lot_lines = json.pack_lot_ids;
        for (var i = 0; i < pack_lot_lines.length; i++) {
            var packlotline = pack_lot_lines[i][2];
            var pack_lot_line = new Packlotline(
                { env: this.env },
                { json: { ...packlotline, order_line: this } }
            );
            this.pack_lot_lines.add(pack_lot_line);
        }
        this.tax_ids = json.tax_ids && json.tax_ids.length !== 0 ? json.tax_ids[0][2] : undefined;
        this.set_customer_note(json.customer_note);
        this.refunded_qty = json.refunded_qty;
        this.refunded_orderline_id = json.refunded_orderline_id;
        this.saved_quantity = json.qty;
        this.uuid = json.uuid;
        this.skipChange = json.skip_change;
        this.combo_line_ids = json.combo_line_ids;
        this.combo_parent_id = json.combo_parent_id;
        this.comboLine = this.pos.db.combo_line_by_id[json.combo_line_id];
    }
    clone() {
        var orderline = new Orderline(
            { env: this.env },
            {
                pos: this.pos,
                order: this.order,
                product: this.product,
                price: this.price,
            }
        );
        orderline.order = null;
        orderline.custom_attribute_value_ids = this.custom_attribute_value_ids;
        orderline.quantity = this.quantity;
        orderline.quantityStr = this.quantityStr;
        orderline.discount = this.discount;
        orderline.price = this.price;
        orderline.selected = false;
        orderline.price_type = this.price_type;
        orderline.customerNote = this.customerNote;
        return orderline;
    }
    getDisplayClasses() {
        return {};
    }
    getPackLotLinesToEdit(isAllowOnlyOneLot) {
        const currentPackLotLines = this.pack_lot_lines;
        let nExtraLines = Math.abs(this.quantity) - currentPackLotLines.length;
        nExtraLines = Math.ceil(nExtraLines);
        nExtraLines = nExtraLines > 0 ? nExtraLines : 1;
        const tempLines = currentPackLotLines
            .map((lotLine) => ({
                id: lotLine.cid,
                text: lotLine.lot_name,
            }))
            .concat(
                Array.from(Array(nExtraLines)).map((_) => ({
                    text: "",
                }))
            );
        return isAllowOnlyOneLot ? [tempLines[0]] : tempLines;
    }
    // What if a number different from 1 (or -1) is specified
    // to an orderline that has product tracked by lot? Lot tracking (based
    // on the current implementation) requires that 1 item per orderline is
    // allowed.
    async editPackLotLines() {
        const isAllowOnlyOneLot = this.product.isAllowOnlyOneLot();
        const editedPackLotLines = await this.pos.getEditedPackLotLines(
            isAllowOnlyOneLot,
            this.getPackLotLinesToEdit(isAllowOnlyOneLot),
            this.product.display_name
        );
        if (!editedPackLotLines) {
            return;
        }
        this.setPackLotLines(editedPackLotLines);
        this.order.select_orderline(this);
    }
    /**
     * @param { modifiedPackLotLines, newPackLotLines }
     *    @param {Object} modifiedPackLotLines key-value pair of String (the cid) & String (the new lot_name)
     *    @param {Array} newPackLotLines array of { lot_name: String }
     */
    setPackLotLines({ modifiedPackLotLines, newPackLotLines, setQuantity = true }) {
        // Set the new values for modified lot lines.
        const lotLinesToRemove = [];
        for (const lotLine of this.pack_lot_lines) {
            const modifiedLotName = modifiedPackLotLines[lotLine.cid];
            if (modifiedLotName) {
                lotLine.lot_name = modifiedLotName;
            } else {
                // We should not call lotLine.remove() here because
                // we don't want to mutate the array while looping thru it.
                lotLinesToRemove.push(lotLine);
            }
        }

        // Remove those that needed to be removed.
        for (const lotLine of lotLinesToRemove) {
            this.pack_lot_lines.remove(lotLine);
        }

        // Create new pack lot lines.
        let newPackLotLine;
        for (const newLotLine of newPackLotLines) {
            newPackLotLine = new Packlotline({ env: this.env }, { order_line: this });
            newPackLotLine.lot_name = newLotLine.lot_name;
            this.pack_lot_lines.add(newPackLotLine);
        }

        // Set the quantity of the line based on number of pack lots.
        if (!this.product.to_weight && setQuantity) {
            this.set_quantity_by_lot();
        }
    }
    set_product_lot(product) {
        this.has_product_lot = product.tracking !== "none";
        this.pack_lot_lines = this.has_product_lot && new PosCollection();
    }
    getNote() {
        return this.note;
    }
    setNote(note) {
        this.note = note;
    }
    setHasChange(isChange) {
        this.hasChange = isChange;
    }
    // sets a discount [0,100]%
    set_discount(discount) {
        var parsed_discount =
            typeof discount === "number"
                ? discount
                : isNaN(parseFloat(discount))
                ? 0
                : oParseFloat("" + discount);
        var disc = Math.min(Math.max(parsed_discount || 0, 0), 100);
        this.discount = disc;
        this.discountStr = "" + disc;
    }
    // returns the discount [0,100]%
    get_discount() {
        return this.discount;
    }
    get_discount_str() {
        return this.discountStr;
    }
    set_price_extra(price_extra) {
        this.price_extra = parseFloat(price_extra) || 0.0;
    }
    set_full_product_name() {
        this.full_product_name = this.product.display_name;
    }
    get_price_extra() {
        return this.price_extra;
    }
    updateSavedQuantity() {
        this.saved_quantity = this.quantity;
    }
    // sets the quantity of the product. The quantity will be rounded according to the
    // product's unity of measure properties. Quantities greater than zero will not get
    // rounded to zero
    // Return true if successfully set the quantity, otherwise, return false.
    set_quantity(quantity, keep_price) {
        this.order.assert_editable();
        var quant =
            typeof quantity === "number" ? quantity : oParseFloat("" + (quantity ? quantity : 0));
        if (this.refunded_orderline_id in this.pos.toRefundLines) {
            const toRefundDetail = this.pos.toRefundLines[this.refunded_orderline_id];
            const maxQtyToRefund =
                toRefundDetail.orderline.qty - toRefundDetail.orderline.refundedQty;
            if (quant > 0) {
                this.env.services.popup.add(ErrorPopup, {
                    title: _t("Positive quantity not allowed"),
                    body: _t(
                        "Only a negative quantity is allowed for this refund line. Click on +/- to modify the quantity to be refunded."
                    ),
                });
                return false;
            } else if (quant == 0) {
                toRefundDetail.qty = 0;
            } else if (-quant <= maxQtyToRefund) {
                toRefundDetail.qty = -quant;
            } else {
                this.env.services.popup.add(ErrorPopup, {
                    title: _t("Greater than allowed"),
                    body: _t(
                        "The requested quantity to be refunded is higher than the refundable quantity of %s.",
                        this.env.utils.formatProductQty(maxQtyToRefund)
                    ),
                });
                return false;
            }
        }
        var unit = this.get_unit();
        if (unit) {
            if (unit.rounding) {
                var decimals = this.pos.dp["Product Unit of Measure"];
                var rounding = Math.max(unit.rounding, Math.pow(10, -decimals));
                this.quantity = round_pr(quant, rounding);
                this.quantityStr = formatFloat(this.quantity, {
                    digits: [69, decimals],
                });
            } else {
                this.quantity = round_pr(quant, 1);
                this.quantityStr = this.quantity.toFixed(0);
            }
        } else {
            this.quantity = quant;
            this.quantityStr = "" + this.quantity;
        }

        // just like in sale.order changing the quantity will recompute the unit price
        if (!keep_price && this.price_type === "original") {
            this.set_unit_price(
                this.product.get_price(
                    this.order.pricelist,
                    this.get_quantity(),
                    this.get_price_extra()
                )
            );
            this.order.fix_tax_included_price(this);
        }
        return true;
    }
    // return the quantity of product
    get_quantity() {
        return this.quantity;
    }
    get_quantity_str() {
        return this.quantityStr;
    }
    get_quantity_str_with_unit() {
        if (this.is_pos_groupable()) {
            return this.quantityStr + " " + this.get_unit().name;
        } else {
            return this.quantityStr;
        }
    }

    get_lot_lines() {
        return this.pack_lot_lines && this.pack_lot_lines;
    }

    get_required_number_of_lots() {
        var lots_required = 1;

        if (this.product.tracking == "serial") {
            lots_required = Math.abs(this.quantity);
        }

        return lots_required;
    }

    get_valid_lots() {
        return this.pack_lot_lines.filter((item) => {
            return item.lot_name;
        });
    }

    set_quantity_by_lot() {
        var valid_lots_quantity = this.get_valid_lots().length;
        if (this.quantity < 0) {
            valid_lots_quantity = -valid_lots_quantity;
        }
        this.set_quantity(valid_lots_quantity);
    }

    has_valid_product_lot() {
        if (!this.has_product_lot) {
            return true;
        }
        var valid_product_lot = this.get_valid_lots();
        return this.get_required_number_of_lots() === valid_product_lot.length;
    }

    // return the unit of measure of the product
    get_unit() {
        return this.product.get_unit();
    }
    // return the product of this orderline
    get_product() {
        return this.product;
    }
    get_full_product_name() {
        return this.full_product_name || this.product.display_name;
    }
    /**
     * Return the full product name with variant details.
     *
     * e.g. Desk Organiser product with variant:
     * - Size: S
     * - Fabric: Plastic
     *
     * -> "Desk Organiser (S, Plastic)"
     * @returns {string}
     */
    get_full_product_name_with_variant() {
        return constructFullProductName(
            this,
            this.pos.db.attribute_value_by_id,
            this.product.display_name
        );
    }
    // selects or deselects this orderline
    set_selected(selected) {
        this.selected = selected;
        // this trigger also triggers the change event of the collection.
    }
    // returns true if this orderline is selected
    is_selected() {
        return this.selected;
    }
    // when we add an new orderline we want to merge it with the last line to see reduce the number of items
    // in the orderline. This returns true if it makes sense to merge the two
    can_be_merged_with(orderline) {
        var price = parseFloat(
            round_di(this.price || 0, this.pos.dp["Product Price"]).toFixed(
                this.pos.dp["Product Price"]
            )
        );
        var order_line_price = orderline
            .get_product()
            .get_price(orderline.order.pricelist, this.get_quantity());
        order_line_price = round_di(
            orderline.compute_fixed_price(order_line_price),
            this.pos.currency.decimal_places
        );
        let hasSameAttributes = Object.keys(Object(orderline.attribute_value_ids)).length === Object.keys(Object(this.attribute_value_ids)).length;
        if(hasSameAttributes && Object(orderline.attribute_value_ids)?.length && Object(this.attribute_value_ids)?.length) {
            hasSameAttributes = orderline.attribute_value_ids.every((value, index) => value === this.attribute_value_ids[index]);
        }
        return (
            !this.skipChange &&
            orderline.getNote() === this.getNote() &&
            this.get_product().id === orderline.get_product().id &&
            this.get_unit() &&
            this.is_pos_groupable() &&
            // don't merge discounted orderlines
            this.get_discount() === 0 &&
            floatIsZero(
                price - order_line_price - orderline.get_price_extra(),
                this.pos.currency.decimal_places
            ) &&
            !(
                this.product.tracking === "lot" &&
                (this.pos.picking_type.use_create_lots || this.pos.picking_type.use_existing_lots)
            ) &&
            this.full_product_name === orderline.full_product_name &&
            orderline.get_customer_note() === this.get_customer_note() &&
            !this.refunded_orderline_id &&
            !this.isPartOfCombo() &&
            !orderline.isPartOfCombo() &&
            hasSameAttributes
        );
    }
    is_pos_groupable() {
        return this.get_unit()?.is_pos_groupable && !this.isPartOfCombo();
    }
    merge(orderline) {
        this.order.assert_editable();
        this.set_quantity(this.get_quantity() + orderline.get_quantity());
    }
    export_as_JSON() {
        var pack_lot_ids = [];
        if (this.has_product_lot) {
            this.pack_lot_lines.forEach((item) => {
                return pack_lot_ids.push([0, 0, item.export_as_JSON()]);
            });
        }
        return {
            uuid: this.uuid,
            skip_change: this.skipChange,
            custom_attribute_value_ids: this.custom_attribute_value_ids.map((attr) => [0, 0, attr]),
            qty: this.get_quantity(),
            price_unit: this.get_unit_price(),
            price_subtotal: this.get_price_without_tax(),
            price_subtotal_incl: this.get_price_with_tax(),
            discount: this.get_discount(),
            product_id: this.get_product().id,
            tax_ids: [[6, false, this.get_applicable_taxes().map((tax) => tax.id)]],
            id: this.id,
            pack_lot_ids: pack_lot_ids,
            attribute_value_ids: this.attribute_value_ids || [],
            full_product_name: this.get_full_product_name(),
            price_extra: this.get_price_extra(),
            customer_note: this.get_customer_note(),
            refunded_orderline_id: this.refunded_orderline_id,
            price_type: this.price_type,
            combo_line_ids: this.comboLines?.map((line) => line.id || line.cid),
            combo_parent_id: this.comboParent?.id || this.comboParent?.cid,
            combo_line_id: this.comboLine?.id,
        };
    }

    // changes the base price of the product for this orderline
    set_unit_price(price) {
        this.order.assert_editable();
        var parsed_price = !isNaN(price)
            ? price
            : isNaN(parseFloat(price))
            ? 0
            : oParseFloat("" + price);
        this.price = round_di(parsed_price || 0, this.pos.dp["Product Price"]);
    }
    get_unit_price() {
        var digits = this.pos.dp["Product Price"];
        // round and truncate to mimic _symbol_set behavior
        return parseFloat(round_di(this.price || 0, digits).toFixed(digits));
    }
    get_unit_display_price() {
        if (this.pos.config.iface_tax_included === "total") {
            return this.get_all_prices(1).priceWithTax;
        } else {
            return this.get_all_prices(1).priceWithoutTax;
        }
    }
    /**
     * This is the price that will appear as striked through.
     * @returns {number | false}
     */
    get_old_unit_display_price() {
        return (
            this.display_discount_policy() === "without_discount" &&
            this.env.utils.roundCurrency(this.get_unit_display_price()) <
                this.env.utils.roundCurrency(this.get_taxed_lst_unit_price()) &&
            this.get_taxed_lst_unit_price()
        );
    }
    getUnitDisplayPriceBeforeDiscount() {
        if (this.pos.config.iface_tax_included === "total") {
            return this.get_all_prices(1).priceWithTaxBeforeDiscount;
        } else {
            return this.get_all_prices(1).priceWithoutTaxBeforeDiscount;
        }
    }
    get_base_price() {
        var rounding = this.pos.currency.rounding;
        return round_pr(
            this.get_unit_price() * this.get_quantity() * (1 - this.get_discount() / 100),
            rounding
        );
    }
    get_display_price_one() {
        var rounding = this.pos.currency.rounding;
        var price_unit = this.get_unit_price();
        if (this.pos.config.iface_tax_included !== "total") {
            return round_pr(price_unit * (1.0 - this.get_discount() / 100.0), rounding);
        } else {
            var product = this.get_product();
            var taxes_ids = this.tax_ids || product.taxes_id;
            var product_taxes = this.pos.get_taxes_after_fp(taxes_ids, this.order.fiscal_position);
            var all_taxes = this.compute_all(
                product_taxes,
                price_unit,
                1,
                this.pos.currency.rounding
            );

            return round_pr(all_taxes.total_included * (1 - this.get_discount() / 100), rounding);
        }
    }
    get_display_price() {
        if (this.pos.config.iface_tax_included === "total") {
            return this.get_price_with_tax();
        } else {
            return this.get_price_without_tax();
        }
    }
    get_taxed_lst_unit_price() {
        const lstPrice = this.compute_fixed_price(this.get_lst_price());
        const product = this.get_product();
        const taxesIds = product.taxes_id;
        const productTaxes = this.pos.get_taxes_after_fp(taxesIds, this.order.fiscal_position);
        const unitPrices = this.compute_all(productTaxes, lstPrice, 1, this.pos.currency.rounding);
        if (this.pos.config.iface_tax_included === "total") {
            return unitPrices.total_included;
        } else {
            return unitPrices.total_excluded;
        }
    }
    get_price_without_tax() {
        return this.get_all_prices().priceWithoutTax;
    }
    get_price_with_tax() {
        return this.get_all_prices().priceWithTax;
    }
    get_price_with_tax_before_discount() {
        return this.get_all_prices().priceWithTaxBeforeDiscount;
    }
    get_tax() {
        return this.get_all_prices().tax;
    }
    get_applicable_taxes() {
        var i;
        // Shenaningans because we need
        // to keep the taxes ordering.
        var ptaxes_ids = this.tax_ids || this.get_product().taxes_id;
        var ptaxes_set = {};
        for (i = 0; i < ptaxes_ids.length; i++) {
            ptaxes_set[ptaxes_ids[i]] = true;
        }
        var taxes = [];
        for (i = 0; i < this.pos.taxes.length; i++) {
            if (ptaxes_set[this.pos.taxes[i].id]) {
                taxes.push(this.pos.taxes[i]);
            }
        }
        return taxes;
    }
    get_tax_details() {
        return this.get_all_prices().taxDetails;
    }
    get_taxes() {
        var taxes_ids = this.tax_ids || this.get_product().taxes_id;
        return this.pos.getTaxesByIds(taxes_ids);
    }
    /**
     * Calculate the amount of taxes of a specific Orderline, that are included in the price.
     * @returns {Number} the total amount of price included taxes
     */
    get_total_taxes_included_in_price() {
        const productTaxes = this._getProductTaxesAfterFiscalPosition();
        const taxDetails = this.get_tax_details();
        return productTaxes
            .filter((tax) => tax.price_include)
            .reduce((sum, tax) => sum + taxDetails[tax.id].amount, 0);
    }
    _map_tax_fiscal_position(tax, order = false) {
        return this.pos._map_tax_fiscal_position(tax, order);
    }
    /**
     * Mirror JS method of:
     * _compute_amount in addons/account/models/account.py
     */
    _compute_all(tax, base_amount, quantity, price_exclude) {
        return this.pos._compute_all(tax, base_amount, quantity, price_exclude);
    }
    /**
     * Mirror JS method of:
     * compute_all in addons/account/models/account.py
     *
     * Read comments in the python side method for more details about each sub-methods.
     */
    compute_all(taxes, price_unit, quantity, currency_rounding, handle_price_include = true) {
        return this.pos.compute_all(
            taxes,
            price_unit,
            quantity,
            currency_rounding,
            handle_price_include
        );
    }
    /**
     * Calculates the taxes for a product, and converts the taxes based on the fiscal position of the order.
     *
     * @returns {Object} The calculated product taxes after filtering and fiscal position conversion.
     */
    _getProductTaxesAfterFiscalPosition() {
        const product = this.get_product();
        let taxesIds = this.tax_ids || product.taxes_id;
        taxesIds = taxesIds.filter((t) => t in this.pos.taxes_by_id);
        return this.pos.get_taxes_after_fp(taxesIds, this.order.fiscal_position);
    }
    get_all_prices(qty = this.get_quantity()) {
        var price_unit = this.get_unit_price() * (1.0 - this.get_discount() / 100.0);
        var taxtotal = 0;

        var product = this.get_product();
        var taxes_ids = this.tax_ids || product.taxes_id;
        taxes_ids = taxes_ids.filter((t) => t in this.pos.taxes_by_id);
        var taxdetail = {};
        var product_taxes = this.pos.get_taxes_after_fp(taxes_ids, this.order.fiscal_position);

        var all_taxes = this.compute_all(
            product_taxes,
            price_unit,
            qty,
            this.pos.currency.rounding
        );
        var all_taxes_before_discount = this.compute_all(
            product_taxes,
            this.get_unit_price(),
            qty,
            this.pos.currency.rounding
        );
        all_taxes.taxes.forEach(function (tax) {
            taxtotal += tax.amount;
            taxdetail[tax.id] = {
                amount: tax.amount,
                base: tax.base,
            };
        });

        return {
            priceWithTax: all_taxes.total_included,
            priceWithoutTax: all_taxes.total_excluded,
            priceWithTaxBeforeDiscount: all_taxes_before_discount.total_included,
            priceWithoutTaxBeforeDiscount: all_taxes_before_discount.total_excluded,
            tax: taxtotal,
            taxDetails: taxdetail,
        };
    }
    display_discount_policy() {
        return this.order.pricelist ? this.order.pricelist.discount_policy : "with_discount";
    }
    compute_fixed_price(price) {
        return this.pos.computePriceAfterFp(price, this.get_taxes());
    }
    get_fixed_lst_price() {
        return this.compute_fixed_price(this.get_lst_price());
    }
    get_lst_price() {
        return this.product.get_price(this.pos.default_pricelist, 1, this.price_extra);
    }
    set_lst_price(price) {
        this.order.assert_editable();
        this.product.lst_price = round_di(parseFloat(price) || 0, this.pos.dp["Product Price"]);
    }
    is_last_line() {
        var order = this.pos.get_order();
        var orderlines = order.orderlines;
        var last_id = orderlines[orderlines.length - 1].cid;
        var selectedLine = order ? order.selected_orderline : null;

        return !selectedLine ? false : last_id === selectedLine.cid;
    }
    set_customer_note(note) {
        this.customerNote = note || "";
    }
    get_customer_note() {
        return this.customerNote;
    }
    get_total_cost() {
        return this.product.standard_price * this.quantity;
    }
    /**
     * Checks if the current line is a tip from a customer.
     * @returns Boolean
     */
    isTipLine() {
        const tipProduct = this.pos.config.tip_product_id;
        return tipProduct && this.product.id === tipProduct[0];
    }

    /**
     * @returns {Orderline[]} all the lines that are in the same combo tree as the given line
     * (including the given line), or just the given line if it is not part of a combo.
     */
    getAllLinesInCombo() {
        if (this.comboParent) {
            // having a `comboParent` means that we are not
            // at the root node of the combo tree.
            // Thus, we first navigate to the root
            return this.comboParent.getAllLinesInCombo();
        }
        const lines = [];
        const stack = [this];
        while (stack.length) {
            const n = stack.pop();
            lines.push(n);
            if (n.comboLines) {
                stack.push(...n.comboLines);
            }
        }
        return lines;
    }
    isPartOfCombo() {
        return Boolean(this.comboParent || this.comboLines?.length);
    }
    findAttribute(values, customAttributes) {
        const listOfAttributes = [];
        const addedPtal_id = [];
        for (const value of values){
            for (const ptal_id of this.pos.ptal_ids_by_ptav_id[value]){
                if (addedPtal_id.includes(ptal_id)){
                    continue;
                }
                const attribute = this.pos.attributes_by_ptal_id[ptal_id]
                const attFound = attribute.values.filter((target) => {
                    return Object.values(values).includes(target.id);
                }).map(att => ({...att})); // make a copy
                attFound.forEach((att) => {
                    if (att.is_custom) {
                        customAttributes.forEach((customAttribute) => {
                            if (att.id === customAttribute.custom_product_template_attribute_value_id) {
                                att.name = customAttribute.value;
                            }
                        });
                    }
                });
                const modifiedAttribute = {
                    ...attribute,
                    valuesForOrderLine: attFound,
                };
                listOfAttributes.push(modifiedAttribute);
                addedPtal_id.push(ptal_id);
            }
        }
        return listOfAttributes;
    }
    getDisplayData() {
        return {
            productName: this.get_full_product_name(),
            price:
                this.get_discount_str() === "100"
                    ? "free"
                    : this.env.utils.formatCurrency(this.get_display_price()),
            qty: this.get_quantity_str(),
            unit: this.get_unit().name,
            unitPrice: this.env.utils.formatCurrency(this.get_unit_display_price()),
            oldUnitPrice: this.env.utils.formatCurrency(this.get_old_unit_display_price()),
            discount: this.get_discount_str(),
            customerNote: this.get_customer_note(),
            internalNote: this.getNote(),
            comboParent: this.comboParent?.get_full_product_name(),
            pack_lot_lines: this.get_lot_lines(),
            price_without_discount: this.env.utils.formatCurrency(
                this.getUnitDisplayPriceBeforeDiscount()
            ),
            attributes: this.attribute_value_ids
                ? this.findAttribute(this.attribute_value_ids, this.custom_attribute_value_ids)
                : [],
        };
    }
}

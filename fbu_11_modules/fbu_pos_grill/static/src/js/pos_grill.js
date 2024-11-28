/** @odoo-module */

import { Order, Orderline, Payment } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { sprintf } from "@web/core/utils/strings";
import { parseFloat } from "@web/views/fields/parsers";
import { floatIsZero } from "@web/core/utils/numbers";
import { useBus, useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { ControlButtonsMixin } from "@point_of_sale/app/utils/control_buttons_mixin";
import { GrillOrderPopupWidget } from "./grill_screen";

import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";

import { Component, onMounted, useRef } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";


// New orders are now associated with the current table, if any.
patch(Order.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
    },
    async add_product(product, options) {
        const result = await super.add_product(...arguments);
        var self = this;
        var selected_orderline = this.get_selected_orderline();
        //selected_orderline.set_grill_peroduct(product);
        this.display_grill_popup();
        if(selected_orderline && (selected_orderline.is_grill_service || selected_orderline.is_consumable_bom)){
            debugger;
            var grill_method_id = product.pos_grill_method_id ? product.pos_grill_method_id[0] : undefined;
            if (grill_method_id){
                var grill_method = this.pos.db.get_grill_method_by_id(grill_method_id);
                selected_orderline.set_grillmethod(grill_method);
            }
            var grill_qty_id = product.pos_grill_qty_ids ? product.pos_grill_qty_ids[0] : undefined;
            if (!this.is_return_order && grill_qty_id){
                var grillqty = this.pos.db.get_pos_grill_qty_by_id(grill_qty_id);
                var grill_nqty = selected_orderline.get_grillnqty() || 1;
                var qty_grill = grillqty ? grillqty.qty : 0;
                var qty = grill_nqty * qty_grill;
                selected_orderline.set_grillqty(grillqty);
                selected_orderline.set_quantity(qty);
            }
            if (options.pos_grill_qty_id){
                var grillqty = this.pos.db.get_pos_grill_qty_by_id(options.pos_grill_qty_id);
                selected_orderline.set_grillqty(grillqty);
            }
            debugger;
            this.display_grill_popup();
        }
        return result;
    },
    display_grill_popup(){
        debugger;
        var order_line = this.get_selected_orderline();
        if (order_line){
            debugger;
            const { confirmed, payload } =  this.env.services.popup.add(
                GrillOrderPopupWidget,
                {
                product: this,
                order_line: order_line,
                order: this,
                 });
            if (!confirmed) {
                debugger;
                return;
            }


//            this.env.services.popup.add(GrillOrderPopupWidget, {
//                product: this,
//                order_line: order_line,
//                order: this,
//            });
        }
	},
	set_product_orderline_price(product) {
	    debugger;
        var self = this;
        var selected_orderline = this.get_selected_orderline();
        var product = product || (selected_orderline ? selected_orderline.get_product() : null);
        if (!this.is_return_order && product && product.grill_service){
            var orderlines = this.get_orderlines();
            //var other_orderlines = _.filter(self.get_orderlines(), function (orderline) {
            //	return (orderline.id !== selected_orderline.id);
            //});
            //var productid_groupedorderlines = this.get_groupedorderlines_by_product_id(other_orderlines);
            var productid_groupedorderlines = this.get_groupedorderlines_by_product_id(orderlines);
            var orderlines_by_currproduct = productid_groupedorderlines[product.id];
            if (orderlines){
                orderlines.forEach(function (orderline) {
                    var product_price = orderline.product.get_price(orderline.order.pricelist, orderline.get_quantity());
                    // Added the condition to set the unit _price for addons , for brekfast module(if more than 3 addons set price for it) so added this customization
                    if (orderline.parent_order_line_id!=null)
                    {
                        var parent_order_line = orderline.order.get_orderline(orderline.parent_order_line_id);
                        if(parent_order_line.product.breakfast){
                            var ss = orderline;

                            var addon =parent_order_line.get_addons();

                            for (var i=0;i<addon.length;i++){

                                if(ss.get_product().id==addon[i].product_tmpl_product_variant_id[0]){
                                    var unit_price=addon[i].product_tmpl_lst_price;
                                    if (i<3){unit_price=0;}
                                    ss.set_unit_price(unit_price);
                                    }

                            }
                        }
                        else{
                            orderline.set_unit_price(product_price);
                        }

                    }
                    else{
                        orderline.set_unit_price(product_price);
                    }
                });
            }
        }
        // Add for Rice
        /*if (product && product.consumable_bom){
            var orderlines = this.get_orderlines();
            //var other_orderlines = _.filter(self.get_orderlines(), function (orderline) {
            //  return (orderline.id !== selected_orderline.id);
            //});
            //var productid_groupedorderlines = this.get_groupedorderlines_by_product_id(other_orderlines);
            var productid_groupedorderlines = this.get_groupedorderlines_by_product_id(orderlines);
            var orderlines_by_currproduct = productid_groupedorderlines[product.id];
            if (orderlines){
                orderlines.forEach(function (orderline) {
                    var product_price = orderline.product.get_price(orderline.order.pricelist, orderline.get_quantity());
                    orderline.set_unit_price(product_price);
                });
            }
        }*/
    },
});

patch(Orderline.prototype, {
    setup() {
        super.setup(...arguments);
        debugger;
        this.set_grill_product(this.product);
        this.grillmethod = this.grillmethod || null;
        this.marinade = this.marinade || null;
        this.kitchennotes = this.kitchennotes || [];
        this.addons = this.addons || [];
        this.parent_addon_id = this.parent_addon_id || null;
        this.addons_order_line_ids = this.addons_order_line_ids || [];
        this.parent_order_line_id = this.parent_order_line_id || null;
        this.pos_grill_method_id = this.pos_grill_method_id || null;
        this.bom_id = this.bom_id || null;
        //this.pos_grill_addon_ids = this.pos_grill_addon_ids || [];
        //this.pos_grill_note_ids = this.pos_grill_note_ids || [];
        this.grill_note = this.grill_note || '';
        this.product_price = this.product_price || null;
        this.grillqty = this.grillqty || null;
        this.grill_nqty = this.grill_nqty || 1;
        this.pos_grill_qty_id = this.pos_grill_qty_id || null;
        this.medium_level = this.medium_level || null;
        /* Fish Name */
        this.fish_id = this.fish_id || null;
//        if (!options.json) {
//            orderline_sequence = orderline_sequence + 10;
//            this.sequence = orderline_sequence;
//        }
    },
    //@override
    clone() {
        const orderline = super.clone(...arguments);
        debugger;
        orderline.grillmethod = this.grillmethod;
        orderline.marinade = this.marinade;
        orderline.addons = this.addons;
        orderline.parent_addon_id = this.parent_addon_id;
        orderline.addons_order_line_ids = this.addons_order_line_ids;
        orderline.parent_order_line_id = this.parent_order_line_id;
        orderline.kitchennotes = this.kitchennotes;
        orderline.pos_grill_method_id = this.pos_grill_method_id;
        orderline.bom_id = this.bom_id;
        //orderline.pos_grill_addon_ids = this.pos_grill_addon_ids;
        //orderline.pos_grill_note_ids = this.pos_grill_note_ids;
        orderline.grill_note = this.grill_note;
        orderline.product_price = this.product_price;
        orderline.grillqty = this.grillqty;
        orderline.grill_nqty = this.grill_nqty;
        orderline.pos_grill_qty_id = this.pos_grill_qty_id;
        orderline.medium_level = this.medium_level;
        /* Fish Name */
        orderline.fish_id = this.fish_id;
        return orderline;
    },
    //@override
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        debugger;
        json.grillmethod = this.grillmethod;
        json.marinade = this.marinade;
        json.addons = this.addons;
        json.parent_addon_id = this.parent_addon_id;
        json.addons_order_line_ids = this.addons_order_line_ids;
        json.parent_order_line_id = this.parent_order_line_id;
        json.kitchennotes = this.kitchennotes;
        json.grill_note = this.grill_note;
        json.pos_grill_method_id = this.pos_grill_method_id;
        json.bom_id = this.bom_id;
        //json.pos_grill_addon_ids = this.pos_grill_addon_ids;
        //json.pos_grill_note_ids = this.pos_grill_note_ids;
        //To Do : Replace me
        /*var len = this.pos_grill_note_ids.length;
        var grillnote_ids;
        if (this.pos_grill_note_ids && len > 2){
            if (Array.isArray(this.pos_grill_note_ids[2])){
                grillnote_ids = this.pos_grill_note_ids[2];
            }
        }
        if (!grillnote_ids){
            grillnote_ids = this.pos_grill_note_ids;
        }
        json.pos_grill_note_ids = [[6, false, grillnote_ids]];*/
        //json.pos_grill_note_ids = [];
        //To Do : Replace me
        /*var len = this.pos_grill_note_ids.length;
        var grillnote_ids;
        if (this.pos_grill_note_ids && len > 2){
            if (Array.isArray(this.pos_grill_note_ids[2])){
                grillnote_ids = this.pos_grill_note_ids[2];
            }
        }
        if (!grillnote_ids){
            grillnote_ids = this.pos_grill_note_ids;
        }*/
        //json.pos_grill_note_ids = [[6, false, grillnote_ids]];
        json.pos_grill_addon_ids = [[6, false, this.get_pos_grill_addon_ids()]];
        json.pos_grill_note_ids = [[6, false, this.get_pos_grill_note_ids()]];
        json.product_price = this.product_price;
        json.grillqty = this.grillqty;
        json.grill_nqty = this.grill_nqty;
        json.pos_grill_qty_id = this.pos_grill_qty_id;
        json.medium_level = this.medium_level;
        /* Fish Name */
        json.fish_id = this.fish_id;
        json.sequence = this.sequence;
        return json;
    },
    //@override
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        debugger;
        this.set_grill_product(this.product);
        this.grillmethod = json.grillmethod;
        this.marinade = json.marinade;
        this.addons = json.addons;
        this.parent_addon_id = json.parent_addon_id;
        this.addons_order_line_ids = json.addons_order_line_ids;
        this.parent_order_line_id = json.parent_order_line_id;
        this.kitchennotes = json.kitchennotes;
        this.pos_grill_method_id = json.pos_grill_method_id;
        this.bom_id = json.bom_id;
        //this.pos_grill_addon_ids = json.pos_grill_addon_ids;
        //this.pos_grill_note_ids = json.pos_grill_note_ids;
        this.grill_note = json.grill_note;
        this.product_price = json.product_price;
        this.grillqty = json.grillqty;
        this.grill_nqty = json.grill_nqty;
        this.pos_grill_qty_id = json.pos_grill_qty_id;
        this.medium_level = json.medium_level;
        /* Fish Name */
        this.fish_id = json.fish_id;
        this.sequence = json.sequence;
        orderline_sequence = Math.max(this.sequence+10,orderline_sequence);
    },
    set_product_price(product_price){
        this.order.assert_editable();
        this.product_price = product_price;
	    },
    get_product_price(){
        return this.product_price;
    },
    set_sequence(sequence){
        this.order.assert_editable();
        this.sequence = sequence;
        this.trigger('change',this);
    },
    get_sequence(){
        return this.sequence;
    },
    set_grill_product(product){
        this.is_grill_service = product.grill_service || false;
        this.is_consumable_bom = product.consumable_bom || false;
        this.is_ready_to_eat = product.ready_to_eat || false;
        this.is_breakfast = product.breakfast || false;
        var bom_ids = product.bom_ids;
        if (bom_ids) {
            for(var i = 0, len = bom_ids.length; i < len; i++){
                this.bom_id = bom_ids[i];
            }
        }
    },
    click_grill_icon(){
        this.trigger('click_grillorder',this);
    },
    set_grillmethod(grillmethod){
        this.order.assert_editable();
        this.grillmethod = grillmethod;
        this.pos_grill_method_id = grillmethod ? grillmethod.id : null;
        this.trigger('change',this);
    },
    get_medium_level:function(){
        return this.medium_level || '';
    },
    set_medium_level:function(medium_level){
        this.medium_level =medium_level;
    },
    get_grillmethod(){
        return this.grillmethod;
    },
    set_marinade(marinade){
        this.order.assert_editable();
        this.marinade = marinade;
        this.bom_id = marinade ? marinade.id : null;
        this.trigger('change',this);
    },
    get_marinade(){
        return this.marinade;
    },
    set_addons(addon,order_line){
        this.order.assert_editable();
        if (addon){
            var pos_grill_addon_id = addon ? addon.id : null;
            //this.pos_grill_addon_ids.push(pos_grill_addon_id);
            if (this.pos.config.enable_orderline_addons){
                var addons_order_line = this.order.get_addons_order_line_by_parent_ids(this.id, pos_grill_addon_id);
                var quantity = this.get_quantity();
                if (addons_order_line){
                    addons_order_line.set_quantity(quantity);
                }else{
                    var product_tmpl_id = addon.product_tmpl_id[0];
                    var product_id = addon.product_tmpl_product_variant_id[0];
                    var product = this.pos.db.get_product_by_tmpl_id(product_tmpl_id);
                    var product = this.pos.db.get_product_by_id(product_id);
                    if (!product) {
                        return false;
                    }
                    var price =addon.product_tmpl_lst_price;
                     if(order_line.product.breakfast){
                           var add_len= order_line.get_addons().length;
                           if(add_len<3){
                                price=0;
                           }

                        }

                    this.order.add_product(product, {quantity:quantity, merge:false,price:price});
                    var selected_orderline = this.order.get_selected_orderline();
                    if (selected_orderline && pos_grill_addon_id){
                        var selected_orderline_sequence = this.get_sequence();
                        selected_orderline_sequence += 1;
                        selected_orderline.set_sequence(selected_orderline_sequence);
                        this.set_addons_order_line_id(selected_orderline.id, pos_grill_addon_id);
                    }
                    this.order.select_orderline(this);
                }
            }
            this.addons.push(addon);
            this.trigger('change',this);
        }
    },
    remove_addons(addon){
        this.order.assert_editable();
        if (addon){
            var matched = _.find(this.addons, function (ad) { return ad.id == addon.id; });
            var pos_grill_addon_id = addon ? addon.id : null;
            var addons_order_line = this.order.get_addons_order_line_by_parent_ids(this.id, pos_grill_addon_id);
            if (this.pos.config.enable_orderline_addons && addons_order_line){
                var matched_addons_order_line_id = _.find(this.addons_order_line_ids, function (addons_order_line_id) { return addons_order_line_id == addons_order_line.id; });
                this.addons_order_line_ids = _.without(this.addons_order_line_ids, matched_addons_order_line_id);

                this.order.remove_orderline(addons_order_line);
                this.order.select_orderline(this);


                //addons_order_line.trigger('remove',addons_order_line);
                //addons_order_line.set_quantity('remove');
                //this.order.trigger('change');
            }
            this.addons = _.without(this.addons, matched);

            this.trigger('change',this);
        }
    },
    delete_addons(){
        var self = this;
        this.order.assert_editable();
        _.each(this.addons, function(addon) {
            self.remove_addons(addon);
        });
        this.addons = [];
        //var pos_grill_addon_id = null;
        //this.pos_grill_addon_ids = [];
        this.trigger('change',this);
    },
    get_addons(){
        return this.addons || [];
    },
    get_addon_filling_heading(){
        return this.is_breakfast ? 'Fillings :':'Addons :';
    },
    get_addons_price(){
        var addons = this.get_addons();
        var addons_price = 0;
        for (var i = 0; i < addons.length; i++) {
            if (addons[i]){
                addons_price += addons[i].product_tmpl_lst_price || 0.0;
            }
        }
        return addons_price;
    },
    check_addons(addon){
        var matched = _.find(this.addons, function (ad) { return ad.id == addon.id; });
        return matched;
    },
    get_addons_by_id(addon_id){
        var matched = _.find(this.addons, function (ad) { return ad.id == addon_id; });
        return matched;
    },
    set_addons_order_line_id(addons_order_line_id, addon_id){
        this.order.assert_editable();
        this.addons_order_line_ids.push(addons_order_line_id);
        var addons_order_line = this.order.get_orderline(addons_order_line_id);
        addons_order_line.set_parent_order_line_id(this.id);
        addons_order_line.set_parent_addon_id(addon_id);
    },
    get_addons_order_line_ids(){
        return this.addons_order_line_ids;
    },
    get_addons_order_lines(){
        var addons_order_lines = [];
        var addons_order_line_ids = this.get_addons_order_line_ids() || [];
        for (var i = 0; i < addons_order_line_ids.length; i++) {
            var addons_order_line_id = this.addons_order_line_ids[i];
            if (addons_order_line_id){
                var addons_order_line = this.order.get_orderline(addons_order_line_id);
                addons_order_lines.push(addons_order_line);
            }
        }
        return addons_order_lines;
    },
    set_parent_order_line_id(parent_order_line_id){
        this.order.assert_editable();
        this.parent_order_line_id = parent_order_line_id;
        //this.trigger('change',this);
    },
    get_parent_order_line_id(){
        return this.parent_order_line_id;
    },
    get_parent_order_line(){
        var parent_order_line = this.order.get_orderline(this.parent_order_line_id);
        return parent_order_line;
    },
    set_parent_addon_id(parent_addon_id){
        this.order.assert_editable();
        this.parent_addon_id = parent_addon_id;
        //this.trigger('change',this);
    },
    get_parent_addon_id(){
        return this.parent_addon_id;
    },
    set_kitchennotes(kitchennote){
        this.order.assert_editable();
        this.kitchennotes.push(kitchennote);
        var pos_grill_note_id = kitchennote ? kitchennote.id : null;
        //this.pos_grill_note_ids.push(pos_grill_note_id);
        this.trigger('change',this);
    },
    remove_kitchennotes(kitchennote){
        this.order.assert_editable();
        //this.kitchennotes = this.kitchennotes.filter(item => item !== kitchennote);
        var matched = _.find(this.kitchennotes, function (kn) { return kn.id == kitchennote.id; });
        //var matched = _.findWhere(this.kitchennotes, {id: kitchennote.id});
        this.kitchennotes = _.without(this.kitchennotes, matched);

        var pos_grill_note_id = kitchennote ? kitchennote.id : null;
        //this.pos_grill_note_ids = this.pos_grill_note_ids.filter(item => item !== pos_grill_note_id);
        //rmatched = _.find(this.pos_grill_note_ids, function (gr_note_id) { return gr_note_id == pos_grill_note_id; });
        //rthis.pos_grill_note_ids = _.without(this.pos_grill_note_ids, matched);
        this.trigger('change',this);
    },
    delete_kitchennotes(){
        this.order.assert_editable();
        this.kitchennotes = [];
        //var pos_grill_note_id = null;
        this.kitchennotes = [];
        //this.pos_grill_note_ids = [];
        this.trigger('change',this);
    },
    get_kitchennotes(){
        return this.kitchennotes;
    },
    check_kitchennotes(kitchennote){
        var matched = _.find(this.kitchennotes, function (kn) { return kn.id == kitchennote.id; });
        return matched;
        /*if (_.contains(this.kitchennotes, kitchennote)){
            return kitchennote;
        }
        return null;*/
    },
    set_grillnote(grill_note){
        this.order.assert_editable();
        this.grill_note = grill_note;
        this.trigger('change',this);
    },
    get_grillnote(){
        return this.grill_note;
    },
    set_grillqty(grillqty){
        debugger;
        this.order.assert_editable();
        this.grillqty = grillqty;
        this.pos_grill_qty_id = grillqty ? grillqty.id : null;
        var grill_nqty = this.get_grillnqty();
        var qty_grill = grillqty ? grillqty.qty : 0;
        var qty = grill_nqty * qty_grill;
        //this.set_quantity(qty);
        this.trigger('change',this);
        if (grillqty){
            this.set_unit_price(this.grillqty.price);
        }
    },
    get_grillqty(){
        return this.grillqty;
    },
    set_grillnqty(grill_nqty){
        this.order.assert_editable();
        this.grill_nqty = grill_nqty || 1;
        var grillqty = this.get_grillqty();
        var qty_grill = grillqty ? grillqty.qty : 0;
        var qty = grill_nqty * qty_grill;
        //this.set_quantity(qty);
        this.trigger('change',this);
    },
    get_grillnqty(){
        return this.grill_nqty;
    },
//    set_unit_price(price, keep_price){
//        var self = this;
//        var product = this.get_product();
//        var min_qty = product.grill_min_qty;
//        var qty = this.get_quantity();
//        var qty_groupedproduct = qty;
//        var order = this.order;
//        var orderlines = order.get_orderlines();
//        var productid_groupedorderlines = {};
//        //var other_orderlines = _.filter(order.get_orderlines(), function (orderline) {
//        //	return (orderline.id !== self.id);
//        //});
//        if (orderlines){
//            //productid_groupedorderlines = order.get_groupedorderlines_by_product_id(other_orderlines);
//            //qty_groupedproduct += order.get_qty_groupedproduct(product, productid_groupedorderlines);
//            var productid_groupedorderlines = order.get_groupedorderlines_by_product_id(orderlines);
//            qty_groupedproduct = order.get_qty_groupedproduct(product, productid_groupedorderlines);
//        }
//        var grill_price_lines = product.pos_grill_price_id ? this.pos.db.get_price_lines_by_grill_price_id(product.pos_grill_price_id[0]) : [];
//        if (order.is_return_order){
//            _super_orderline.set_unit_price.apply(this, arguments);
//        } else if(! keep_price && product.grill_service && qty_groupedproduct && grill_price_lines){
//            var product_price = this.product.get_price(this.order.pricelist, this.get_quantity());
//            var min_price = parseFloat(product_price);
//            for(var i = 0, len = grill_price_lines.length; i < len; i++){
//                if (qty_groupedproduct > parseFloat(grill_price_lines[i].from_qty) && qty_groupedproduct <= parseFloat(grill_price_lines[i].to_qty)) {
//                    if (!grill_price_lines[i].use_product_price){
//                        min_price = parseFloat(grill_price_lines[i].price);
//                    }
//                    min_price = parseFloat(min_price) / parseFloat(qty_groupedproduct);
//                    break;
//                }
//                else if (grill_price_lines[i].to_qty === 0.0 && qty_groupedproduct > grill_price_lines[i].from_qty) {
//                    if (!grill_price_lines[i].use_product_price){
//                        min_price = parseFloat(grill_price_lines[i].price);
//                    }
//                    break;
//                }
//                /*else if (grill_price_lines[i].from_qty === 0.0 && qty_groupedproduct <= grill_price_lines[i].to_qty) {
//                    if (!grill_price_lines[i].use_product_price){
//                        min_price = parseFloat(grill_price_lines[i].price);
//                    }
//                    break;
//                } */
//            }
//            this.set_unit_price(min_price, 'do not recompute min price');
//        } else if(! keep_price && product.consumable_bom){
//            var min_price = this.grillqty ? this.grillqty.price : parseFloat(price);
//            this.set_unit_price(min_price, 'do not recompute min price');
//        }
//        else{
//            var parent_order_line =false;
//             if(this.parent_order_line_id!=null){
//                parent_order_line = this.order.get_orderline(this.parent_order_line_id);
//
//            }
//            if (parent_order_line && parent_order_line.get_product().breakfast)
//            {
//                this.set_product_price(price);
//            }
//            else{
//                var product_price = this.product.get_price(this.order.pricelist, this.get_quantity());
//                this.set_product_price(product_price);
//                if (!this.pos.config.enable_orderline_addons){
//                    var addons_price = this.get_addons_price();
//                    price += addons_price;
//                }
//                //_super_orderline.set_unit_price.apply(this, arguments);
//                _super_orderline.set_unit_price.call(this, price, keep_price);
//            }
//        }
//    },
    get_pos_grill_addon_ids(){
        var pos_grill_addon_ids = [];
        for (var i = 0; i < this.addons.length; i++) {
            if (this.addons[i]){
                pos_grill_addon_ids.push(this.addons[i].id);
            }
        }
        return pos_grill_addon_ids;
    },
    get_pos_grill_note_ids(){
        var pos_grill_note_ids = [];
        for (var i = 0; i < this.kitchennotes.length; i++) {
            if (this.kitchennotes[i]){
                pos_grill_note_ids.push(this.kitchennotes[i].id);
            }
        }
        return pos_grill_note_ids;
    },
    /* Fish Name */

    set_fishname(fish_id){
        this.order.assert_editable();
        this.fish_id = fish_id;
        this.trigger('change',this);
    },
    get_fishname(){
        var fishname = this.pos.db.get_pos_grill_fish_by_id(this.fish_id);
        return fishname;
    },
    set_quantity(quantity, keep_price){
        this.order.assert_editable();
        var addons_order_lines = this.get_addons_order_lines();
        if (addons_order_lines.length){
            addons_order_lines.forEach(addonsOrderLine => {
                if (addons_order_line,length){
                    addons_order_line.set_quantity(quantity, keep_price);
                }
            });
        }
//        _super_orderline.set_quantity.call(this, quantity, keep_price);
    },
    get_line_class(){
            var classname = 'orderline ';
            if (this.selected){
                classname += ' selected';
            }
            if (this.parent_order_line_id){
                classname += ' parent_orderline';
            }
            return classname;
        },
});

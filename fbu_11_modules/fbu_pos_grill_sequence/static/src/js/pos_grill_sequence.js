odoo.define('pos_grill_sequence.pos_grill_sequence', function(require) {
    "use strict";
    var exports = {}
    var models = require('point_of_sale.models');
    var pos_db = require('point_of_sale.DB');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var utils = require('web.utils');
    var field_utils = require('web.field_utils');
    var rpc = require('web.rpc');
    var round_di = utils.round_decimals;
    var gui = require('point_of_sale.gui');
    var round_pr = utils.round_precision;
    var time = require('web.time');
    var QWeb = core.qweb;
    var SuperPosModel = models.PosModel.prototype;
	var SuperOrder = models.Order.prototype;

    var _t = core._t;
    

    var pop_error_type = 406;
    var pop_error_data = {'exception_type': 'validation', 'title': '', 'message': '', 'debug': ''};
    var pop_err = {'code': pop_error_type, 'data': pop_error_data};
    var local_grill_sequence_number = 100;
    var local_grill_offline_number = 1;

    models.load_fields('pos.session', ['pos_grill_seq_id', 'grill_session']);
    models.load_models([
        {
            model: 'pos.session',
            fields: ['grill_offline_number', 'grill_label'],
            domain: function(self){ return [['id','=', self.pos_session.id]]; },
            loaded: function(self,pos_sessions){
            	var grill_offline_number = pos_sessions[0].grill_offline_number;
            	//var grill_offline_number = pos_sessions[0].grill_offline_number.replace(/\d+/g).map(Number);
            	self.pos_session.grill_offline_number = Math.max(grill_offline_number, local_grill_offline_number);
            	self.pos_session.grill_label = pos_sessions[0].grill_label;
            },
        }
    ], {
        'after': 'pos.config'
    });
    
    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        generate_grill_sequence: function(options){
            var self = this;
            var def = new $.Deferred();
            options = options || {};
            //options['show_error'] = true;
            var timeout = typeof options.timeout === 'number' ? options.timeout : 7500 * 12; 
            var def = new $.Deferred();
            var pos_grill_seq_id = this.pos_session.pos_grill_seq_id ? this.pos_session.pos_grill_seq_id[0] : 0;
            var context = this.pos_session.user_context || {};
            var order = this.get_order(); 
        	var sequence_number_next = 0;  
        	var pos_session_id = this.pos_session.id;
        	var params = {'grill_offline_number': local_grill_offline_number, 'pos_session_id': pos_session_id};
        	debugger;
            rpc.query({
                model: 'pos.grill.seq',
                method: 'get_grill_sequence',
                args: [pos_grill_seq_id],
                kwargs: {params:params, context: context},
            }, {
                timeout: timeout,
                shadow: true,
                async: false,
            }).done(function(pos_grill_seq){
                if (Array.isArray(pos_grill_seq) && pos_grill_seq.length){
                    pos_grill_seq.forEach(function(grill_seq){
                    	sequence_number_next = grill_seq.sequence_number_next
                        order.set_grill_sequence_number(sequence_number_next);                    	
                        def.resolve();
                    });
            	}else{
                    var grill_offline_number = Math.max(order.grill_offline_number, self.pos_session.grill_offline_number);
                    grill_offline_number++;
                    self.pos_session.grill_offline_number = grill_offline_number;
                    local_grill_offline_number = grill_offline_number
                	order.set_grill_sequence_number(grill_offline_number); 
	        		pop_error_data['title'] = _("Sequence Ref!");
	        		pop_error_data['message'] = _("Gill Sequence Ref Cannot Found!");
		        	def.reject(pop_error_type, pop_err);
            	}
            }).fail(function (type, error){
        		pop_error_data['title'] = _("Sequence Ref!");
        		pop_error_data['message'] = _t('Your network connection is probably down.');
        		pop_error_data['debug'] = error;
                var except = error.data;
                var error_body;
                if (except){
                	error_body = except.arguments && except.arguments[0] || except.message || error_body;                    	
                }
                if (error) {
                    console.log(error);
                }
                if(error.code === 200 ){    
                    if (error.data.exception_type == 'warning') {
                        delete error.data.debug;
                    }
                    if (options.show_error) {
                        self.gui.show_popup('error-traceback',{
                            'title': error.data.message,
                            'body':  error.data.debug
                        });
                    }
                }
                var grill_offline_number = Math.max(order.grill_offline_number, self.pos_session.grill_offline_number);
                grill_offline_number++;
                self.pos_session.grill_offline_number = grill_offline_number;
                local_grill_offline_number = grill_offline_number
                var grill_label = self.pos_session.grill_label
            	order.set_grill_sequence_number(grill_label + grill_offline_number);
	        	def.reject(pop_error_type, pop_err);
            });
            return def;
        },
    });
    
    
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attr, options) {
			var self = this;        	
        	//_super_order.initialize.call(this,attr,options);
            this.grill_sequence_number = local_grill_sequence_number;
            this.grill_offline_number = options.pos.pos_session.grill_offline_number;
            this.grill_session = options.pos.pos_session.grill_session;            
            return _super_order.initialize.call(this, attr, options);
        },
        set_grill_sequence_number: function (grill_sequence_number) {
        	this.grill_sequence_number = grill_sequence_number;
        	local_grill_sequence_number = grill_sequence_number;
        	
        },
        get_grill_sequence_number: function () {
            return this.grill_sequence_number;
        },
        init_from_JSON: function(json){
            //_super_order.init_from_JSON.apply(this, arguments);
            this.grill_sequence_number = json.grill_sequence_number;
            this.grill_offline_number = json.grill_offline_number;
            this.pos.pos_session.grill_offline_number = Math.max(this.grill_offline_number, this.pos.pos_session.grill_offline_number);
            this.grill_session = json.grill_session;
            local_grill_offline_number = Math.max(this.pos.pos_session.grill_offline_number, local_grill_offline_number);
            _super_order.init_from_JSON.call(this, json);

        },
        export_as_JSON: function(){
            var json = _super_order.export_as_JSON.call(this);
            json.grill_sequence_number = this.grill_sequence_number;
            json.grill_offline_number = this.grill_offline_number;
            json.grill_session = this.pos.pos_session.grill_session;
            return json;
        },
        export_for_printing: function(){
            debugger;
            var json = SuperOrder.export_for_printing.apply(this, arguments);
            json['grill_sequence_number'] = this.get_grill_sequence_number();
            return json;
        },
        print_grill_kot: function(){
            var self = this;
            var printers = this.pos.printers;
            var receipt = QWeb.render('NetworkPrinterGrillKOT',{order:this});
            printers.forEach(function(printer){
                printer.print(receipt);
            })

        },
        format_currency_no_symbol: function(amount, precision) {
        var currency = (this.pos && this.pos.currency) ? this.pos.currency : {symbol:'$', position: 'after', rounding: 0.01, decimals: 2};
        var decimals = currency.decimals;

        if (precision && this.pos.dp[precision] !== undefined) {
            decimals = this.pos.dp[precision];
        }

        if (typeof amount === 'number') {
            amount = round_di(amount,decimals).toFixed(decimals);
            amount = field_utils.format.float(round_di(amount, decimals), {digits: [69, decimals]});
        }

        return amount;
    },
	});

    screens.PaymentScreenWidget.include({
        finalize_validation: function() {
            var self = this;
            var order = this.pos.get_order();
            if (this.pos.config.module_pos_grill) {
            	var sequence_number_next = 0;
	            this.pos.generate_grill_sequence().done(function () {
	            	//sequence_number_next = order.get_grill_sequence_number(); 
	                self._super();
	                if (self.pos.config.company_id[0] === 3){
	                    order.print_grill_kot(); // added for printing KOT in kitchen while validating the order coded for hamriyah branch Grill
	                }
	            }).fail(function (type, error){
	            	console.log(error);
	            	//sequence_number_next = order.get_grill_sequence_number(); 
	                /*self.pos.gui.show_popup('error',{
	                    'title': error.data.title,
	                    'body': error.data.message,
	                    'message':  error.data.message,
	                    'debug':  error.data.debug,
	                });*/ 
	            	self._super();               
	            }); 
            }else{
            	self._super(); 
            }          
        }
    });

    return exports;

});

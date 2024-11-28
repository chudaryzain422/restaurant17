odoo.define('pos_counter.pos_counter', function (require) {
"use strict";

	var models = require('point_of_sale.models');
	var core = require('web.core');
	
	var _t = core._t;
	
	models.load_fields('pos.session', ['pos_counter_id', 'pos_counter_name']);
    models.load_models([
        {
            model: 'pos.counter',
            fields: [],
            domain: function(self){ return [['id','=', self.pos_session.pos_counter_id ? self.pos_session.pos_counter_id[0] : 0]]; },
            loaded: function(self,pos_counter){
            	self.pos_session.pos_counter = pos_counter[0];
            },
        }
    ], {
        'after': 'pos.session'
    });


});
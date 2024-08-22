/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { FloorScreen } from "@pos_restaurant/app/floor_screen/floor_screen";
import { jsonrpc } from "@web/core/network/rpc_service";
patch(FloorScreen.prototype, {
    setup() {
        super.setup(...arguments);
    },
    /**
    For payment validation in pos
    **/
    get activeTables() {
        var self = this
        debugger;
        jsonrpc('/active/floor/tables', {'floor_id' : self.activeFloor.id,
        }).then( function(data){
            debugger;
            self.tables = data
        });
        let reserved_tables = []
        for(let rec in self.tables){
            let new_tables = self.activeFloor.tables.find(item => item['id'] == self.tables[rec])
            if (new_tables){
                debugger;
                reserved_tables.push(new_tables)
            }
        }
        debugger;
        reserved_tables.forEach(function(record){
            debugger;
            record.reserved = true;
        });
        return self.activeFloor ? self.activeFloor.tables : null;
    }
});

/** @odoo-module **/
import { registry } from "@web/core/registry";
import { onWillStart, onMounted, useState, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
const actionRegistry = registry.category("actions");
import { _t } from "@web/core/l10n/translation";
const { DateTime } = luxon;
var op_type;
/* This class represents dashboard in Inventory. */
class SalesDashboard extends owl.Component{
    setup() {
        this.orm = useService('orm')
        this.rootRef = useRef('root')
        this.state = useState({

            year_sales:[],
            year_sales_count:[],
        });
        // When the component is about to start, fetch data in tiles
        onWillStart(async () => {
            this.props.title = 'SalesDashboard';
        });
        // When the component is mounted, render various charts
        onMounted(async () => {
            await this.render_graphs();
        });
    }
    render_graphs(){

        this.render_year_sales_graph();
    }



    render_year_sales_graph(){
        this.orm.call("sales.yearly.report", "get_details",[]
        ).then( (result) => {
            if (result) { alert("ioio");alert(JSON.stringify(result));
            result = result[0];
                this.rootRef.el.querySelector("#year_sales_table").style.display = 'block';
                var ctx = this.rootRef.el.querySelector("#year_sales_move_graph");
                var gctx = this.rootRef.el.querySelector("#year_sales_move_graph_growth");

                var name = result.year
                var count = result.previous_year_sales
                var total_sales = result.total_sales
                var growth_rate = result.growth_rate
                var count = result.previous_year_sales
                var cagr_value = result.cagr_value
                var cagr_period = result.cagr_period
                var cagr_per = result.cagr_per
                alert("count");
                alert(count);
                this.state.year_sales = name
                this.state.year_sales_count = count
                this.rootRef.el.querySelector('#year_sales_table').style.display = 'none';
                var myChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: name,
                        datasets: [{
                            label: 'Current Sales',
                            data: total_sales,
                            backgroundColor: '#003f5c',
                            borderColor: '#003f5c',
                            barPercentage: 0.5,
                            barThickness: 6,
                            maxBarThickness: 8,
                            minBarLength: 0,
                            borderWidth: 1,
                            type: 'bar',
                            fill: false
                        },
//                        {
//                            label: 'growth',
//                            data: growth_rate,
//                            backgroundColor: '#ff5733',
//                            borderColor: '#ff5733',
//                            barPercentage: 0.5,
//                            barThickness: 6,
//                            maxBarThickness: 8,
//                            minBarLength: 0,
//                            borderWidth: 1,
//                            type: 'line',
//
//                        },
                        {
                            label: 'previous sales',
                            data: count,
                            backgroundColor: '#33ff36',
                            borderColor: '#33ff36',
                            type: 'bar',

                        },
                        ]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            },
                        },
                        responsive: true,
                        maintainAspectRatio: false,
                    }
                });

                var grwothmyChart = new Chart(gctx, {
                    type: 'line',
                    data: {
                        labels: name,
                        datasets: [{
                            label: 'Growth',
                            data: growth_rate,
                            backgroundColor: '#003f5c',
                            borderColor: '#003f5c',
                            barPercentage: 0.5,
                            barThickness: 6,
                            maxBarThickness: 8,
                            minBarLength: 0,
                            borderWidth: 1,
                            type: 'line',
                            fill: false
                        }

                        ]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            },
                        },
                        responsive: true,
                        maintainAspectRatio: false,
                    }
                });

                $('#cgcar_info').replaceWith($('<div id="cgcar_info" class="card blue-card"><h2>CAGR'+cagr_period+'</h2><p>'+cagr_per+' %
                </p> </div>'))
            }
            else{
                this.rootRef.el.querySelector('#year_sales_table').style.display = 'none';
            }
        });
    }


}
SalesDashboard.template = "SalesDashboard";
actionRegistry.add('sales_dashboard_tag', SalesDashboard);

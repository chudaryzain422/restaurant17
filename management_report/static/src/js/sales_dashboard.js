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

    convertToKandM(value){

        if (value >= 1000000) {
            return (value / 1000000).toFixed(2) + ' M'; // Convert to millions
        } else if (value >= 1000) {
            return (value / 1000).toFixed(2) + ' K'; // Convert to thousands
        } else {
            return parseFloat(value).toFixed(2); // Return the value if less than 1000
        }
    }



    render_year_sales_graph(){
    var self=this;


        this.orm.call("sale.order", "get_details",[]
        ).then( (result) => {
        alert(result);
        console.log(result);

//this.rootRef.el.querySelector("#year_sales_move_graph")
            var SalesData= result['result'];
            var total_sales= result['total_sales'];
            var total_cost_price= result['total_cost_price'];
            var total_sales_qty= result['total_sales_qty'];
            var prediction_months= result['prediction_result'];
             const g_year = [...new Set(SalesData.map(item => item.year))];
        const g_months = [...new Set(SalesData.map(item => item.month))];

        const grossProfitData_t = g_year.map(cat => ({
            label: cat,
            data: g_months.map(month => {
                const monthData = SalesData.filter(item => (item.month) === month);
                return monthData.reduce((sum, entry) => sum + entry.total_sales, 0);
//                return entry ? entry.gross_profit : 0;
            }),
            backgroundColor: '#' + Math.floor(Math.random()*16777215).toString(16)  // Random color
        }));
        const predict_chart = {
            labels: 'predicted sales',
            datasets: [{
                 label:prediction_months.map(holiday => holiday.month),
                data: prediction_months.map(holiday => holiday.data),
                backgroundColor: ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0'],
                hoverBackgroundColor: ['#ff6666', '#3399ff', '#66ff66', '#ff9966', '#9999ff']
            }]
        };

//        const total_sales= this.$('#kpi_total-sales');
//      const total_profit= this.$('#kpi_total-gross-profit');
//      const total_qtysales= this.$('#kpi_total-quantity-sold');
//      const cost_value= this.$('#kpi_cost-value');

      let amount = total_sales.toFixed(2);
        let profit_amount = total_sales_qty;
        let cost_amount = total_cost_price.toFixed(2);
        let words = this.convertToKandM(amount);
        let cost_amount_words = this.convertToKandM(cost_amount);
        this.rootRef.el.querySelector('#total-sales').textContent = `${words}`;
        this.rootRef.el.querySelector('#total-qtysales').textContent = profit_amount;
//        this.rootRef.el.querySelector('total-profit').textContent = `${profit_amount_words}(AED)`;
        this.rootRef.el.querySelector('#cost-value').textContent = `${cost_amount_words}(AED)`;

        const monthly_trendnig_sales =this.rootRef.el.querySelector('#monthly_trendnig_sales');

//         const grossProfitData_t = g_categories.map(cat => ({
//            label: cat,
//            data: g_months.map(month => {
//                const monthData = SalesData.filter(item => (item.month) === month && item.sale_category === cat);
//                return monthData.reduce((sum, entry) => sum + entry.gross_profit, 0);
////                return entry ? entry.gross_profit : 0;
//            }),
//            backgroundColor: '#' + Math.floor(Math.random()*16777215).toString(16)  // Random color
//        }));


         new Chart(monthly_trendnig_sales, {
            type: 'bar',
          data: predict_chart,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right',
                    },
                    title: {
                        display: true,
                        text: 'Sales Prediction for next month '
                    }
                },
            }
        });


//           const monthly_sales_chart = g_months.map(cat => ({
//            label: cat,
//            data: g_months.map(month => {
//
//                const monthData = SalesData.filter(item => (item.month) === month);
//                return monthData.reduce((sum, entry) => sum + entry.total_sales, 0);
//            }),
//            backgroundColor: '#' + Math.floor(Math.random()*16777215).toString(16)  // Random color
//        }));
//        this.rootRef.el.querySelector('#overviewsales');

//        this.rootRef.el.querySelector('#overviewsales').replaceWith($('<canvas id="overviewsales" width="500" height="500"></canvas>'));
var ctx2= this.rootRef.el.querySelector('#overviewsales');
var grwothmyChart = new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: g_months,
                datasets: grossProfitData_t
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Monthly Sales Report'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Sales'
                        }
                    }
                }
            }
        });

//            if (result) {
//
//
//            alert("ioio");alert(JSON.stringify(result));
//            result = result[0];
//                this.rootRef.el.querySelector("#year_sales_table").style.display = 'block';
//                var ctx = this.rootRef.el.querySelector("#year_sales_move_graph");
//                var gctx = this.rootRef.el.querySelector("#year_sales_move_graph_growth");
//
//                var name = result.year
//                var count = result.previous_year_sales
//                var total_sales = result.total_sales
//                var growth_rate = result.growth_rate
//                var count = result.previous_year_sales
//                var cagr_value = result.cagr_value
//                var cagr_period = result.cagr_period
//                var cagr_per = result.cagr_per
//                alert("count");
//                alert(count);
//                this.state.year_sales = name
//                this.state.year_sales_count = count
//                this.rootRef.el.querySelector('#year_sales_table').style.display = 'none';
//                var myChart = new Chart(ctx, {
//                    type: 'line',
//                    data: {
//                        labels: name,
//                        datasets: [{
//                            label: 'Current Sales',
//                            data: total_sales,
//                            backgroundColor: '#003f5c',
//                            borderColor: '#003f5c',
//                            barPercentage: 0.5,
//                            barThickness: 6,
//                            maxBarThickness: 8,
//                            minBarLength: 0,
//                            borderWidth: 1,
//                            type: 'bar',
//                            fill: false
//                        },
////                        {
////                            label: 'growth',
////                            data: growth_rate,
////                            backgroundColor: '#ff5733',
////                            borderColor: '#ff5733',
////                            barPercentage: 0.5,
////                            barThickness: 6,
////                            maxBarThickness: 8,
////                            minBarLength: 0,
////                            borderWidth: 1,
////                            type: 'line',
////
////                        },
//                        {
//                            label: 'previous sales',
//                            data: count,
//                            backgroundColor: '#33ff36',
//                            borderColor: '#33ff36',
//                            type: 'bar',
//
//                        },
//                        ]
//                    },
//                    options: {
//                        scales: {
//                            y: {
//                                beginAtZero: true
//                            },
//                        },
//                        responsive: true,
//                        maintainAspectRatio: false,
//                    }
//                });
//
//                var grwothmyChart = new Chart(gctx, {
//                    type: 'line',
//                    data: {
//                        labels: name,
//                        datasets: [{
//                            label: 'Growth',
//                            data: growth_rate,
//                            backgroundColor: '#003f5c',
//                            borderColor: '#003f5c',
//                            barPercentage: 0.5,
//                            barThickness: 6,
//                            maxBarThickness: 8,
//                            minBarLength: 0,
//                            borderWidth: 1,
//                            type: 'line',
//                            fill: false
//                        }
//
//                        ]
//                    },
//                    options: {
//                        scales: {
//                            y: {
//                                beginAtZero: true
//                            },
//                        },
//                        responsive: true,
//                        maintainAspectRatio: false,
//                    }
//                });
//
//                $('#cgcar_info').replaceWith($('<div id="cgcar_info" class="card blue-card"><h2>CAGR'+cagr_period+'</h2><p>'+cagr_per+' %
//                </p> </div>'))
//            }
//            else{
//                this.rootRef.el.querySelector('#year_sales_table').style.display = 'none';
//            }
        });
    }


}
SalesDashboard.template = "SalesDashboard";
actionRegistry.add('sales_dashboard_tag', SalesDashboard);

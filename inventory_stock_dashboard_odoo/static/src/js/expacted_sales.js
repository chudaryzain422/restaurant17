/** @odoo-module **/
import { registry } from "@web/core/registry";
import { onWillStart, onMounted, useState, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
const actionRegistry = registry.category("actions");
import { _t } from "@web/core/l10n/translation";
const { DateTime } = luxon;

class ExpectedSalesDashboard extends owl.Component {
    setup() {
        this.orm = useService('orm');
        this.rootRef = useRef('root');
        this.state = useState({
            total_sales: 0,
            growth_percentage: 0,
            cagr: 0,
            sales_data: [],
        });
        this.group_by = 'month'; // Default grouping
        this.salesComparisonChart = null; // Store chart instance
        this.salesGrowthChart = null; // Store chart instance

        // When the component starts, fetch the data.
        onWillStart(async () => {
            await this.fetchData();
        });

        // When the component is mounted, render the charts.
        onMounted(async () => {
            await this.renderCharts();
        });
    }

    async fetchData() {
        const result = await this.orm.call("expected.sale.report", "get_dashboard_data", [1,this.group_by]);
        if (result) {
            this.state.total_sales = result.total_sales;
            this.state.growth_percentage = result.growth_percentage;
            this.state.cagr = result.cagr;
            this.state.sales_data = result.sales_data;
        }
    }

    async renderCharts() {
        this.renderSalesComparisonChart();
        this.renderSalesGrowthChart();
    }

    renderSalesComparisonChart() {
        const ctx = this.rootRef.el.querySelector("#sales_comparison_chart");
        const salesData = this.state.sales_data;

        // Destroy existing chart if it exists
        if (this.salesComparisonChart) {
            this.salesComparisonChart.destroy();
            this.salesComparisonChart = null; // Clear reference
        }

        // Create a new chart instance
        this.salesComparisonChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: salesData.labels,
                datasets: [
                    {
                        label: 'Expected Sales',
                        data: salesData.expected_sales,
                        backgroundColor: '#33ff36',
                    },
                    {
                        label: 'Actual Sales',
                        data: salesData.actual_sales,
                        backgroundColor: '#003f5c',
                    },
                ],
            },
            options: {
                scales: { y: { beginAtZero: true } },
                responsive: true,
                maintainAspectRatio: false,
            },
        });
    }

    renderSalesGrowthChart() {
        const gctx = this.rootRef.el.querySelector("#sales_growth_chart");
        const salesData = this.state.sales_data;

        // Destroy existing chart if it exists
        if (this.salesGrowthChart) {
            this.salesGrowthChart.destroy();
            this.salesGrowthChart = null; // Clear reference
        }

        // Create a new chart instance
        this.salesGrowthChart = new Chart(gctx, {
            type: 'line',
            data: {
                labels: salesData.labels,
                datasets: [{
                    label: 'Growth Rate',
                    data: salesData.growth_rate,
                    backgroundColor: '#003f5c',
                    borderColor: '#003f5c',
                    fill: false,
                }],
            },
            options: {
                scales: { y: { beginAtZero: true } },
                responsive: true,
                maintainAspectRatio: false,
            },
        });
    }

    async onGroupByChange(ev) {
        this.group_by = ev.target.value;
        await this.fetchData();
        await this.renderCharts();
    }
}
ExpectedSalesDashboard.template = "ExpectedSalesDashboard";
actionRegistry.add('expected_sales_dashboard_tag', ExpectedSalesDashboard);

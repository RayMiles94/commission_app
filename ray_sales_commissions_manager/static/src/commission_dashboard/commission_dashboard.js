/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useEffect, useRef, useState } from "@odoo/owl";
import { loadBundle } from "@web/core/assets";
import { _t } from "@web/core/l10n/translation";
import { WarningDialog } from "@web/core/errors/error_dialogs";

/**
 * SalesCommissionDashboard component
 *
 * This component displays a dashboard with sales commission data,
 * including summary counts, charts (bar and line), and filter options.
 * It fetches data from the backend and allows filtering by date range,
 * role type, and data type.
 */
export class SalesCommissionDashboard extends Component {
  static template = "ray.SalesCommissionDashboard";
  static props = {
    action: { Object },
    actionId: { type: Number, optional: true },
    className: String,
    globalState: { type: Object, optional: true },
    updateActionState: { type: Function, optional: true },
  };

  setup() {
    this.action = useService("action");
    this.orm = useService("orm");
    this.chart = null;
    this.chart1 = null;
    this.canvasRef = useRef("canvas");
    this.canvasRef1 = useRef("canvas1");
    this.dialogService = useService("dialog");
    this.chart_data = {
      user_names: [],
      amounts: [],
    };
    this.state = useState({
      filter: {
        start: false,
        end: false,
        role_type: "All",
        data_type: "All",
      },
      datalist: [],
      teams: [],
      team_leaders: [],
      regions: [],
      sales_count: 0,
      commission_count: 0,
      commission_revenue: 0,
    });
    onWillStart(async () => {
      await loadBundle("web.chartjs_lib");
      try {
        let data = await this.orm.call(
          "app.commission.dashboard",
          "load_data",
          [[]]
        );
        if (data.total_sales_count) {
          this.state.sales_count = data.total_sales_count;
        }
        if (data.total_commissions) {
          this.state.commission_count = data.total_commissions;
        }
        if (data.revenue) {
          this.state.commission_revenue = data.revenue;
        }
        if (data.teams) {
          this.state.teams = data.teams;
        }
        if (data.team_leaders) {
          this.state.team_leaders = data.team_leaders;
        }
        if (data.regions) {
          this.state.regions = data.regions;
        }
        if (data.chart) {
          this.chart_data = data.chart;
        }
      } catch (error) {
        console.log(error);
      }
    });

    useEffect(() => {
      this.renderChart(false);
      return () => {
        if (this.chart) {
          this.chart.destroy();
        }
        if (this.chart1) {
          this.chart1.destroy();
        }
      };
    });
  }

  /**
   * Returns Chart.js config for the bar chart
   * @param {Object} chart_data - Chart data with labels and amounts
   */
  _bar_chart(chart_data) {
    return {
      type: "bar",
      data: {
        labels: chart_data.user_names,
        datasets: [
          {
            label: "# of revenue",
            data: chart_data.amounts,
            borderWidth: 1,
          },
        ],
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    };
  }

  /**
   * Returns Chart.js config for the line chart
   * @param {Object} chart_data - Chart data with labels and amounts
   */
  _line_chart(chart_data) {
    return {
      type: "line",
      data: {
        labels: chart_data.user_names,
        datasets: [
          {
            label: "Sales Commission",
            data: chart_data.amounts,
            borderColor: "rgba(75, 192, 192, 1)",
            backgroundColor: "rgba(75, 192, 192, 0.2)",
            tension: 0.4, // Smooth curves
            fill: true,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: "top",
          },
          title: {
            display: true,
            text: "Monthly Commission Trend",
          },
        },
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    };
  }

  /**
   * Render or re-render the charts using the given data or current chart_data state
   * @param {Object|false} data - Chart data object or false to use existing state
   */
  renderChart(data) {
    if (this.chart) {
      this.chart.destroy();
    }
    if (this.chart1) {
      this.chart1.destroy();
    }

    let chart_data = false;
    if (data) {
      chart_data = data;
    } else {
      chart_data = this.chart_data;
    }

    this.chart = new Chart(this.canvasRef.el, this._bar_chart(chart_data));
    this.chart1 = new Chart(this.canvasRef1.el, this._line_chart(chart_data));
  }

  /**
   * Helper to generate six random integers between 1 and 55
   * Used for testing or placeholder data
   */
  getSixRandomInts() {
    const result = [];
    for (let i = 0; i < 6; i++) {
      const randomInt = Math.floor(Math.random() * 55) + 1;
      result.push(randomInt);
    }
    return result;
  }

  onChangeStartDate(value) {
    this.state.filter.start = value;
  }

  onChangeEndDate(value) {
    this.state.filter.end = value;
  }

  onChangeDataType(value) {
    this.state.filter.data_type = value;
  }

  /**
   * Handler for changing role type filter
   * Updates datalist based on selection (Teams, Team Leader, Regions)
   */
  onChangeType(value) {
    this.state.filter.role_type = value;
    this.state.filter.data_type = "All";
    let { teams, team_leaders, regions } = this.state;
    switch (value) {
      case "Teams":
        this.state.datalist = teams;
        break;
      case "Team Leader":
        this.state.datalist = team_leaders;
        break;
      case "Regions":
        this.state.datalist = regions;
        break;
      default:
        this.state.datalist = [];
    }
  }

  /**
   * Called when user triggers dashboard update after setting filters.
   * Validates date range and fetches filtered data from backend.
   * Updates state and re-renders charts accordingly.
   */
  async UpdateDashboard() {
    let { start, end } = this.state.filter;
    const startDate = new Date(start);
    const endDate = new Date(end);

    if (startDate > endDate) {
      return this.dialogService.add(WarningDialog, {
        title: _t("Invalid Date Range"),
        message: _t("Start date cannot be after end date."),
      });
    }
    try {
      let response = await this.orm.call(
        "app.commission.dashboard",
        "filter_data",
        [null, this.state.filter]
      );
      if (response.error) {
        return this.dialogService.add(WarningDialog, {
          title: _t("Error"),
          message: _t("problem in backend"),
        });
      }
      if (response.total_sales_count) {
        this.state.sales_count = response.total_sales_count;
      } else {
        this.state.sales_count = 0;
      }
      if (response.total_commissions) {
        this.state.commission_count = response.total_commissions;
      } else {
        this.state.commission_count = 0;
      }
      if (response.revenue) {
        this.state.commission_revenue = response.revenue;
      } else {
        this.state.commission_revenue = 0;
      }
      if (response.chart_data) {
        this.chart_data = response.chart_data;
        this.renderChart(response.chart_data);
      }
    } catch (error) {}
  }
}

// Register the component as an Odoo action named 'commission_dashboard'
registry
  .category("actions")
  .add("commission_dashboard", SalesCommissionDashboard);

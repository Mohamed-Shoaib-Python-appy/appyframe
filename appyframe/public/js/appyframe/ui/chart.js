import { Chart } from "appyframe-charts/dist/appyframe-charts.esm";

appyframe.provide("appyframe.ui");
appyframe.Chart = Chart;

appyframe.ui.RealtimeChart = class RealtimeChart extends appyframe.Chart {
	constructor(element, socketEvent, maxLabelPoints = 8, data) {
		super(element, data);
		if (data.data.datasets[0].values.length > maxLabelPoints) {
			appyframe.throw(
				__(
					"Length of passed data array is greater than value of maximum allowed label points!"
				)
			);
		}
		this.currentSize = data.data.datasets[0].values.length;
		this.socketEvent = socketEvent;
		this.maxLabelPoints = maxLabelPoints;

		this.start_updating = function () {
			appyframe.realtime.on(this.socketEvent, (data) => {
				this.update_chart(data.label, data.points);
			});
		};

		this.stop_updating = function () {
			appyframe.realtime.off(this.socketEvent);
		};

		this.update_chart = function (label, data) {
			if (this.currentSize >= this.maxLabelPoints) {
				this.removeDataPoint(0);
			} else {
				this.currentSize++;
			}
			this.addDataPoint(__(label), data);
		};
	}
};

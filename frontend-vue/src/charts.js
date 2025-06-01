import ApexCharts from 'apexcharts';
import { fetchDashboardStats, updateMainChart, initDashboard } from './utils/adminApi';
import { CHART_COLORS, CONFIG } from './constants';

// Biến dữ liệu toàn cục cho chart
let dashboardData = {
	series: [
		{
			name: 'Tạo caption',
			data: [0, 0, 0, 0, 0, 0, 0],
			color: CHART_COLORS.ORANGE
		},
		{
			name: 'Đóng góp ảnh',
			data: [0, 0, 0, 0, 0, 0, 0],
			color: CHART_COLORS.BLUE
		}
	],
	categories: ['', '', '', '', '', '', ''],
	summary: {
		total_captions: 0,
		total_contributions: 0,
		total_ratings: 0,
		average_rating: 0
	}
};

// Hàm lấy dữ liệu cho chart
async function loadChartData(days = CONFIG.DEFAULT_DAYS) {
	try {
		const data = await fetchDashboardStats(days);
		if (data && data.success) {
			dashboardData = data;
			return data;
		}
		return null;
	} catch (error) {
		console.error('Failed to load chart data:', error);
		return null;
	}
}

const getMainChartOptions = () => {
	let mainChartColors = {}

	if (document.documentElement.classList.contains('dark')) {
		mainChartColors = {
			borderColor: '#374151',
			labelColor: '#9CA3AF',
			opacityFrom: 0,
			opacityTo: 0.15,
		};
	} else {
		mainChartColors = {
			borderColor: '#F3F4F6',
			labelColor: '#6B7280',
			opacityFrom: 0.45,
			opacityTo: 0,
		}
	}

	return {
		chart: {
			height: 420,
			type: 'area',
			fontFamily: 'Inter, sans-serif',
			foreColor: mainChartColors.labelColor,
			toolbar: {
				show: false
			}
		},
		fill: {
			type: 'gradient',
			gradient: {
				enabled: true,
				opacityFrom: mainChartColors.opacityFrom,
				opacityTo: mainChartColors.opacityTo
			}
		},
		dataLabels: {
			enabled: false
		},
		tooltip: {
			style: {
				fontSize: '14px',
				fontFamily: 'Inter, sans-serif',
			},
		},
		grid: {
			show: true,
			borderColor: mainChartColors.borderColor,
			strokeDashArray: 1,
			padding: {
				left: 35,
				bottom: 15
			}
		},
		series: [
			{
				name: 'Tạo caption',
				data: dashboardData.series[0].data,
				color: CHART_COLORS.ORANGE
			},
			{
				name: 'Đóng góp ảnh',
				data: dashboardData.series[1].data,
				color: CHART_COLORS.BLUE
			}
		],
		markers: {
			size: 5,
			strokeColors: '#ffffff',
			hover: {
				size: undefined,
				sizeOffset: 3
			}
		},
		xaxis: {
			categories: dashboardData.categories,
			labels: {
				style: {
					colors: [mainChartColors.labelColor],
					fontSize: '14px',
					fontWeight: 500,
				},
			},
			axisBorder: {
				color: mainChartColors.borderColor,
			},
			axisTicks: {
				color: mainChartColors.borderColor,
			},
			crosshairs: {
				show: true,
				position: 'back',
				stroke: {
					color: mainChartColors.borderColor,
					width: 1,
					dashArray: 10,
				},
			},
		},
		yaxis: {
			labels: {
				style: {
					colors: [mainChartColors.labelColor],
					fontSize: '14px',
					fontWeight: 500,
				},
				formatter: function (value) {
					return Math.round(value);
				}
			},
		},
		legend: {
			fontSize: '14px',
			fontWeight: 500,
			fontFamily: 'Inter, sans-serif',
			labels: {
				colors: [mainChartColors.labelColor]
			},
			itemMargin: {
				horizontal: 10
			}
		},
		responsive: [
			{
				breakpoint: 1024,
				options: {
					xaxis: {
						labels: {
							show: false
						}
					}
				}
			}
		]
	};
}

// Cập nhật tiêu đề và thông tin tóm tắt cho biểu đồ
function updateChartTitle() {
	const total = (dashboardData.summary.total_captions || 0) + (dashboardData.summary.total_contributions || 0);
	
	// Cập nhật tiêu đề
	const chartTitle = document.querySelector('.text-xl.font-bold');
	if (chartTitle) {
		chartTitle.textContent = total.toString();
	}
	
	// Cập nhật phụ đề
	const chartSubtitle = document.querySelector('.text-base.font-light');
	if (chartSubtitle) {
		chartSubtitle.textContent = 'Tổng hoạt động trong kỳ';
	}
	
	// Cập nhật badge thay đổi
	const percentageChange = document.querySelector('.flex.items-center.justify-end.flex-1.text-base.font-medium.text-green-500');
	if (percentageChange) {
		// Tạm thời hiển thị số lượng caption
		percentageChange.innerHTML = `
			<span>${dashboardData.summary.total_captions || 0}</span>
			<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
			  <path fill-rule="evenodd"
				d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z"
				clip-rule="evenodd"></path>
			</svg>
		`;
	}
}

// Cập nhật chart title khi component đã sẵn sàng
function updateChartUI() {
	// Đợi DOM load xong
	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', updateChartTitle);
	} else {
		updateChartTitle();
	}
}

// Khởi tạo và cập nhật biểu đồ từ dữ liệu API
async function initializeMainChart() {
	try {
		// Lấy dữ liệu từ API
		await loadChartData();
		
		// Cập nhật UI
		updateChartUI();
		
		// Kiểm tra phần tử biểu đồ
		const chartElement = document.getElementById('main-chart');
		if (chartElement) {
			try {
				const chartOptions = getMainChartOptions();
				const chart = new ApexCharts(chartElement, chartOptions);
				chart.render();
	
				// Cập nhật khi chuyển đổi chế độ tối
				document.addEventListener('dark-mode', function () {
					try {
						chart.updateOptions(getMainChartOptions());
					} catch (error) {
						console.warn('Error updating chart on theme change:', error);
					}
				});
				
				// Xử lý sự kiện chọn khoảng thời gian
				const timeRangeButtons = document.querySelectorAll('#weekly-sales-dropdown a');
				timeRangeButtons.forEach(button => {
					button.addEventListener('click', async function(e) {
						e.preventDefault();
						let days = CONFIG.DEFAULT_DAYS;
						
						// Xác định số ngày dựa vào text
						const text = this.textContent.trim().toLowerCase();
						if (text.includes('yesterday')) {
							days = 1;
						} else if (text.includes('today')) {
							days = 1;
						} else if (text.includes('7 days')) {
							days = 7;
						} else if (text.includes('30 days')) {
							days = 30;
						} else if (text.includes('90 days')) {
							days = 90;
						}
						
						try {
							// Cập nhật dữ liệu
							await loadChartData(days);
							chart.updateOptions(getMainChartOptions());
							updateChartTitle();
							
							// Cập nhật dropdown button text
							const dropdownButton = document.querySelector('[data-dropdown-toggle="weekly-sales-dropdown"]');
							if (dropdownButton) {
								dropdownButton.textContent = this.textContent;
								
								// Thêm lại mũi tên
								const arrow = document.createElement('svg');
								arrow.classList.add('w-4', 'h-4', 'ml-2');
								arrow.setAttribute('fill', 'none');
								arrow.setAttribute('stroke', 'currentColor');
								arrow.setAttribute('viewBox', '0 0 24 24');
								arrow.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
								arrow.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>';
								
								dropdownButton.appendChild(arrow);
							}
						} catch (error) {
							console.error('Error updating chart data:', error);
						}
					});
				});
			} catch (error) {
				console.error('Error initializing chart:', error);
				// Hiển thị thông báo lỗi trong chart container
				chartElement.innerHTML = `
					<div class="flex items-center justify-center h-64">
						<div class="text-center text-gray-500 dark:text-gray-400">
							<p>Không thể khởi tạo biểu đồ</p>
							<p class="text-sm">${error.message}</p>
						</div>
					</div>
				`;
			}
		} else {
			console.log('Main chart element not found, skipping chart initialization');
		}
	} catch (error) {
		console.error('Failed to initialize main chart:', error);
	}
}

// Khởi tạo các biểu đồ khi trang đã load
document.addEventListener('DOMContentLoaded', function() {
	// Khởi tạo dashboard API
	initDashboard();
	
	// Khởi tạo biểu đồ chính
	initializeMainChart();
	
	// Các biểu đồ khác giữ nguyên...
});

if (document.getElementById('new-products-chart')) {
	const options = {
		colors: ['#1A56DB', '#FDBA8C'],
		series: [
			{
				name: 'Quantity',
				color: '#1A56DB',
				data: [
					{ x: '01 Feb', y: 170 },
					{ x: '02 Feb', y: 180 },
					{ x: '03 Feb', y: 164 },
					{ x: '04 Feb', y: 145 },
					{ x: '05 Feb', y: 194 },
					{ x: '06 Feb', y: 170 },
					{ x: '07 Feb', y: 155 },
				]
			}
		],
		chart: {
			type: 'bar',
			height: '140px',
			fontFamily: 'Inter, sans-serif',
			foreColor: '#4B5563',
			toolbar: {
				show: false
			}
		},
		plotOptions: {
			bar: {
				columnWidth: '90%',
				borderRadius: 3
			}
		},
		tooltip: {
			shared : false,
			intersect: false,
			style: {
				fontSize: '14px',
				fontFamily: 'Inter, sans-serif'
			},
		},
		states: {
			hover: {
				filter: {
					type: 'darken',
					value: 1
				}
			}
		},
		stroke: {
			show: true,
			width: 5,
			colors: ['transparent']
		},
		grid: {
			show: false
		},
		dataLabels: {
			enabled: false
		},
		legend: {
			show: false
		},
		xaxis: {
			floating: false,
			labels: {
				show: false
			},
			axisBorder: {
				show: false
			},
			axisTicks: {
				show: false
			},
		},
		yaxis: {
			show: false
		},
		fill: {
			opacity: 1
		}
	};

	const chart = new ApexCharts(document.getElementById('new-products-chart'), options);
	chart.render();
}

if (document.getElementById('sales-by-category')) {
	const options = {
		colors: ['#1A56DB', '#FDBA8C'],
		series: [
			{
				name: 'Desktop PC',
				color: '#1A56DB',
				data: [
					{ x: '01 Feb', y: 170 },
					{ x: '02 Feb', y: 180 },
					{ x: '03 Feb', y: 164 },
					{ x: '04 Feb', y: 145 },
					{ x: '05 Feb', y: 194 },
					{ x: '06 Feb', y: 170 },
					{ x: '07 Feb', y: 155 },
				]
			},
			{
				name: 'Phones',
				color: '#FDBA8C',
				data: [
					{ x: '01 Feb', y: 120 },
					{ x: '02 Feb', y: 294 },
					{ x: '03 Feb', y: 167 },
					{ x: '04 Feb', y: 179 },
					{ x: '05 Feb', y: 245 },
					{ x: '06 Feb', y: 182 },
					{ x: '07 Feb', y: 143 }
				]
			},
			{
				name: 'Gaming/Console',
				color: '#17B0BD',
				data: [
					{ x: '01 Feb', y: 220 },
					{ x: '02 Feb', y: 194 },
					{ x: '03 Feb', y: 217 },
					{ x: '04 Feb', y: 279 },
					{ x: '05 Feb', y: 215 },
					{ x: '06 Feb', y: 263 },
					{ x: '07 Feb', y: 183 }
				]
			}
		],
		chart: {
			type: 'bar',
			height: '420px',
			fontFamily: 'Inter, sans-serif',
			foreColor: '#4B5563',
			toolbar: {
				show: false
			}
		},
		plotOptions: {
			bar: {
				columnWidth: '90%',
				borderRadius: 3
			}
		},
		tooltip: {
			shared : true,
			intersect: false,
			style: {
				fontSize: '14px',
				fontFamily: 'Inter, sans-serif'
			},
		},
		states: {
			hover: {
				filter: {
					type: 'darken',
					value: 1
				}
			}
		},
		stroke: {
			show: true,
			width: 5,
			colors: ['transparent']
		},
		grid: {
			show: false
		},
		dataLabels: {
			enabled: false
		},
		legend: {
			show: false
		},
		xaxis: {
			floating: false,
			labels: {
				show: false
			},
			axisBorder: {
				show: false
			},
			axisTicks: {
				show: false
			},
		},
		yaxis: {
			show: false
		},
		fill: {
			opacity: 1
		}
	};

	const chart = new ApexCharts(document.getElementById('sales-by-category'), options);
	chart.render();
}

const getVisitorsChartOptions = () => {
	let visitorsChartColors = {}

	if (document.documentElement.classList.contains('dark')) {
		visitorsChartColors = {
			fillGradientShade: 'dark',
			fillGradientShadeIntensity: 0.45,
		};
	} else {
		visitorsChartColors = {
			fillGradientShade: 'light',
			fillGradientShadeIntensity: 1,
		}
	}

	return {
		series: [{
			name: 'Visitors',
			data: [500, 590, 600, 520, 610, 550, 600]
		}],
		labels: ['01 Feb', '02 Feb', '03 Feb', '04 Feb', '05 Feb', '06 Feb', '07 Feb'],
		chart: {
			type: 'area',
			height: '305px',
			fontFamily: 'Inter, sans-serif',
			sparkline: {
				enabled: true
			},
			toolbar: {
				show: false
			}
		},
		fill: {
			type: 'gradient',
			gradient: {
				shade: visitorsChartColors.fillGradientShade,
				shadeIntensity: visitorsChartColors.fillGradientShadeIntensity
			},
		},
		plotOptions: {
			area: {
				fillTo: 'end'
			}
		},
		theme: {
			monochrome: {
				enabled: true,
				color: '#1A56DB',
			}
		},
		tooltip: {
			style: {
				fontSize: '14px',
				fontFamily: 'Inter, sans-serif'
			},
		},
	}
}


const getSignupsChartOptions = () => {
	let signupsChartColors = {}

	if (document.documentElement.classList.contains('dark')) {
		signupsChartColors = {
			backgroundBarColors: ['#374151', '#374151', '#374151', '#374151', '#374151', '#374151', '#374151']
		};
	} else {
		signupsChartColors = {
			backgroundBarColors: ['#E5E7EB', '#E5E7EB', '#E5E7EB', '#E5E7EB', '#E5E7EB', '#E5E7EB', '#E5E7EB']
		};
	}

	return {
		series: [{
			name: 'Users',
			data: [1334, 2435, 1753, 1328, 1155, 1632, 1336]
		}],
		labels: ['01 Feb', '02 Feb', '03 Feb', '04 Feb', '05 Feb', '06 Feb', '07 Feb'],
		chart: {
			type: 'bar',
			height: '140px',
			foreColor: '#4B5563',
			fontFamily: 'Inter, sans-serif',
			toolbar: {
				show: false
			}
		},
		theme: {
			monochrome: {
				enabled: true,
				color: '#1A56DB'
			}
		},
		plotOptions: {
			bar: {
				columnWidth: '25%',
				borderRadius: 3,
				colors: {
					backgroundBarColors: signupsChartColors.backgroundBarColors,
					backgroundBarRadius: 3
				},
			},
			dataLabels: {
				hideOverflowingLabels: false
			}
		},
		xaxis: {
			floating: false,
			labels: {
				show: false
			},
			axisBorder: {
				show: false
			},
			axisTicks: {
				show: false
			},
		},
		tooltip: {
			shared: true,
			intersect: false,
			style: {
				fontSize: '14px',
				fontFamily: 'Inter, sans-serif'
			}
		},
		states: {
			hover: {
				filter: {
					type: 'darken',
					value: 0.8
				}
			}
		},
		fill: {
			opacity: 1
		},
		yaxis: {
			show: false
		},
		grid: {
			show: false
		},
		dataLabels: {
			enabled: false
		},
		legend: {
			show: false
		},
	};
}

if (document.getElementById('week-signups-chart')) {
	const chart = new ApexCharts(document.getElementById('week-signups-chart'), getSignupsChartOptions());
	chart.render();

	// init again when toggling dark mode
	document.addEventListener('dark-mode', function () {
		chart.updateOptions(getSignupsChartOptions());
	});
}

const getTrafficChannelsChartOptions = () => {

	let trafficChannelsChartColors = {}

	if (document.documentElement.classList.contains('dark')) {
		trafficChannelsChartColors = {
			strokeColor: '#1f2937'
		};
	} else {
		trafficChannelsChartColors = {
			strokeColor: '#ffffff'
		}
	}

	return {
		series: [70, 5, 25],
		labels: ['Desktop', 'Tablet', 'Phone'],
		colors: ['#16BDCA', '#FDBA8C', '#1A56DB'],
		chart: {
			type: 'donut',
			height: 400,
			fontFamily: 'Inter, sans-serif',
			toolbar: {
				show: false
			},
		},
		responsive: [{
			breakpoint: 430,
			options: {
			  chart: {
				height: 300
			  }
			}
		}],
		stroke: {
			colors: [trafficChannelsChartColors.strokeColor]
		},
		states: {
			hover: {
				filter: {
					type: 'darken',
					value: 0.9
				}
			}
		},
		tooltip: {
			shared: true,
			followCursor: false,
			fillSeriesColor: false,
			inverseOrder: true,
			style: {
				fontSize: '14px',
				fontFamily: 'Inter, sans-serif'
			},
			x: {
				show: true,
				formatter: function (_, { seriesIndex, w }) {
					const label = w.config.labels[seriesIndex];
					return label
				}
			},
			y: {
				formatter: function (value) {
					return value + '%';
				}
			}
		},
		grid: {
			show: false
		},
		dataLabels: {
			enabled: false
		},
		legend: {
			show: false
		},
	};
}

if (document.getElementById('traffic-by-device')) {
	const chart = new ApexCharts(document.getElementById('traffic-by-device'), getTrafficChannelsChartOptions());
	chart.render();

	// init again when toggling dark mode
	document.addEventListener('dark-mode', function () {
		chart.updateOptions(getTrafficChannelsChartOptions());
	});
}

// Export các hàm để sử dụng trong các file khác
export { getMainChartOptions, loadChartData, updateChartTitle, updateChartUI };

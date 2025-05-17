<template>
  <div class="grid grid-cols-1 gap-6 lg:grid-cols-2 2xl:grid-cols-3">
    <!-- Main Stats -->
    <div class="dashboard-card col-span-1 lg:col-span-2 2xl:col-span-3">
      <div class="flex justify-between items-start">
        <h3 class="text-xl font-bold leading-none text-gray-900 dark:text-white">Thống kê hệ thống</h3>
      </div>
      <div class="flex flex-col mt-6">
        <div class="overflow-x-auto rounded-lg">
          <div class="inline-block min-w-full align-middle">
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div class="stat-card">
                <div class="flex items-center">
                  <div class="inline-flex flex-shrink-0 justify-center items-center w-12 h-12 text-blue-500 bg-blue-100 rounded-lg dark:bg-blue-900 dark:text-blue-300">
                    <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                      <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd"></path>
                    </svg>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-500 truncate dark:text-gray-400">Tổng lượt tạo Caption</div>
                    <div class="text-2xl font-semibold text-gray-900 dark:text-white">{{ stats.totalCaptions }}</div>
                  </div>
                </div>
              </div>
              <div class="stat-card">
                <div class="flex items-center">
                  <div class="inline-flex flex-shrink-0 justify-center items-center w-12 h-12 text-green-500 bg-green-100 rounded-lg dark:bg-green-900 dark:text-green-300">
                    <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                      <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd"></path>
                    </svg>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-500 truncate dark:text-gray-400">Tổng ảnh đóng góp</div>
                    <div class="text-2xl font-semibold text-gray-900 dark:text-white">{{ stats.totalContributions }}</div>
                  </div>
                </div>
              </div>
              <div class="stat-card">
                <div class="flex items-center">
                  <div class="inline-flex flex-shrink-0 justify-center items-center w-12 h-12 text-yellow-500 bg-yellow-100 rounded-lg dark:bg-yellow-900 dark:text-yellow-300">
                    <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                    </svg>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-500 truncate dark:text-gray-400">Tổng lượt đánh giá</div>
                    <div class="text-2xl font-semibold text-gray-900 dark:text-white">{{ stats.totalRatings }}</div>
                  </div>
                </div>
              </div>
              <div class="stat-card">
                <div class="flex items-center">
                  <div class="inline-flex flex-shrink-0 justify-center items-center w-12 h-12 text-red-500 bg-red-100 rounded-lg dark:bg-red-900 dark:text-red-300">
                    <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                    </svg>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-500 truncate dark:text-gray-400">Điểm đánh giá TB</div>
                    <div class="text-2xl font-semibold text-gray-900 dark:text-white">{{ stats.averageRating }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Activity Chart -->
    <div class="dashboard-card lg:col-span-2">
      <div class="flex justify-between mb-4">
        <div class="flex-shrink-0">
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">Hoạt động hệ thống</h3>
          <span class="text-base font-normal text-gray-500 dark:text-gray-400">{{ chartDays }} ngày qua</span>
        </div>
        <div class="flex items-center space-x-2">
          <button 
            @click="changeChartPeriod(7)" 
            :class="[
              'px-3 py-1 text-xs font-medium rounded-lg',
              chartDays === 7 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
            ]">
            7 ngày
          </button>
          <button 
            @click="changeChartPeriod(30)" 
            :class="[
              'px-3 py-1 text-xs font-medium rounded-lg',
              chartDays === 30 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
            ]">
            30 ngày
          </button>
        </div>
      </div>
      <div id="activity-chart" class="chart-container"></div>
    </div>

    <!-- Leaderboard -->
    <div class="dashboard-card">
      <div class="flex justify-between items-start">
        <h3 class="text-xl font-bold leading-none text-gray-900 dark:text-white">Bảng xếp hạng</h3>
      </div>
      <div class="flow-root mt-4">
        <ul class="divide-y divide-gray-200 dark:divide-gray-700">
          <li v-if="topContributors.length === 0" class="py-3 sm:py-4">
            <div class="flex items-center justify-center">
              <p class="text-sm text-gray-500 dark:text-gray-400">
                Chưa có dữ liệu đóng góp
              </p>
            </div>
          </li>
          <li v-for="(user, index) in topContributors" :key="user.id" class="py-3 sm:py-4">
            <div class="flex items-center space-x-4">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-blue-500 dark:text-blue-300 font-bold">
                  {{ index + 1 }}
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate dark:text-white">
                  {{ user.username }}
                </p>
              </div>
              <div class="inline-flex items-center">
                <span class="bg-blue-100 text-blue-800 text-sm font-medium me-2 px-2.5 py-0.5 rounded dark:bg-blue-900 dark:text-blue-300">
                  {{ user.contribution_count }}
                </span>
                <span class="text-sm text-gray-700 dark:text-gray-300">đóng góp</span>
              </div>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted, ref, watch } from 'vue';
import ApexCharts from 'apexcharts';
import { fetchDashboardStats, fetchTopContributors } from '../../utils/adminApi';

export default {
  name: 'Dashboard',
  setup() {
    const stats = ref({
      totalCaptions: '0',
      totalContributions: '0',
      totalRatings: '0',
      averageRating: '0.0'
    });
    
    const chartDays = ref(7);
    const topContributors = ref([]);
    let activityChart = null;
    
    const loadDashboardStats = async () => {
      try {
        console.log('Fetching dashboard stats with days:', chartDays.value);
        const response = await fetchDashboardStats(chartDays.value);
        console.log('API response:', response);
        
        if (response.success) {
          stats.value = {
            totalCaptions: response.data.totalCaptions.toLocaleString(),
            totalContributions: response.data.totalContributions.toLocaleString(),
            totalRatings: response.data.totalRatings.toLocaleString(),
            averageRating: Number(response.data.averageRating).toFixed(1)
          };
          
          updateActivityChart(response.data);
        } else {
          console.error('API returned success:false', response.error);
        }
      } catch (error) {
        console.error('Error loading dashboard stats:', error);
      }
    };

    const loadTopContributors = async () => {
      try {
        console.log('Fetching top contributors');
        const response = await fetchTopContributors();
        console.log('Top contributors response:', response);
        
        if (response.success) {
          topContributors.value = response.data;
        } else {
          console.error('Failed to fetch top contributors:', response.error);
        }
      } catch (error) {
        console.error('Error loading top contributors:', error);
      }
    };
    
    const updateActivityChart = (data) => {
      if (!data || !data.series || !data.categories) {
        console.error('Chart data is missing required properties', data);
        return;
      }
      
      console.log('Updating chart with data:', data);
      
      // Make sure we have the proper data series and they're in the right order
      const captionSeries = data.series.find(s => s.name === 'Tạo caption') || { name: 'Tạo caption', data: [] };
      const contributionSeries = data.series.find(s => s.name === 'Đóng góp ảnh') || { name: 'Đóng góp ảnh', data: [] };
      
      console.log('Caption series:', captionSeries);
      console.log('Contribution series:', contributionSeries);
      
      // Use categories directly from the backend without trying to parse dates
      const formattedCategories = data.categories;
      
      console.log('Formatted categories:', formattedCategories);
      
      const chartOptions = {
        chart: {
          height: 320,
          type: 'area',
          fontFamily: 'Inter, sans-serif',
          toolbar: {
            show: false
          },
          animations: {
            enabled: true,
            easing: 'easeinout',
            speed: 800,
            animateGradually: {
              enabled: true,
              delay: 150
            },
            dynamicAnimation: {
              enabled: true,
              speed: 350
            }
          }
        },
        series: [
          {
            name: captionSeries.name,
            data: captionSeries.data
          },
          {
            name: contributionSeries.name,
            data: contributionSeries.data
          }
        ],
        dataLabels: {
          enabled: false
        },
        grid: {
          show: true,
          strokeDashArray: 4,
          padding: {
            left: 2,
            right: 2,
            top: -20
          }
        },
        xaxis: {
          categories: formattedCategories,
          labels: {
            show: true,
            style: {
              fontFamily: 'Inter, sans-serif',
              cssClass: 'text-xs font-normal fill-gray-500 dark:fill-gray-400'
            }
          },
          axisBorder: {
            show: false
          },
          axisTicks: {
            show: false
          }
        },
        yaxis: {
          labels: {
            show: true,
            style: {
              fontFamily: 'Inter, sans-serif',
              cssClass: 'text-xs font-normal fill-gray-500 dark:fill-gray-400'
            }
          }
        },
        stroke: {
          width: 3,
          curve: 'smooth'
        },
        fill: {
          type: 'gradient',
          gradient: {
            shade: 'light',
            type: 'vertical',
            shadeIntensity: 0.5,
            opacityFrom: 0.5,
            opacityTo: 0,
            stops: [0, 100]
          }
        },
        colors: ['#f97316', '#3b82f6'], // Orange for captions, blue for contributions
        legend: {
          show: true,
          position: 'top',
          horizontalAlign: 'left',
          fontSize: '14px',
          fontFamily: 'Inter, sans-serif',
          offsetY: -5
        },
        tooltip: {
          enabled: true,
          shared: true,
          custom: ({ series, seriesIndex, dataPointIndex, w }) => {
            const date = formattedCategories[dataPointIndex];
            const captionValue = series[0][dataPointIndex];
            const contributionValue = series[1][dataPointIndex];
            
            return `
              <div class="p-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm">
                <div class="font-medium text-gray-800 dark:text-white">${date}</div>
                <div class="flex items-center mt-1">
                  <span class="w-3 h-3 rounded-full bg-orange-500 mr-1"></span>
                  <span class="text-gray-600 dark:text-gray-400">${captionSeries.name}: </span>
                  <span class="ml-1 font-medium text-gray-900 dark:text-white">${captionValue}</span>
                </div>
                <div class="flex items-center mt-1">
                  <span class="w-3 h-3 rounded-full bg-blue-500 mr-1"></span>
                  <span class="text-gray-600 dark:text-gray-400">${contributionSeries.name}: </span>
                  <span class="ml-1 font-medium text-gray-900 dark:text-white">${contributionValue}</span>
                </div>
              </div>
            `;
          }
        }
      };

      if (activityChart) {
        activityChart.updateOptions(chartOptions);
      } else {
        const chartElement = document.getElementById('activity-chart');
        if (chartElement) {
          activityChart = new ApexCharts(chartElement, chartOptions);
          activityChart.render();
        } else {
          console.error('Chart element not found');
        }
      }
    };
    
    const changeChartPeriod = (days) => {
      chartDays.value = days;
      loadDashboardStats();
    };

    onMounted(() => {
      // Load dashboard statistics
      loadDashboardStats();
      // Load top contributors
      loadTopContributors();
    });
    
    return {
      stats,
      chartDays,
      topContributors,
      changeChartPeriod
    };
  }
}
</script>

<style>
.chart-container {
  min-height: 320px;
}

.dashboard-card {
  @apply bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 sm:p-6;
}

.stat-card {
  @apply bg-white shadow rounded-lg p-4 sm:p-6 h-full dark:bg-gray-700 transition-all duration-200 hover:shadow-lg;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 100px;
}
</style> 
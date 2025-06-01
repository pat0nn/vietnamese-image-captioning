// Hàm lấy thông tin thống kê từ API
import { API_URL, CONFIG, CHART_COLORS } from '../constants';

/**
 * Helper function to get the correct API URL based on configuration
 * @returns {string} The appropriate API URL
 */
function getApiUrl() {
    // Sử dụng API_URL từ window hoặc từ constants
    const apiUrl = window.API_URL || API_URL;
    
    // Nếu là URL tương đối (rỗng), sử dụng gốc của window.location
    if (apiUrl === '' && typeof window !== 'undefined') {
        return window.location.origin;
    }
    
    return apiUrl;
}

// User Management API Functions
async function fetchUsers(page = 1, limit = 20, search = '') {
    try {
        // Sử dụng helper function để lấy API URL
        const apiUrl = getApiUrl();
        
        // Lấy token từ localStorage
        const token = localStorage.getItem(CONFIG.TOKEN_KEY);
        
        if (!token) {
            console.error('No authentication token found');
            return null;
        }
        
        // Thiết lập các headers cho request
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
        
        // Build query string
        let queryParams = new URLSearchParams();
        queryParams.append('page', page);
        queryParams.append('limit', limit);
        if (search) {
            queryParams.append('search', search);
        }
        
        // Gọi API để lấy danh sách người dùng
        const response = await fetch(`${apiUrl}/api/admin/users?${queryParams.toString()}`, {
            method: 'GET',
            headers: headers,
            credentials: 'include'
        });
        
        // Kiểm tra response status
        if (!response.ok) {
            if (response.status === 401) {
                console.error('Unauthorized access. Please login again.');
                // Có thể redirect người dùng đến trang đăng nhập tại đây
                return null;
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Parse dữ liệu JSON từ response
        const data = await response.json();
        
        if (!data.success) {
            console.error('API error:', data.error);
            return null;
        }
        
        return data;
    } catch (error) {
        console.error('Error fetching users:', error);
        return null;
    }
}

async function fetchUserById(userId) {
    try {
        const apiUrl = getApiUrl();
        const token = localStorage.getItem(CONFIG.TOKEN_KEY);
        
        if (!token) {
            console.error('No authentication token found');
            return null;
        }
        
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
        
        const response = await fetch(`${apiUrl}/api/admin/users/${userId}`, {
            method: 'GET',
            headers: headers,
            credentials: 'include'
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                console.error('Unauthorized access. Please login again.');
                return null;
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            console.error('API error:', data.error);
            return null;
        }
        
        return data.user;
    } catch (error) {
        console.error('Error fetching user:', error);
        return null;
    }
}

async function createUser(userData) {
    try {
        const apiUrl = getApiUrl();
        const token = localStorage.getItem(CONFIG.TOKEN_KEY);
        
        if (!token) {
            console.error('No authentication token found');
            return null;
        }
        
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
        
        const response = await fetch(`${apiUrl}/api/admin/users`, {
            method: 'POST',
            headers: headers,
            credentials: 'include',
            body: JSON.stringify(userData)
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                console.error('Unauthorized access. Please login again.');
                return null;
            }
            
            // Get error message from response
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            console.error('API error:', data.error);
            return null;
        }
        
        return data;
    } catch (error) {
        console.error('Error creating user:', error);
        throw error;
    }
}

async function updateUser(userId, userData) {
    try {
        const apiUrl = getApiUrl();
        const token = localStorage.getItem(CONFIG.TOKEN_KEY);
        
        if (!token) {
            console.error('No authentication token found');
            return null;
        }
        
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
        
        const response = await fetch(`${apiUrl}/api/admin/users/${userId}`, {
            method: 'PUT',
            headers: headers,
            credentials: 'include',
            body: JSON.stringify(userData)
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                console.error('Unauthorized access. Please login again.');
                return null;
            }
            
            // Get error message from response
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            console.error('API error:', data.error);
            return null;
        }
        
        return data;
    } catch (error) {
        console.error('Error updating user:', error);
        throw error;
    }
}

async function deleteUser(userId) {
    try {
        const apiUrl = getApiUrl();
        const token = localStorage.getItem(CONFIG.TOKEN_KEY);
        
        if (!token) {
            console.error('No authentication token found');
            return null;
        }
        
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
        
        const response = await fetch(`${apiUrl}/api/admin/users/${userId}`, {
            method: 'DELETE',
            headers: headers,
            credentials: 'include'
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                console.error('Unauthorized access. Please login again.');
                return null;
            }
            
            // Get error message from response
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            console.error('API error:', data.error);
            return null;
        }
        
        return data;
    } catch (error) {
        console.error('Error deleting user:', error);
        throw error;
    }
}

// Login API Function
async function loginUser(username, password) {
    try {
        const apiUrl = getApiUrl();
        
        const response = await fetch(`${apiUrl}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                username, 
                password,
                admin_only: true  // Set this to true for admin dashboard login
            })
        });
        
        if (!response.ok) {
            // Get error message from response
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            console.error('API error:', data.error);
            return null;
        }
        
        // Save token to localStorage
        localStorage.setItem(CONFIG.TOKEN_KEY, data.token);
        
        return data;
    } catch (error) {
        console.error('Error logging in:', error);
        throw error;
    }
}

async function fetchDashboardStats(days = CONFIG.DEFAULT_DAYS) {
    try {
        // Sử dụng API_URL từ config hoặc thiết lập mặc định
        const apiUrl = getApiUrl();
        console.log('Fetching dashboard stats from:', apiUrl, 'with days:', days);
        
        // Lấy token từ localStorage
        const token = localStorage.getItem(CONFIG.TOKEN_KEY);
        
        if (!token) {
            console.error('No authentication token found');
            return {
                success: false,
                error: 'No authentication token found'
            };
        }
        
        // Thiết lập các headers cho request
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
        
        // Gọi API để lấy dữ liệu
        const url = `${apiUrl}/api/admin/dashboard/stats?days=${days}`;
        console.log('API URL:', url);
        
        const response = await fetch(url, {
            method: 'GET',
            headers: headers,
            credentials: 'include'
        });
        
        // Kiểm tra response status
        if (!response.ok) {
            if (response.status === 401) {
                console.error('Unauthorized access. Please login again.');
                // Có thể redirect người dùng đến trang đăng nhập tại đây
                return {
                    success: false,
                    error: 'Unauthorized access'
                };
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Parse dữ liệu JSON từ response
        const data = await response.json();
        console.log('Dashboard stats API response:', data);
        
        if (!data.success) {
            console.error('API error:', data.error);
            return {
                success: false,
                error: data.error || 'Unknown API error'
            };
        }
        
        // If the backend returns empty or invalid data, return an error
        if (!data.data) {
            console.error('Backend returned no data');
            return {
                success: false,
                error: 'No data returned from server'
            };
        }
        
        return data;
    } catch (error) {
        console.error('Error fetching dashboard stats:', error);
        return {
            success: false,
            error: error.message || 'Error fetching dashboard data'
        };
    }
}

async function fetchTopContributors(limit = 5) {
    try {
        // Sử dụng API_URL từ config hoặc thiết lập mặc định
        const apiUrl = getApiUrl();
        console.log('Fetching top contributors from:', apiUrl);
        
        // Lấy token từ localStorage
        const token = localStorage.getItem(CONFIG.TOKEN_KEY);
        
        if (!token) {
            console.error('No authentication token found');
            return {
                success: false,
                error: 'No authentication token found'
            };
        }
        
        // Thiết lập các headers cho request
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
        
        // Gọi API để lấy dữ liệu
        const url = `${apiUrl}/api/admin/top-contributors?limit=${limit}`;
        console.log('API URL:', url);
        
        const response = await fetch(url, {
            method: 'GET',
            headers: headers,
            credentials: 'include'
        });
        
        // Kiểm tra response status
        if (!response.ok) {
            if (response.status === 401) {
                console.error('Unauthorized access. Please login again.');
                return {
                    success: false,
                    error: 'Unauthorized access'
                };
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Parse dữ liệu JSON từ response
        const data = await response.json();
        console.log('Top contributors API response:', data);
        
        if (!data.success) {
            console.error('API error:', data.error);
            return {
                success: false,
                error: data.error || 'Unknown API error'
            };
        }
        
        return data;
    } catch (error) {
        console.error('Error fetching top contributors:', error);
        return {
            success: false,
            error: error.message || 'Error fetching top contributors data'
        };
    }
}

// Hàm cập nhật biểu đồ chính trên dashboard
function updateMainChart(chartData) {
    if (!chartData || !window.ApexCharts) {
        console.error('Chart data or ApexCharts library is missing');
        return;
    }
    
    // Check if the chart element exists
    const chartElement = document.getElementById('main-chart');
    if (!chartElement) {
        console.error('Main chart element not found');
        return;
    }
    
    // Cập nhật tiêu đề và thông tin của chart
    const chartTitle = document.querySelector('.text-xl.font-bold');
    if (chartTitle) {
        chartTitle.textContent = `${chartData.summary.total_captions + chartData.summary.total_contributions || 0}`;
    }
    
    const chartSubtitle = document.querySelector('.text-base.font-light');
    if (chartSubtitle) {
        chartSubtitle.textContent = 'Tổng hoạt động trong kỳ';
    }
    
    // Chuẩn bị dữ liệu cho chart
    const captionSeries = chartData.series[0].data;
    const contributionSeries = chartData.series[1].data;
    const categories = chartData.categories;
    
    // Tạo chart options
    const mainChartOptions = {
        chart: {
            height: 420,
            type: 'area',
            fontFamily: 'Inter, sans-serif',
            toolbar: {
                show: false
            }
        },
        fill: {
            type: 'gradient',
            gradient: {
                enabled: true,
                opacityFrom: 0.45,
                opacityTo: 0
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
            borderColor: '#F3F4F6',
            strokeDashArray: 1,
            padding: {
                left: 35,
                bottom: 15
            }
        },
        series: [
            {
                name: 'Tạo caption',
                data: captionSeries,
                color: CHART_COLORS.ORANGE
            },
            {
                name: 'Đóng góp ảnh',
                data: contributionSeries,
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
            categories: categories,
            labels: {
                style: {
                    fontSize: '14px',
                    fontWeight: 500,
                },
            }
        },
        yaxis: {
            labels: {
                style: {
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
            itemMargin: {
                horizontal: 10
            }
        }
    };
    
    // Áp dụng theme dark mode nếu cần
    if (document.documentElement.classList.contains('dark')) {
        mainChartOptions.grid.borderColor = '#374151';
        mainChartOptions.xaxis.labels.style.colors = '#9CA3AF';
        mainChartOptions.yaxis.labels.style.colors = '#9CA3AF';
        mainChartOptions.legend.labels = {
            colors: ['#9CA3AF']
        };
        mainChartOptions.fill.gradient.opacityFrom = 0;
        mainChartOptions.fill.gradient.opacityTo = 0.15;
    }
    
    try {
        // Khởi tạo và render chart
        const chart = new ApexCharts(chartElement, mainChartOptions);
        chart.render();
        
        // Xử lý khi chuyển đổi dark mode
        document.addEventListener('dark-mode', function () {
            try {
                chart.updateOptions(mainChartOptions);
            } catch (error) {
                console.warn('Could not update chart on theme change:', error);
            }
        });
    } catch (error) {
        console.error('Error rendering chart:', error);
        // Hiển thị thông báo lỗi trong chart container
        chartElement.innerHTML = `
            <div class="flex items-center justify-center h-64">
                <div class="text-center text-gray-500 dark:text-gray-400">
                    <p>Không thể hiển thị biểu đồ</p>
                    <p class="text-sm">${error.message}</p>
                </div>
            </div>
        `;
    }
}

// Hàm tạo bảng tóm tắt thống kê
function updateStatsSummary(statsData) {
    if (!statsData || !statsData.summary) {
        return;
    }
    
    const summary = statsData.summary;
    
    // Tìm phần tử chứa các card thống kê
    const statsContainer = document.querySelector('.grid-cols-1.sm\\:grid-cols-2.xl\\:grid-cols-4');
    if (!statsContainer) {
        return;
    }
    
    // Cập nhật hoặc thay thế nội dung
    statsContainer.innerHTML = `
        <div class="p-4 bg-white border border-gray-200 rounded-lg shadow-sm dark:border-gray-700 sm:p-6 dark:bg-gray-800">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Lượt tạo caption</h3>
                <div class="flex items-center justify-end flex-1 text-base font-medium text-green-500 dark:text-green-400">
                    ${summary.total_captions || 0}
                </div>
            </div>
            <div id="month-activity-chart"></div>
        </div>
        <div class="p-4 bg-white border border-gray-200 rounded-lg shadow-sm dark:border-gray-700 sm:p-6 dark:bg-gray-800">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Lượt đóng góp</h3>
                <div class="flex items-center justify-end flex-1 text-base font-medium text-green-500 dark:text-green-400">
                    ${summary.total_contributions || 0}
                </div>
            </div>
            <div id="new-customers-chart"></div>
        </div>
        <div class="p-4 bg-white border border-gray-200 rounded-lg shadow-sm dark:border-gray-700 sm:p-6 dark:bg-gray-800">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Lượt đánh giá</h3>
                <div class="flex items-center justify-end flex-1 text-base font-medium text-green-500 dark:text-green-400">
                    ${summary.total_ratings || 0}
                </div>
            </div>
            <div id="week-signups-chart"></div>
        </div>
        <div class="p-4 bg-white border border-gray-200 rounded-lg shadow-sm dark:border-gray-700 sm:p-6 dark:bg-gray-800">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Đánh giá trung bình</h3>
                <div class="flex items-center justify-end flex-1 text-base font-medium text-green-500 dark:text-green-400">
                    ${summary.average_rating?.toFixed(1) || 0}/5
                </div>
            </div>
            <div id="week-signups-chart-2"></div>
        </div>
    `;
}

// Hàm khởi tạo và load dữ liệu
async function initDashboard() {
    // Thiết lập API_URL từ window hoặc mặc định
    window.API_URL = window.API_URL || API_URL;
    
    // Kiểm tra xem người dùng đã đăng nhập chưa
    const token = localStorage.getItem(CONFIG.TOKEN_KEY);
    if (!token) {
        console.warn('No authentication token found, skipping dashboard initialization');
        return;
    }
    
    // Lấy số ngày thống kê từ query param hoặc mặc định
    const urlParams = new URLSearchParams(window.location.search);
    const days = parseInt(urlParams.get('days') || CONFIG.DEFAULT_DAYS.toString(), 10);
    
    // Lấy dữ liệu từ API
    const statsData = await fetchDashboardStats(days);
    if (!statsData) {
        console.error('Failed to fetch dashboard statistics');
        return;
    }
    
    // Cập nhật biểu đồ và summary
    updateMainChart(statsData);
    updateStatsSummary(statsData);
    
    // Thiết lập auto-refresh
    setInterval(async () => {
        console.log('Auto-refreshing dashboard data...');
        const refreshedData = await fetchDashboardStats(days);
        if (refreshedData) {
            updateMainChart(refreshedData);
            updateStatsSummary(refreshedData);
        }
    }, CONFIG.DASHBOARD_REFRESH_INTERVAL);
}

// Contribution API Functions
async function fetchContributions(params = {}) {
    try {
        const apiUrl = getApiUrl();
        const token = localStorage.getItem(CONFIG.TOKEN_KEY);
        
        if (!token) {
            console.error('No authentication token found');
            return { success: false, error: 'No authentication token found' };
        }
        
        const headers = {
            'Authorization': `Bearer ${token}`
        };
        
        // Build query string with all possible parameters
        let queryParams = new URLSearchParams();
        if (params.page) queryParams.append('page', params.page);
        if (params.limit) queryParams.append('limit', params.limit);
        if (params.status) queryParams.append('status', params.status);
        if (params.search) queryParams.append('search', params.search);
        if (params.userId) queryParams.append('user_id', params.userId);
        
        const response = await fetch(`${apiUrl}/api/admin/contributions?${queryParams.toString()}`, {
            method: 'GET',
            headers: headers,
            credentials: 'include'
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                console.error('Unauthorized access. Please login again.');
                return { success: false, error: 'Authentication failed' };
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            console.error('API error:', data.error);
            return { success: false, error: data.error };
        }
        
        return {
            success: true,
            data: {
                contributions: data.contributions || [],
                total: data.total || 0
            }
        };
    } catch (error) {
        console.error('Error fetching contributions:', error);
        return { success: false, error: error.message };
    }
}

async function contributeImage(formData) {
    try {
        const apiUrl = getApiUrl();
        const token = localStorage.getItem(CONFIG.TOKEN_KEY);
        
        if (!token) {
            console.error('No authentication token found');
            return { success: false, error: 'No authentication token found' };
        }
        
        const headers = {
            'Authorization': `Bearer ${token}`
            // Don't set Content-Type here as it will be automatically set with the boundary when using FormData
        };
        
        const response = await fetch(`${apiUrl}/api/contribute`, {
            method: 'POST',
            headers: headers,
            body: formData,
            credentials: 'include'
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                console.error('Unauthorized access. Please login again.');
                return { success: false, error: 'Authentication failed' };
            }
            
            // Try to get error message from response
            let errorMessage;
            try {
                const errorData = await response.json();
                errorMessage = errorData.error;
            } catch (e) {
                errorMessage = `HTTP error! status: ${response.status}`;
            }
            
            throw new Error(errorMessage);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            console.error('API error:', data.error);
            return { success: false, error: data.error };
        }
        
        return {
            success: true,
            data: data
        };
    } catch (error) {
        console.error('Error contributing image:', error);
        return { success: false, error: error.message };
    }
}

async function updateContribution(contributionId, data) {
    try {
        const apiUrl = getApiUrl();
        const token = localStorage.getItem(CONFIG.TOKEN_KEY);
        
        if (!token) {
            console.error('No authentication token found');
            return null;
        }
        
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
        
        const response = await fetch(`${apiUrl}/api/admin/contributions/${contributionId}`, {
            method: 'PUT',
            headers: headers,
            credentials: 'include',
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                console.error('Unauthorized access. Please login again.');
                return null;
            }
            
            // Get error message from response
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const responseData = await response.json();
        
        if (!responseData.success) {
            console.error('API error:', responseData.error);
            return null;
        }
        
        return responseData;
    } catch (error) {
        console.error('Error updating contribution:', error);
        throw error;
    }
}

async function deleteContribution(contributionId) {
    try {
        const apiUrl = getApiUrl();
        const token = localStorage.getItem(CONFIG.TOKEN_KEY);
        
        if (!token) {
            console.error('No authentication token found');
            return null;
        }
        
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
        
        const response = await fetch(`${apiUrl}/api/admin/contributions/${contributionId}`, {
            method: 'DELETE',
            headers: headers,
            credentials: 'include'
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                console.error('Unauthorized access. Please login again.');
                return null;
            }
            
            // Get error message from response
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            console.error('API error:', data.error);
            return null;
        }
        
        return data;
    } catch (error) {
        console.error('Error deleting contribution:', error);
        throw error;
    }
}

async function reviewContribution(contributionId, status, notes = '') {
    try {
        const apiUrl = getApiUrl();
        const token = localStorage.getItem(CONFIG.TOKEN_KEY);
        
        if (!token) {
            console.error('No authentication token found');
            return null;
        }
        
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
        
        const response = await fetch(`${apiUrl}/api/admin/contribution/${contributionId}/review`, {
            method: 'PUT',
            headers: headers,
            credentials: 'include',
            body: JSON.stringify({ status, notes })
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                console.error('Unauthorized access. Please login again.');
                return null;
            }
            
            // Get error message from response
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            console.error('API error:', data.error);
            return null;
        }
        
        return data;
    } catch (error) {
        console.error('Error reviewing contribution:', error);
        throw error;
    }
}

async function fetchCaptionHistory(params = {}) {
    try {
        const apiUrl = getApiUrl();
        const token = localStorage.getItem(CONFIG.TOKEN_KEY);
        
        if (!token) {
            console.error('No authentication token found');
            return { success: false, error: 'No authentication token found' };
        }
        
        const headers = {
            'Authorization': `Bearer ${token}`
        };
        
        // Build query string with all possible parameters
        let queryParams = new URLSearchParams();
        if (params.page) queryParams.append('page', params.page);
        if (params.limit) queryParams.append('limit', params.limit);
        if (params.user_id) queryParams.append('user_id', params.user_id);
        if (params.ai_only) queryParams.append('ai_only', params.ai_only);
        if (params.rating) queryParams.append('rating', params.rating);
        
        const response = await fetch(`${apiUrl}/api/caption-history?${queryParams.toString()}`, {
            method: 'GET',
            headers: headers,
            credentials: 'include'
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                console.error('Unauthorized access. Please login again.');
                return { success: false, error: 'Authentication failed' };
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            console.error('API error:', data.error);
            return { success: false, error: data.error };
        }
        
        return {
            success: true,
            data: {
                captions: data.captions || [],
                total: data.total || 0,
                page: data.page,
                limit: data.limit,
                pages: data.pages
            }
        };
    } catch (error) {
        console.error('Error fetching caption history:', error);
        return { success: false, error: error.message };
    }
}

async function deleteCaptionHistory(imageId) {
    try {
        const apiUrl = getApiUrl();
        const token = localStorage.getItem(CONFIG.TOKEN_KEY);
        
        if (!token) {
            console.error('No authentication token found');
            return { success: false, error: 'No authentication token found' };
        }
        
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
        
        const response = await fetch(`${apiUrl}/api/admin/caption/${imageId}`, {
            method: 'DELETE',
            headers: headers,
            credentials: 'include'
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                console.error('Unauthorized access. Please login again.');
                return { success: false, error: 'Authentication failed' };
            }
            
            // Get error message from response
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            console.error('API error:', data.error);
            return { success: false, error: data.error };
        }
        
        return {
            success: true,
            message: data.message || 'Caption deleted successfully'
        };
    } catch (error) {
        console.error('Error deleting caption:', error);
        return { success: false, error: error.message };
    }
}

// Export all the API functions
export {
    fetchUsers,
    fetchUserById,
    createUser,
    updateUser,
    deleteUser,
    loginUser,
    fetchDashboardStats,
    updateMainChart,
    updateStatsSummary,
    initDashboard,
    fetchContributions,
    updateContribution,
    deleteContribution,
    reviewContribution,
    contributeImage,
    fetchCaptionHistory,
    deleteCaptionHistory,
    fetchTopContributors
}; 
import axios from 'axios';
import Cookies from 'js-cookie';

// Hằng số
const TOKEN_KEY = 'auth_token';
// Sử dụng biến môi trường hoặc giá trị mặc định cho API URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

/**
 * Lưu token vào cả localStorage và cookie
 */
export const saveToken = (token) => {
    console.log(`Saving token: ${token ? token.substring(0, 15) + '...' : 'null or undefined'}`);
    
    if (!token) {
        console.warn('Attempt to save empty token');
        return;
    }
    
    try {
        // Lưu vào localStorage
        localStorage.setItem(TOKEN_KEY, token);
        console.log('Token saved to localStorage');
        
        // Lưu vào cookie
        Cookies.set('token', token, { 
            expires: 30,  // 30 days
            sameSite: 'none',
            secure: true,
            path: '/'
        });
        console.log('Token saved to cookies');
        
        // Kiểm tra xem token đã được lưu chưa
        const savedToken = getToken();
        console.log(`Token verification - Retrieved: ${savedToken ? savedToken.substring(0, 15) + '...' : 'null'}`);
    } catch (error) {
        console.error('Error saving token:', error);
    }
};

/**
 * Lấy token từ localStorage hoặc cookie
 */
export const getToken = () => {
    let token = null;
    
    // Thử lấy từ localStorage trước
    try {
        token = localStorage.getItem(TOKEN_KEY);
        if (token) {
            console.log(`Token found in localStorage: ${token.substring(0, 15)}...`);
            return token;
        }
    } catch (e) {
        console.warn('Error reading from localStorage:', e);
    }
    
    // Nếu không có trong localStorage, thử lấy từ cookie
    try {
        token = Cookies.get('token');
        if (token) {
            console.log(`Token found in cookies: ${token.substring(0, 15)}...`);
            // Cập nhật lại localStorage nếu chỉ có trong cookie
            try {
                localStorage.setItem(TOKEN_KEY, token);
                console.log('Token from cookies synced to localStorage');
            } catch (e) {
                console.warn('Error syncing token to localStorage:', e);
            }
            return token;
        }
    } catch (e) {
        console.warn('Error reading from cookies:', e);
    }
    
    console.log('No token found in storage');
    return null;
};

/**
 * Xóa token khỏi cả localStorage và cookie
 */
export const clearToken = () => {
    console.log('Clearing token from storage');
    try {
        localStorage.removeItem(TOKEN_KEY);
        console.log('Token removed from localStorage');
    } catch (e) {
        console.warn('Error removing from localStorage:', e);
    }
    
    try {
        Cookies.remove('token', { path: '/' });
        console.log('Token removed from cookies');
    } catch (e) {
        console.warn('Error removing from cookies:', e);
    }
    
    // Kiểm tra xem token đã được xóa chưa
    const remainingToken = getToken();
    if (remainingToken) {
        console.warn(`WARNING: Token still exists after clearing: ${remainingToken.substring(0, 15)}...`);
    } else {
        console.log('Token successfully cleared from all storage');
    }
};

// Tạo instance Axios với cấu hình mặc định
const api = axios.create({
    baseURL: API_URL,
    withCredentials: true, // Quan trọng: cho phép gửi cookies
    headers: {
        'Content-Type': 'application/json',
    },
});

// Thêm interceptor cho request để tự động thêm token vào header
api.interceptors.request.use(
    (config) => {
        const token = getToken();
        if (token) {
            console.log(`Adding token to request: ${token.substring(0, 15)}...`);
            config.headers['Authorization'] = `Bearer ${token}`;
        } else {
            console.log('No token available for request');
        }
        return config;
    },
    (error) => {
        console.error('Request interceptor error:', error);
        return Promise.reject(error);
    }
);

// Thêm interceptor cho response để xử lý lỗi
api.interceptors.response.use(
    (response) => {
        // Nếu response chứa token mới, cập nhật
        if (response.data && response.data.token) {
            console.log('New token received in response, updating');
            saveToken(response.data.token);
        }
        
        // Trả về response
        return response;
    },
    (error) => {
        console.error('API error:', error);
        
        // Nếu là lỗi 401 Unauthorized, xóa token và thông báo
        if (error.response && error.response.status === 401) {
            console.warn('401 Unauthorized error detected');
            
            // Chỉ xóa token nếu không phải là lỗi từ các endpoints liên quan đến xác thực
            const skipPathsForTokenClear = ['/login', '/register', '/user'];
            const requestPath = error.config.url;
            
            if (skipPathsForTokenClear.some(path => requestPath.includes(path))) {
                console.log(`Skipping token clear for auth-related path: ${requestPath}`);
            } else {
                console.warn('Clearing auth token due to 401 error');
                clearToken();
                
                // Dispatch event cho AuthContext
                window.dispatchEvent(new CustomEvent('auth-error', { 
                    detail: { message: 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.' } 
                }));
            }
        }
        
        return Promise.reject(error);
    }
);

// Auth methods
export const login = async (username, password) => {
    try {
        console.log(`Đăng nhập người dùng: ${username}`);
        const response = await api.post('/login', { username, password });
        
        // Token được lưu tự động qua interceptor
        return response.data;
    } catch (error) {
        console.error('Lỗi đăng nhập:', error);
        throw error;
    }
};

export const register = async (username, password) => {
    try {
        console.log(`Đăng ký người dùng: ${username}`);
        const response = await api.post('/register', { username, password });
        
        // Token được lưu tự động qua interceptor
        return response.data;
    } catch (error) {
        console.error('Lỗi đăng ký:', error);
        throw error;
    }
};

export const logout = async () => {
    try {
        console.log('Đăng xuất người dùng');
        const response = await api.post('/logout');
        
        clearToken();
        return response.data;
    } catch (error) {
        console.error('Lỗi đăng xuất:', error);
        clearToken(); // Xóa token cả khi API lỗi
        throw error;
    }
};

export const getCurrentUser = async () => {
    try {
        console.log('Lấy thông tin người dùng hiện tại');
        const response = await api.get('/user');
        return response.data;
    } catch (error) {
        console.error('Lỗi lấy thông tin người dùng:', error);
        throw error;
    }
};

// Image methods
export const captionImage = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const headers = {
        'Content-Type': 'multipart/form-data'
    };
    
    try {
        console.log('Gửi yêu cầu tạo caption cho ảnh');
        const response = await api.post('/caption', formData, {
            headers
        });
        return response.data;
    } catch (error) {
        console.error('Lỗi tạo caption:', error);
        throw error;
    }
};

export const contributeImage = async (file, caption, skipAiCaption = false) => {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('userCaption', caption);
    
    if (skipAiCaption) {
        formData.append('skipAiCaption', 'true');
    }
    
    const headers = {
        'Content-Type': 'multipart/form-data'
    };
    
    try {
        console.log('Gửi đóng góp ảnh và caption');
        // Log formData để debug
        console.log('FormData contents:');
        for (let pair of formData.entries()) {
            console.log(pair[0] + ': ' + pair[1]);
        }
        
        const response = await api.post('/contribute', formData, {
            headers
        });
        return response.data;
    } catch (error) {
        console.error('Lỗi đóng góp ảnh:', error);
        throw error;
    }
};

export const getUserContributions = async () => {
    try {
        console.log('Lấy danh sách đóng góp của người dùng');
        const response = await api.get('/user/contributions');
        return response.data;
    } catch (error) {
        console.error('Lỗi lấy danh sách đóng góp:', error);
        throw error;
    }
};

export const updateContribution = async (imageId, caption) => {
    try {
        console.log(`Cập nhật đóng góp: ${imageId}`);
        const response = await api.put(`/contribution/${imageId}`, { caption });
        return response.data;
    } catch (error) {
        console.error('Lỗi cập nhật đóng góp:', error);
        throw error;
    }
};

export const deleteContribution = async (imageId) => {
    try {
        console.log(`Xóa đóng góp: ${imageId}`);
        const response = await api.delete(`/contribution/${imageId}`);
        return response.data;
    } catch (error) {
        console.error('Lỗi xóa đóng góp:', error);
        throw error;
    }
};

export default api; 
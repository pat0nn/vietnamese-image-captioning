import { useState, useEffect } from 'react';
import Head from 'next/head';
import { getToken, API_URL, markNgrokAsConfirmed } from '../utils/requestHelper';
import styles from '../styles/userProfile.module.css';

// Xử lý để lấy base URL từ API_URL
const BASE_URL = API_URL.replace(/\/api$/, '');

export default function TestNgrokDirect() {
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [token, setToken] = useState(null);

  useEffect(() => {
    setToken(getToken());
  }, []);

  const checkEndpoint = async (endpoint, useToken = false) => {
    setStatus('loading');
    setError(null);
    
    try {
      const url = `${API_URL}${endpoint}?_ngrok_skip_browser_warning=true`;
      console.log(`Testing endpoint: ${url}`);
      
      const headers = {};
      if (useToken && token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch(url, { headers });
      
      // Kiểm tra content type
      const contentType = response.headers.get('content-type') || '';
      console.log(`Response content type: ${contentType}`);
      
      if (contentType.includes('text/html')) {
        setError('Received HTML response. You need to confirm the ngrok URL first.');
        setStatus('error');
        return;
      }
      
      const data = await response.json();
      setResult(data);
      setStatus('success');
      
      // Đánh dấu URL đã được xác nhận
      if (API_URL.includes('ngrok')) {
        markNgrokAsConfirmed(API_URL);
      }
    } catch (e) {
      console.error('Error testing endpoint:', e);
      setError(e.message);
      setStatus('error');
    }
  };

  const confirmNgrokManually = () => {
    if (API_URL.includes('ngrok')) {
      // Mở URL ngrok trong tab mới
      window.open(`${API_URL}/ngrok-ready`, '_blank');
    } else {
      alert('Không phải URL ngrok, không cần xác nhận.');
    }
  };

  const checkContributions = async () => {
    if (!token) {
      setError('Bạn chưa đăng nhập. Vui lòng đăng nhập trước.');
      return;
    }
    
    await checkEndpoint('/user/contributions', true);
  };

  return (
    <div className={styles.container}>
      <Head>
        <title>Xác nhận Ngrok URL trực tiếp</title>
      </Head>

      <main className={styles.main}>
        <h1 className={styles.title}>Xác nhận Ngrok URL trực tiếp</h1>
        
        <div className={styles.card} style={{ marginBottom: '20px' }}>
          <h2>Thông tin API</h2>
          <p><strong>API URL:</strong> {API_URL}</p>
          <p><strong>Base URL:</strong> {BASE_URL}</p>
          <p><strong>Token:</strong> {token ? `${token.substring(0, 20)}...` : 'Không có token'}</p>
        </div>

        <div className={styles.buttonContainer}>
          <button
            className={styles.button}
            onClick={confirmNgrokManually}
            style={{ backgroundColor: '#4CAF50' }}
          >
            1. Xác nhận URL Ngrok trước
          </button>
          
          <button
            className={styles.button}
            onClick={() => checkEndpoint('/ngrok-ready')}
            disabled={status === 'loading'}
          >
            2. Kiểm tra Endpoint '/ngrok-ready'
          </button>
          
          <button
            className={styles.button}
            onClick={() => checkEndpoint('/test-auth', true)}
            disabled={status === 'loading'}
          >
            3. Kiểm tra Endpoint '/test-auth'
          </button>
          
          <button
            className={styles.button}
            onClick={checkContributions}
            disabled={status === 'loading'}
          >
            4. Kiểm tra Endpoint '/user/contributions'
          </button>
        </div>

        {status === 'loading' && (
          <div className={styles.card}>
            <h3>Đang kiểm tra...</h3>
            <p>Vui lòng đợi trong giây lát.</p>
          </div>
        )}

        {error && (
          <div className={styles.card} style={{ backgroundColor: '#ffeeee', borderColor: '#ff0000' }}>
            <h3>Lỗi</h3>
            <p>{error}</p>
            <p>
              <strong>Hướng dẫn:</strong> Nếu bạn thấy lỗi về HTML response, hãy nhấn nút "1. Xác nhận URL Ngrok trước" và hoàn thành bước xác nhận trong tab mới. Sau đó thử lại.
            </p>
          </div>
        )}

        {result && (
          <div className={styles.card} style={{ backgroundColor: '#eeffee', borderColor: '#00aa00' }}>
            <h3>Kết quả thành công</h3>
            <pre style={{ overflow: 'auto', maxHeight: '300px', fontSize: '14px' }}>
              {JSON.stringify(result, null, 2)}
            </pre>
            
            {result.contributions && (
              <div style={{ marginTop: '20px' }}>
                <h4>Số lượng đóng góp: {result.contributions.length}</h4>
                {result.contributions.length > 0 && (
                  <p style={{ color: 'green', fontWeight: 'bold' }}>
                    Bạn đã có {result.contributions.length} đóng góp trong database!
                  </p>
                )}
              </div>
            )}
          </div>
        )}
        
        <div className={styles.card} style={{ marginTop: '20px' }}>
          <h2>Hướng dẫn khắc phục</h2>
          <ol>
            <li>Nhấn nút <strong>"1. Xác nhận URL Ngrok trước"</strong> và hoàn thành bước xác nhận trong tab mới.</li>
            <li>Quay lại trang này và nhấn <strong>"2. Kiểm tra Endpoint '/ngrok-ready'"</strong> để xác nhận kết nối thành công.</li>
            <li>Tiếp tục với các nút còn lại theo thứ tự để kiểm tra từng endpoint.</li>
            <li>Nếu tất cả kiểm tra đều thành công, đặc biệt là kiểm tra endpoint '/user/contributions' hiển thị số lượng đóng góp {'>'} 0, nhưng trang hồ sơ vẫn hiển thị "Bạn chưa có đóng góp nào", hãy tải lại trang hồ sơ và thử lại.</li>
          </ol>
        </div>
      </main>
    </div>
  );
} 
import { useState, useEffect } from 'react';
import Head from 'next/head';
import { getToken } from '../utils/requestHelper';
import styles from '../styles/userProfile.module.css';

// Lấy API_URL từ biến môi trường hoặc giá trị mặc định
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';
// Xử lý để lấy base URL từ API_URL
const BASE_URL = API_URL.replace(/\/api$/, '');

export default function TestNgrok() {
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [token, setToken] = useState(null);

  const testEndpoints = async () => {
    setLoading(true);
    setError(null);
    setResults({});

    const testResults = {
      token: getToken(),
      apiUrl: API_URL,
      baseUrl: BASE_URL,
      timestamp: new Date().toISOString(),
      endpoints: {}
    };

    setToken(testResults.token);

    // Thêm tham số ngrok cho tất cả endpoints
    const ngrokParam = API_URL.includes('ngrok') ? '?_ngrok_skip_browser_warning=true' : '';

    try {
      // Test 1: Kiểm tra endpoint ngrok-ready
      try {
        const ngrokReadyResponse = await fetch(`${API_URL}/ngrok-ready${ngrokParam}`);
        const ngrokReadyData = await ngrokReadyResponse.json();
        testResults.endpoints['ngrok-ready'] = {
          status: ngrokReadyResponse.status,
          ok: ngrokReadyResponse.ok,
          data: ngrokReadyData
        };
      } catch (e) {
        testResults.endpoints['ngrok-ready'] = {
          error: e.message
        };
      }

      // Test 2: Kiểm tra endpoint test-auth
      try {
        const headers = {};
        if (testResults.token) {
          headers['Authorization'] = `Bearer ${testResults.token}`;
        }
        
        const testAuthResponse = await fetch(`${API_URL}/test-auth${ngrokParam}`, {
          headers
        });
        const testAuthData = await testAuthResponse.json();
        testResults.endpoints['test-auth'] = {
          status: testAuthResponse.status,
          ok: testAuthResponse.ok,
          data: testAuthData
        };
      } catch (e) {
        testResults.endpoints['test-auth'] = {
          error: e.message
        };
      }

      // Test 3: Kiểm tra endpoint user/contributions
      try {
        const headers = {};
        if (testResults.token) {
          headers['Authorization'] = `Bearer ${testResults.token}`;
        }
        
        const contributionsResponse = await fetch(`${API_URL}/user/contributions${ngrokParam}`, {
          headers
        });

        // Kiểm tra Content-Type của response
        const contentType = contributionsResponse.headers.get('content-type') || '';
        
        if (contentType.includes('text/html')) {
          // Đây là trang HTML, có thể là trang xác nhận ngrok
          testResults.endpoints['user/contributions'] = {
            status: contributionsResponse.status,
            ok: false,
            error: 'Nhận được HTML thay vì JSON. Đây có thể là trang xác nhận ngrok.',
            isHtml: true,
          };
          
          // Lấy text để kiểm tra
          const text = await contributionsResponse.text();
          testResults.endpoints['user/contributions'].preview = text.substring(0, 150) + '...';
        } else {
          // Đây là JSON như mong đợi
          const contributionsData = await contributionsResponse.json();
          testResults.endpoints['user/contributions'] = {
            status: contributionsResponse.status,
            ok: contributionsResponse.ok,
            data: contributionsData,
            contributionsCount: contributionsData.contributions ? contributionsData.contributions.length : 0
          };
        }
      } catch (e) {
        testResults.endpoints['user/contributions'] = {
          error: e.message
        };
      }

      // Test 4: Kiểm tra tệp uploads
      try {
        const uploadTestResponse = await fetch(`${BASE_URL}/uploads/test-image.txt${ngrokParam}`);
        const uploadTestText = await uploadTestResponse.text();
        testResults.endpoints['uploads'] = {
          status: uploadTestResponse.status,
          ok: uploadTestResponse.ok,
          text: uploadTestText
        };
      } catch (e) {
        testResults.endpoints['uploads'] = {
          error: e.message
        };
      }

      setResults(testResults);
    } catch (e) {
      setError(`Lỗi chung: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    testEndpoints();
  }, []);

  const handleManualConfirm = () => {
    // Mở cửa sổ mới đến URL ngrok-ready
    window.open(`${API_URL}/ngrok-ready`, '_blank');
  };

  return (
    <div className={styles.container}>
      <Head>
        <title>Kiểm tra kết nối Ngrok</title>
      </Head>

      <main className={styles.main}>
        <h1 className={styles.title}>Kiểm tra kết nối Ngrok</h1>

        <div className={styles.card} style={{ marginBottom: '20px' }}>
          <h2>Thông tin cấu hình</h2>
          <p><strong>API URL:</strong> {API_URL}</p>
          <p><strong>Base URL:</strong> {BASE_URL}</p>
          <p><strong>Token:</strong> {token ? `${token.substring(0, 20)}...` : 'Không có token'}</p>
        </div>

        <div className={styles.buttonContainer}>
          <button onClick={testEndpoints} className={styles.button} disabled={loading}>
            {loading ? 'Đang kiểm tra...' : 'Kiểm tra lại'}
          </button>
          <button onClick={handleManualConfirm} className={styles.button}>
            Xác nhận URL Ngrok
          </button>
        </div>

        {error && (
          <div className={styles.error}>
            <h3>Lỗi</h3>
            <p>{error}</p>
          </div>
        )}

        <div className={styles.resultsContainer}>
          <h2>Kết quả kiểm tra</h2>

          {loading ? (
            <p>Đang kiểm tra các endpoints...</p>
          ) : (
            <div>
              {Object.entries(results.endpoints || {}).map(([endpoint, result]) => (
                <div key={endpoint} className={`${styles.card} ${result.ok ? styles.success : styles.warning}`}>
                  <h3>{endpoint}</h3>
                  
                  {result.error ? (
                    <div>
                      <p className={styles.error}><strong>Lỗi:</strong> {result.error}</p>
                      {result.isHtml && result.preview && (
                        <div>
                          <p>Đây có thể là trang xác nhận ngrok. Vui lòng nhấn nút "Xác nhận URL Ngrok" ở trên.</p>
                          <pre style={{ fontSize: '12px', backgroundColor: '#f5f5f5', padding: '10px', overflow: 'auto', maxHeight: '100px' }}>
                            {result.preview}
                          </pre>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div>
                      <p><strong>Trạng thái:</strong> {result.status}</p>
                      {endpoint === 'user/contributions' && (
                        <p><strong>Số đóng góp:</strong> {result.contributionsCount || 0}</p>
                      )}
                      {endpoint === 'uploads' && result.text && (
                        <p><strong>Nội dung:</strong> {result.text}</p>
                      )}
                      {result.data && (
                        <details>
                          <summary>Chi tiết dữ liệu</summary>
                          <pre style={{ fontSize: '12px', backgroundColor: '#f5f5f5', padding: '10px', overflow: 'auto' }}>
                            {JSON.stringify(result.data, null, 2)}
                          </pre>
                        </details>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
} 
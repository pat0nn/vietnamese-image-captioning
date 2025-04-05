import { Inter } from 'next/font/google';
import { AuthProvider } from '../components/Auth/AuthContext';
import AuthWrapper from '../components/Auth/AuthWrapper';
import TokenRefresher from '../components/Auth/TokenRefresher';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import "../styles/globals.css";
 
// If loading a variable font, you don't need to specify the font weight
const inter = Inter({ subsets: ['latin'] });
 
export default function MyApp({ Component, pageProps }) {
  return (
    <AuthProvider>
      <AuthWrapper>
        <TokenRefresher />
        <main className={inter.className}>
          <Component {...pageProps} />
          <ToastContainer position="bottom-right" />
        </main>
      </AuthWrapper>
    </AuthProvider>
  );
}
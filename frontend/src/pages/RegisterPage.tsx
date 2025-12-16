import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { RegisterForm } from '../components/auth/RegisterForm';
import { Layout } from 'antd';

const { Content } = Layout;

export const RegisterPage = () => {
  const { isAuthenticated } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  return (
    <Layout style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      <Content
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          padding: 24,
        }}
      >
        <div style={{ backgroundColor: 'white', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.1)', width: '100%', maxWidth: 600 }}>
          <RegisterForm />
        </div>
      </Content>
    </Layout>
  );
};

import { useState } from 'react';
import { Form, Input, Button, Alert, Typography, Divider } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useAuthStore } from '../../stores/authStore';
import { useNavigate, Link } from 'react-router-dom';

const { Title, Text } = Typography;

export const LoginForm = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const { login, isLoading, error, clearError } = useAuthStore();
  const [localError, setLocalError] = useState<string | null>(null);

  const onFinish = async (values: { email: string; password: string }) => {
    setLocalError(null);
    clearError();
    try {
      await login(values.email, values.password);
      navigate('/dashboard');
    } catch (err: any) {
      setLocalError(err.response?.data?.detail || 'Login failed');
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: '0 auto', padding: '40px 20px' }}>
      <div style={{ textAlign: 'center', marginBottom: 32 }}>
        <Title level={2} style={{ marginBottom: 8 }}>
          Welcome Back
        </Title>
        <Text type="secondary">Sign in to continue your wellness journey</Text>
      </div>

      {(error || localError) && (
        <Alert
          message={error || localError}
          type="error"
          showIcon
          closable
          onClose={() => {
            clearError();
            setLocalError(null);
          }}
          style={{ marginBottom: 16 }}
        />
      )}

      <Form
        form={form}
        name="login"
        onFinish={onFinish}
        layout="vertical"
        requiredMark={false}
      >
        <Form.Item
          name="email"
          label="Email"
          rules={[
            { required: true, message: 'Please enter your email' },
            { type: 'email', message: 'Please enter a valid email' },
          ]}
        >
          <Input
            prefix={<UserOutlined />}
            placeholder="your@email.com"
            size="large"
          />
        </Form.Item>

        <Form.Item
          name="password"
          label="Password"
          rules={[{ required: true, message: 'Please enter your password' }]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="Password"
            size="large"
          />
        </Form.Item>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            loading={isLoading}
            block
            size="large"
            style={{ backgroundColor: '#2D7D90' }}
          >
            Sign In
          </Button>
        </Form.Item>
      </Form>

      <Divider>New to Firefly?</Divider>

      <Link to="/register">
        <Button block size="large">
          Create an Account
        </Button>
      </Link>

      <div style={{ textAlign: 'center', marginTop: 24 }}>
        <Text type="secondary" style={{ fontSize: 12 }}>
          Your data is encrypted and secure.
        </Text>
      </div>
    </div>
  );
};

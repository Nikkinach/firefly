import { useState } from 'react';
import { Form, Input, Button, Alert, Typography, Checkbox, Steps, Card } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { useAuthStore } from '../../stores/authStore';
import { useNavigate, Link } from 'react-router-dom';

const { Title, Text, Paragraph } = Typography;

export const RegisterForm = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const { register, isLoading, error, clearError } = useAuthStore();
  const [currentStep, setCurrentStep] = useState(0);
  const [localError, setLocalError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    display_name: '',
    has_adhd: false,
    has_autism_spectrum: false,
    has_anxiety: false,
    has_depression: false,
  });

  const onFinishStep1 = (values: any) => {
    setFormData({ ...formData, ...values });
    setCurrentStep(1);
  };

  const onFinishStep2 = async (values: any) => {
    const finalData = { ...formData, ...values };
    setLocalError(null);
    clearError();

    try {
      await register(finalData);
      navigate('/onboarding');
    } catch (err: any) {
      setLocalError(err.response?.data?.detail || 'Registration failed');
    }
  };

  const steps = [
    { title: 'Account', description: 'Basic info' },
    { title: 'Profile', description: 'About you' },
  ];

  return (
    <div style={{ maxWidth: 500, margin: '0 auto', padding: '40px 20px' }}>
      <div style={{ textAlign: 'center', marginBottom: 32 }}>
        <Title level={2} style={{ marginBottom: 8 }}>
          Create Your Account
        </Title>
        <Text type="secondary">Start your personalized wellness journey</Text>
      </div>

      <Steps
        current={currentStep}
        items={steps}
        style={{ marginBottom: 32 }}
        size="small"
      />

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

      {currentStep === 0 && (
        <Form
          form={form}
          name="register-step1"
          onFinish={onFinishStep1}
          layout="vertical"
          requiredMark={false}
          initialValues={formData}
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
              prefix={<MailOutlined />}
              placeholder="your@email.com"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="password"
            label="Password"
            rules={[
              { required: true, message: 'Please create a password' },
              { min: 8, message: 'Password must be at least 8 characters' },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="At least 8 characters"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="display_name"
            label="Display Name (Optional)"
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="How should we call you?"
              size="large"
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block size="large">
              Continue
            </Button>
          </Form.Item>
        </Form>
      )}

      {currentStep === 1 && (
        <Form
          name="register-step2"
          onFinish={onFinishStep2}
          layout="vertical"
          initialValues={formData}
        >
          <Card style={{ marginBottom: 16, backgroundColor: '#f9f9f9' }}>
            <Paragraph style={{ marginBottom: 16 }}>
              <strong>Optional:</strong> Share any conditions that apply to you.
              This helps us customize your experience with tools that actually work for YOUR brain.
            </Paragraph>
            <Text type="secondary" style={{ fontSize: 12 }}>
              You can always update this later in settings.
            </Text>
          </Card>

          <Form.Item name="has_adhd" valuePropName="checked">
            <Checkbox>
              <strong>ADHD</strong>
              <br />
              <Text type="secondary" style={{ fontSize: 12 }}>
                Time blindness support, task breakdown, dopamine management
              </Text>
            </Checkbox>
          </Form.Item>

          <Form.Item name="has_autism_spectrum" valuePropName="checked">
            <Checkbox>
              <strong>Autism Spectrum</strong>
              <br />
              <Text type="secondary" style={{ fontSize: 12 }}>
                Sensory tracking, emotion scaffolding, routine support
              </Text>
            </Checkbox>
          </Form.Item>

          <Form.Item name="has_anxiety" valuePropName="checked">
            <Checkbox>
              <strong>Anxiety</strong>
              <br />
              <Text type="secondary" style={{ fontSize: 12 }}>
                Grounding techniques, breathing exercises, thought reframing
              </Text>
            </Checkbox>
          </Form.Item>

          <Form.Item name="has_depression" valuePropName="checked">
            <Checkbox>
              <strong>Depression</strong>
              <br />
              <Text type="secondary" style={{ fontSize: 12 }}>
                Behavioral activation, mood tracking, energy management
              </Text>
            </Checkbox>
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
              Create Account
            </Button>
          </Form.Item>

          <Button
            onClick={() => setCurrentStep(0)}
            block
            style={{ marginBottom: 16 }}
          >
            Back
          </Button>

          <div style={{ textAlign: 'center' }}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              By creating an account, you agree to our Terms of Service and Privacy Policy.
              Your data is encrypted and you control what you share.
            </Text>
          </div>
        </Form>
      )}

      <div style={{ textAlign: 'center', marginTop: 24 }}>
        <Text>
          Already have an account?{' '}
          <Link to="/login">Sign in</Link>
        </Text>
      </div>
    </div>
  );
};

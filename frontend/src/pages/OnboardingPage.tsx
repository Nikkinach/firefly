import { useState } from 'react';
import { Card, Steps, Typography, Slider, Button, Radio, Checkbox, Space } from 'antd';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { api } from '../services/api';

const { Title, Text, Paragraph } = Typography;

export const OnboardingPage = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [currentStep, setCurrentStep] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  const [preferences, setPreferences] = useState({
    theme: 'calm_light',
    animation_speed: 'normal',
    sound_enabled: true,
    morning_checkin_time: '08:00',
    evening_reflection_time: '20:00',
    max_notifications_per_day: 3,
  });

  const steps = [
    { title: 'Welcome', description: 'Introduction' },
    { title: 'Visual', description: 'Look & feel' },
    { title: 'Notifications', description: 'Reminders' },
    { title: 'Complete', description: 'All set!' },
  ];

  const handleFinish = async () => {
    setIsLoading(true);
    try {
      await api.updatePreferences(preferences);
      navigate('/dashboard');
    } catch (error) {
      console.error('Failed to save preferences:', error);
      navigate('/dashboard');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: '0 auto', padding: 24 }}>
      <Steps
        current={currentStep}
        items={steps}
        style={{ marginBottom: 32 }}
        size="small"
      />

      {currentStep === 0 && (
        <Card>
          <div style={{ textAlign: 'center', marginBottom: 24 }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>✨ 🔥 ✨</div>
            <Title level={2}>Welcome to Firefly</Title>
            <Paragraph style={{ fontSize: 16 }}>
              Your personal companion for mental wellness.
            </Paragraph>
            <Paragraph type="secondary">
              "No judgment, just gentle support"
            </Paragraph>
          </div>

          <Paragraph>
            Firefly is designed to help you:
          </Paragraph>
          <ul>
            <li>Track your mood and emotions</li>
            <li>Get personalized intervention recommendations</li>
            <li>Build healthy coping strategies</li>
            <li>Understand your patterns over time</li>
          </ul>

          {(user?.has_adhd || user?.has_autism_spectrum) && (
            <Card style={{ backgroundColor: '#f0f9ff', marginTop: 16 }}>
              <Text strong>Special features enabled for you:</Text>
              <br />
              {user?.has_adhd && (
                <Text>• ADHD tools: Time blindness support, task breakdown, focus reminders</Text>
              )}
              <br />
              {user?.has_autism_spectrum && (
                <Text>• ASD tools: Sensory tracking, emotion scaffolding, routine support</Text>
              )}
            </Card>
          )}

          <Button
            type="primary"
            block
            size="large"
            onClick={() => setCurrentStep(1)}
            style={{ marginTop: 24, backgroundColor: '#2D7D90' }}
          >
            Get Started
          </Button>
        </Card>
      )}

      {currentStep === 1 && (
        <Card>
          <Title level={4}>Customize Your Experience</Title>
          <Paragraph>
            Adjust these settings to make Firefly comfortable for you.
          </Paragraph>

          <div style={{ marginBottom: 24 }}>
            <Text strong>Theme</Text>
            <Radio.Group
              value={preferences.theme}
              onChange={(e) =>
                setPreferences({ ...preferences, theme: e.target.value })
              }
              style={{ display: 'block', marginTop: 8 }}
            >
              <Space direction="vertical">
                <Radio value="calm_light">🌤️ Calm Light - Soft, gentle colors</Radio>
                <Radio value="calm_dark">🌙 Calm Dark - Easy on the eyes</Radio>
                <Radio value="high_contrast">⬛ High Contrast - Maximum clarity</Radio>
              </Space>
            </Radio.Group>
          </div>

          <div style={{ marginBottom: 24 }}>
            <Text strong>Animation Speed</Text>
            <Radio.Group
              value={preferences.animation_speed}
              onChange={(e) =>
                setPreferences({ ...preferences, animation_speed: e.target.value })
              }
              style={{ display: 'block', marginTop: 8 }}
            >
              <Space direction="vertical">
                <Radio value="none">No animations</Radio>
                <Radio value="slow">Slow animations</Radio>
                <Radio value="normal">Normal animations</Radio>
              </Space>
            </Radio.Group>
          </div>

          <div style={{ marginBottom: 24 }}>
            <Checkbox
              checked={preferences.sound_enabled}
              onChange={(e) =>
                setPreferences({ ...preferences, sound_enabled: e.target.checked })
              }
            >
              Enable gentle sounds
            </Checkbox>
          </div>

          <Space style={{ width: '100%' }}>
            <Button onClick={() => setCurrentStep(0)}>Back</Button>
            <Button
              type="primary"
              onClick={() => setCurrentStep(2)}
              style={{ backgroundColor: '#2D7D90' }}
            >
              Continue
            </Button>
          </Space>
        </Card>
      )}

      {currentStep === 2 && (
        <Card>
          <Title level={4}>Reminder Settings</Title>
          <Paragraph>
            Gentle reminders help build consistent check-in habits. You can change these anytime.
          </Paragraph>

          <div style={{ marginBottom: 24 }}>
            <Text strong>Morning Check-in Time</Text>
            <br />
            <Radio.Group
              value={preferences.morning_checkin_time}
              onChange={(e) =>
                setPreferences({
                  ...preferences,
                  morning_checkin_time: e.target.value,
                })
              }
              style={{ marginTop: 8 }}
            >
              <Space wrap>
                <Radio.Button value="07:00">7:00 AM</Radio.Button>
                <Radio.Button value="08:00">8:00 AM</Radio.Button>
                <Radio.Button value="09:00">9:00 AM</Radio.Button>
                <Radio.Button value="10:00">10:00 AM</Radio.Button>
              </Space>
            </Radio.Group>
          </div>

          <div style={{ marginBottom: 24 }}>
            <Text strong>Evening Reflection Time</Text>
            <br />
            <Radio.Group
              value={preferences.evening_reflection_time}
              onChange={(e) =>
                setPreferences({
                  ...preferences,
                  evening_reflection_time: e.target.value,
                })
              }
              style={{ marginTop: 8 }}
            >
              <Space wrap>
                <Radio.Button value="19:00">7:00 PM</Radio.Button>
                <Radio.Button value="20:00">8:00 PM</Radio.Button>
                <Radio.Button value="21:00">9:00 PM</Radio.Button>
                <Radio.Button value="22:00">10:00 PM</Radio.Button>
              </Space>
            </Radio.Group>
          </div>

          <div style={{ marginBottom: 24 }}>
            <Text strong>Max Notifications Per Day: {preferences.max_notifications_per_day}</Text>
            <Slider
              min={1}
              max={5}
              value={preferences.max_notifications_per_day}
              onChange={(value) =>
                setPreferences({ ...preferences, max_notifications_per_day: value })
              }
              marks={{ 1: '1', 3: '3', 5: '5' }}
              style={{ marginTop: 8 }}
            />
          </div>

          <Space style={{ width: '100%' }}>
            <Button onClick={() => setCurrentStep(1)}>Back</Button>
            <Button
              type="primary"
              onClick={() => setCurrentStep(3)}
              style={{ backgroundColor: '#2D7D90' }}
            >
              Continue
            </Button>
          </Space>
        </Card>
      )}

      {currentStep === 3 && (
        <Card>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 64, marginBottom: 16 }}>🎉</div>
            <Title level={2}>You're All Set!</Title>
            <Paragraph style={{ fontSize: 16 }}>
              Your Firefly experience is now personalized for you.
            </Paragraph>

            <Card style={{ backgroundColor: '#f0f9ff', marginBottom: 24 }}>
              <Text strong>What's next?</Text>
              <br />
              <Text>Start with your first mood check-in to begin building insights.</Text>
            </Card>

            <Button
              type="primary"
              block
              size="large"
              loading={isLoading}
              onClick={handleFinish}
              style={{ backgroundColor: '#2D7D90' }}
            >
              Go to Dashboard
            </Button>

            <Button
              type="link"
              block
              onClick={() => setCurrentStep(0)}
              style={{ marginTop: 8 }}
            >
              Review settings
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
};

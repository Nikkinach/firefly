import { MainLayout } from '../components/layout/MainLayout';
import { Card, Typography, Button, Space, Divider, Alert, Row, Col, Avatar } from 'antd';
import { PhoneOutlined, MessageOutlined, HeartOutlined, SafetyOutlined, GlobalOutlined, TeamOutlined } from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;

// Indian Crisis Resources
const INDIAN_HOTLINES = [
  {
    name: 'Vandrevala Foundation',
    number: '1860-2662-345',
    description: '24/7 multilingual mental health support',
    type: 'call',
    color: '#4ADEB7',
  },
  {
    name: 'iCall (TISS)',
    number: '9152987821',
    description: 'Psychosocial helpline Mon-Sat 8am-10pm',
    type: 'call',
    color: '#FCD34D',
  },
  {
    name: 'AASRA',
    number: '9820466726',
    description: '24/7 crisis intervention',
    type: 'call',
    color: '#F59E0B',
  },
  {
    name: 'Snehi',
    number: '044-24640050',
    description: 'Emotional support 24/7',
    type: 'call',
    color: '#7A899C',
  },
  {
    name: 'Nimhans Helpline',
    number: '080-46110007',
    description: 'National mental health support',
    type: 'call',
    color: '#4ADEB7',
  },
  {
    name: 'Women Helpline',
    number: '181',
    description: 'Women in distress support',
    type: 'call',
    color: '#F59E0B',
  },
];

export const CrisisPage = () => {
  return (
    <MainLayout>
      <div style={{ padding: '20px', maxWidth: 1000, margin: '0 auto' }}>
        {/* Hero Section */}
        <div
          className="fade-in-up"
          style={{
            background: 'linear-gradient(135deg, #2A1F4A 0%, #1C2340 100%)',
            padding: '24px 32px',
            borderRadius: 16,
            marginBottom: 24,
            textAlign: 'center',
            border: '1px solid rgba(74, 222, 183, 0.2)',
          }}
        >
          <SafetyOutlined style={{ fontSize: 40, color: '#4ADEB7', marginBottom: 12 }} />
          <Title level={2} style={{ color: '#FFFFFF', marginBottom: 8 }}>
            Safety Resources
          </Title>
          <Text style={{ color: '#D1D5DB', fontSize: 16 }}>
            You matter. Support is always available.
          </Text>
        </div>

        {/* Emergency Alert */}
        <Alert
          message={
            <span style={{ fontSize: 16, fontWeight: 600 }}>
              If you are in immediate danger, call <strong>112</strong> (Emergency Services)
            </span>
          }
          type="error"
          showIcon
          style={{ marginBottom: 24, borderRadius: 12, padding: '12px 16px' }}
        />

        {/* Crisis Hotlines */}
        <Card
          style={{ marginBottom: 24, borderRadius: 16 }}
          bodyStyle={{ padding: 20 }}
        >
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 20 }}>
            <Avatar
              size={48}
              style={{ backgroundColor: 'rgba(74, 222, 183, 0.2)', border: '2px solid #4ADEB7', marginRight: 12 }}
              icon={<PhoneOutlined style={{ color: '#4ADEB7', fontSize: 24 }} />}
            />
            <div>
              <Title level={4} style={{ color: '#D1D5DB', marginBottom: 0 }}>
                Crisis Helplines (India)
              </Title>
              <Text style={{ color: '#9CA3AF', fontSize: 13 }}>
                Confidential, professional support available
              </Text>
            </div>
          </div>

          <Row gutter={[16, 16]}>
            {INDIAN_HOTLINES.map((hotline, index) => (
              <Col xs={24} md={12} key={index}>
                <Card
                  size="small"
                  style={{
                    backgroundColor: 'rgba(42, 31, 74, 0.4)',
                    border: `1px solid ${hotline.color}40`,
                    borderRadius: 12,
                  }}
                  bodyStyle={{ padding: 16 }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ flex: 1 }}>
                      <Text strong style={{ fontSize: 15, color: hotline.color, display: 'block' }}>
                        {hotline.name}
                      </Text>
                      <Text style={{ fontSize: 12, color: '#9CA3AF' }}>
                        {hotline.description}
                      </Text>
                    </div>
                    <Button
                      type="primary"
                      size="large"
                      icon={<PhoneOutlined />}
                      href={`tel:${hotline.number.replace(/-/g, '')}`}
                      style={{
                        backgroundColor: hotline.color,
                        border: 'none',
                        color: '#0A0F29',
                        fontWeight: 600,
                        borderRadius: 10,
                        height: 44,
                      }}
                    >
                      {hotline.number}
                    </Button>
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
        </Card>

        {/* Safety Plan */}
        <Card
          style={{ marginBottom: 24, borderRadius: 16 }}
          bodyStyle={{ padding: 20 }}
        >
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
            <Avatar
              size={48}
              style={{ backgroundColor: 'rgba(252, 211, 77, 0.2)', border: '2px solid #FCD34D', marginRight: 12 }}
              icon={<HeartOutlined style={{ color: '#FCD34D', fontSize: 24 }} />}
            />
            <Title level={4} style={{ color: '#D1D5DB', marginBottom: 0 }}>
              Safety Plan
            </Title>
          </div>
          <Paragraph style={{ color: '#D1D5DB', fontSize: 14, marginBottom: 16 }}>
            A safety plan is a personalized, practical plan that can help you through a crisis.
            It includes warning signs, coping strategies, and people to contact.
          </Paragraph>
          <Button
            type="primary"
            style={{
              backgroundColor: '#FCD34D',
              border: 'none',
              color: '#0A0F29',
              fontWeight: 600,
              borderRadius: 10,
              height: 44,
            }}
            onClick={() => alert('Safety Plan Builder - Coming Soon')}
          >
            Build Your Safety Plan
          </Button>
        </Card>

        {/* Coping Strategies */}
        <Card
          style={{ marginBottom: 24, borderRadius: 16 }}
          bodyStyle={{ padding: 20 }}
        >
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
            <Avatar
              size={48}
              style={{ backgroundColor: 'rgba(122, 137, 156, 0.2)', border: '2px solid #7A899C', marginRight: 12 }}
              icon={<GlobalOutlined style={{ color: '#7A899C', fontSize: 24 }} />}
            />
            <Title level={4} style={{ color: '#D1D5DB', marginBottom: 0 }}>
              Grounding Techniques
            </Title>
          </div>
          <Row gutter={[12, 12]}>
            <Col xs={24} sm={8}>
              <Button
                block
                style={{
                  height: 60,
                  backgroundColor: 'rgba(74, 222, 183, 0.1)',
                  border: '1px solid rgba(74, 222, 183, 0.3)',
                  color: '#4ADEB7',
                  borderRadius: 10,
                  fontWeight: 600,
                }}
                onClick={() => alert('Box Breathing Exercise')}
              >
                🌬️ Box Breathing
              </Button>
            </Col>
            <Col xs={24} sm={8}>
              <Button
                block
                style={{
                  height: 60,
                  backgroundColor: 'rgba(252, 211, 77, 0.1)',
                  border: '1px solid rgba(252, 211, 77, 0.3)',
                  color: '#FCD34D',
                  borderRadius: 10,
                  fontWeight: 600,
                }}
                onClick={() => alert('5-4-3-2-1 Grounding')}
              >
                🎯 5-4-3-2-1 Grounding
              </Button>
            </Col>
            <Col xs={24} sm={8}>
              <Button
                block
                style={{
                  height: 60,
                  backgroundColor: 'rgba(245, 158, 11, 0.1)',
                  border: '1px solid rgba(245, 158, 11, 0.3)',
                  color: '#F59E0B',
                  borderRadius: 10,
                  fontWeight: 600,
                }}
                onClick={() => alert('TIPP Skills')}
              >
                ❄️ TIPP Skills
              </Button>
            </Col>
          </Row>
        </Card>

        <Divider style={{ borderColor: 'rgba(74, 222, 183, 0.2)' }} />

        <div style={{ textAlign: 'center', padding: '12px 0' }}>
          <Text style={{ color: '#9CA3AF', fontSize: 13 }}>
            These resources are always available here. You can access them anytime from the Safety menu.
          </Text>
        </div>
      </div>
    </MainLayout>
  );
};

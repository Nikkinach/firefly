import { MainLayout } from '../components/layout/MainLayout';
import { MoodCheckin } from '../components/checkin/MoodCheckin';
import { Typography, Row, Col } from 'antd';
import { HeartOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

export const CheckinPage = () => {
  return (
    <MainLayout>
      <div style={{ padding: '24px', maxWidth: 1400, margin: '0 auto' }}>
        {/* Hero Header - matching Analytics style */}
        <div
          className="hero-section fade-in-up"
          style={{
            background: 'linear-gradient(135deg, #1C2340 0%, #0A0F29 100%)',
          }}
        >
          <Row align="middle" gutter={24}>
            <Col xs={24}>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
                <HeartOutlined style={{ fontSize: 48, marginRight: 16, color: '#4ADEB7' }} className="float-animation" />
                <div>
                  <Title level={1} style={{ color: '#FFFFFF', marginBottom: 0 }}>
                    Daily Check-in
                  </Title>
                  <Text style={{ color: '#D1D5DB', fontSize: 16 }}>
                    Your feelings are valid. Let's explore them together.
                  </Text>
                </div>
              </div>
            </Col>
          </Row>
        </div>

        {/* Check-in Component */}
        <MoodCheckin />
      </div>
    </MainLayout>
  );
};

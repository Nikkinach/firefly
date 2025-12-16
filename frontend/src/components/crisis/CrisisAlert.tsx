import { Card, Button, Typography, Space, Divider, Alert } from 'antd';
import { PhoneOutlined, MessageOutlined, HeartOutlined } from '@ant-design/icons';
import type { CrisisResources } from '../../types';
import { api } from '../../services/api';

const { Title, Text, Paragraph } = Typography;

interface Props {
  resources: CrisisResources;
  onSafeNow?: () => void;
}

export const CrisisAlert = ({ resources, onSafeNow }: Props) => {
  const handleSafeNow = async () => {
    try {
      await api.markSafe();
      onSafeNow?.();
    } catch (error) {
      console.error('Error marking safe:', error);
      onSafeNow?.();
    }
  };

  return (
    <div style={{ maxWidth: 500, margin: '0 auto', padding: 20 }}>
      <Card
        style={{
          backgroundColor: '#fff7e6',
          borderColor: '#ffd591',
          textAlign: 'center',
        }}
      >
        <HeartOutlined style={{ fontSize: 48, color: '#fa8c16', marginBottom: 16 }} />

        <Title level={3}>We noticed you might be going through a really hard time.</Title>

        <Paragraph style={{ fontSize: 18, fontWeight: 500, color: '#fa541c' }}>
          You matter.
        </Paragraph>

        <Alert
          message={resources.message}
          type="warning"
          showIcon
          style={{ marginBottom: 24, textAlign: 'left' }}
        />

        <Title level={4} style={{ marginBottom: 16 }}>
          If you're having thoughts of suicide, please reach out:
        </Title>

        <Space direction="vertical" style={{ width: '100%' }}>
          {resources.hotlines.map((hotline, index) => (
            <Card
              key={index}
              style={{
                backgroundColor: '#fff',
                textAlign: 'left',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
                {hotline.type === 'call' ? (
                  <PhoneOutlined style={{ fontSize: 24, color: '#1890ff', marginRight: 12 }} />
                ) : (
                  <MessageOutlined style={{ fontSize: 24, color: '#52c41a', marginRight: 12 }} />
                )}
                <div>
                  <Text strong style={{ fontSize: 16 }}>{hotline.name}</Text>
                  <br />
                  <Text type="secondary">{hotline.description}</Text>
                </div>
              </div>
              <Button
                type="primary"
                size="large"
                block
                href={hotline.type === 'call' ? `tel:${hotline.number}` : undefined}
                style={{
                  backgroundColor: hotline.type === 'call' ? '#1890ff' : '#52c41a',
                  height: 48,
                  fontSize: 18,
                }}
              >
                {hotline.type === 'call' ? (
                  <>
                    <PhoneOutlined /> Call {hotline.number}
                  </>
                ) : (
                  <>
                    <MessageOutlined /> Text {hotline.number}
                  </>
                )}
              </Button>
            </Card>
          ))}
        </Space>

        <Divider />

        <Button
          size="large"
          block
          onClick={handleSafeNow}
          style={{ marginBottom: 16 }}
        >
          I'm Safe Right Now
        </Button>

        <Text type="secondary" style={{ fontSize: 12 }}>
          These resources are always available in Settings &gt; Safety Resources
        </Text>
      </Card>
    </div>
  );
};

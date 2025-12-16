import { useState } from 'react';
import { Card, Button, Tag, Typography, Progress, Rate, Space, Modal, Input } from 'antd';
import { ClockCircleOutlined, ThunderboltOutlined, PlayCircleOutlined } from '@ant-design/icons';
import type { Recommendation } from '../../types';
import { api } from '../../services/api';

const { Text, Paragraph } = Typography;
const { TextArea } = Input;

interface Props {
  recommendation: Recommendation;
}

export const InterventionCard = ({ recommendation }: Props) => {
  const [isActive, setIsActive] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [showFeedback, setShowFeedback] = useState(false);
  const [rating, setRating] = useState(0);
  const [feedbackText, setFeedbackText] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return secs > 0 ? `${minutes}m ${secs}s` : `${minutes}m`;
  };

  const startIntervention = async () => {
    setIsLoading(true);
    try {
      const session = await api.startSession({
        intervention_id: recommendation.intervention_id,
        started_at: new Date().toISOString(),
        context_emotion: 'current',
      });
      setSessionId(session.id);
      setIsActive(true);
      setTimeRemaining(recommendation.duration_seconds);

      // Start countdown
      const interval = setInterval(() => {
        setTimeRemaining((prev) => {
          if (prev <= 1) {
            clearInterval(interval);
            setShowFeedback(true);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } catch (error) {
      console.error('Failed to start session:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const completeSession = async () => {
    if (!sessionId) return;

    setIsLoading(true);
    try {
      await api.completeSession(sessionId, {
        completed_at: new Date().toISOString(),
        was_completed: true,
        effectiveness_rating: rating,
        feedback_text: feedbackText || undefined,
      });
      setShowFeedback(false);
      setIsActive(false);
      setSessionId(null);
      setRating(0);
      setFeedbackText('');
    } catch (error) {
      console.error('Failed to complete session:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const skipSession = async () => {
    if (!sessionId) return;

    try {
      await api.skipSession(sessionId);
      setIsActive(false);
      setSessionId(null);
    } catch (error) {
      console.error('Failed to skip session:', error);
    }
  };

  const getEffortColor = (level: string) => {
    switch (level) {
      case 'minimal':
        return '#52c41a';
      case 'low':
        return '#73d13d';
      case 'medium':
        return '#faad14';
      case 'high':
        return '#fa8c16';
      default:
        return '#d9d9d9';
    }
  };

  if (isActive) {
    return (
      <Card style={{ marginBottom: 16, backgroundColor: '#f0f9ff' }}>
        <div style={{ textAlign: 'center' }}>
          <Text strong style={{ fontSize: 18 }}>{recommendation.name}</Text>
          <div style={{ margin: '24px 0' }}>
            <Progress
              type="circle"
              percent={Math.round(
                ((recommendation.duration_seconds - timeRemaining) /
                  recommendation.duration_seconds) *
                  100
              )}
              format={() => formatDuration(timeRemaining)}
              size={120}
              strokeColor="#2D7D90"
            />
          </div>
          <Paragraph style={{ fontSize: 16, marginBottom: 24 }}>
            {recommendation.short_description}
          </Paragraph>
          <Space>
            <Button onClick={skipSession}>End Early</Button>
            <Button
              type="primary"
              onClick={() => {
                setTimeRemaining(0);
                setShowFeedback(true);
              }}
            >
              Done
            </Button>
          </Space>
        </div>

        <Modal
          title="How did that feel?"
          open={showFeedback}
          onOk={completeSession}
          onCancel={() => setShowFeedback(false)}
          confirmLoading={isLoading}
          okText="Submit Feedback"
        >
          <div style={{ textAlign: 'center', marginBottom: 16 }}>
            <Text>Rate this intervention:</Text>
            <div style={{ marginTop: 8 }}>
              <Rate
                value={rating}
                onChange={setRating}
                tooltips={['Not helpful', 'Slightly', 'Neutral', 'Helpful', 'Very helpful']}
              />
            </div>
          </div>
          <TextArea
            rows={3}
            placeholder="Any additional thoughts? (optional)"
            value={feedbackText}
            onChange={(e) => setFeedbackText(e.target.value)}
          />
        </Modal>
      </Card>
    );
  }

  return (
    <Card
      style={{ marginBottom: 16 }}
      hoverable
      actions={[
        <Button
          type="primary"
          icon={<PlayCircleOutlined />}
          onClick={startIntervention}
          loading={isLoading}
          style={{ backgroundColor: '#2D7D90' }}
        >
          Start
        </Button>,
      ]}
    >
      <div style={{ marginBottom: 12 }}>
        <Text strong style={{ fontSize: 16 }}>{recommendation.name}</Text>
        <div style={{ marginTop: 8 }}>
          <Tag icon={<ClockCircleOutlined />}>
            {formatDuration(recommendation.duration_seconds)}
          </Tag>
          <Tag
            icon={<ThunderboltOutlined />}
            color={getEffortColor(recommendation.effort_level)}
          >
            {recommendation.effort_level} effort
          </Tag>
        </div>
      </div>

      <Paragraph style={{ marginBottom: 12 }}>{recommendation.short_description}</Paragraph>

      <div
        style={{
          backgroundColor: '#f5f5f5',
          padding: 12,
          borderRadius: 8,
          marginBottom: 8,
        }}
      >
        <Text type="secondary" style={{ fontSize: 12 }}>
          <strong>Why this?</strong> {recommendation.why_recommended}
        </Text>
      </div>

      <Text type="secondary" style={{ fontSize: 12 }}>
        Predicted effectiveness: {Math.round(recommendation.predicted_effectiveness * 100)}%
      </Text>
    </Card>
  );
};

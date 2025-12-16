import { useEffect, useState } from 'react';
import { MainLayout } from '../components/layout/MainLayout';
import {
  Card,
  Row,
  Col,
  Typography,
  Button,
  Input,
  List,
  Tag,
  Spin,
  Alert,
  Modal,
  Progress,
  Divider,
  Badge,
  Statistic,
} from 'antd';
import {
  EditOutlined,
  SmileOutlined,
  MehOutlined,
  FrownOutlined,
  WarningOutlined,
  BookOutlined,
  FireOutlined,
  HeartOutlined,
  ThunderboltOutlined,
  TagsOutlined,
} from '@ant-design/icons';
import { api } from '../services/api';
import type { Checkin } from '../types';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

export const JournalPage = () => {
  const [checkins, setCheckins] = useState<Checkin[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showNewEntry, setShowNewEntry] = useState(false);
  const [journalText, setJournalText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState<Checkin | null>(null);
  const [showAnalytics, setShowAnalytics] = useState(false);

  useEffect(() => {
    fetchJournals();
  }, []);

  const fetchJournals = async () => {
    try {
      const data = await api.getCheckins(1, 50);
      const withJournals = data.checkins.filter((c) => c.journal_text && c.journal_text.length > 0);
      setCheckins(withJournals);
    } catch (err) {
      setError('Failed to load journal entries');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyzeEntry = (entry: Checkin) => {
    setSelectedEntry(entry);
    setShowAnalytics(true);
  };

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return <SmileOutlined style={{ color: '#4ADEB7', fontSize: 24 }} />;
      case 'negative':
        return <FrownOutlined style={{ color: '#F87171', fontSize: 24 }} />;
      default:
        return <MehOutlined style={{ color: '#FCD34D', fontSize: 24 }} />;
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return { bg: 'rgba(74, 222, 183, 0.2)', border: '#4ADEB7', text: '#4ADEB7' };
      case 'negative':
        return { bg: 'rgba(248, 113, 113, 0.2)', border: '#F87171', text: '#F87171' };
      default:
        return { bg: 'rgba(252, 211, 77, 0.2)', border: '#FCD34D', text: '#FCD34D' };
    }
  };

  const getEmotionColor = (emotion: string) => {
    const colors: { [key: string]: string } = {
      joy: '#4ADEB7',
      sadness: '#5CDBD3',
      anger: '#FF4D4F',
      fear: '#B37FEB',
      disgust: '#F59E0B',
      surprise: '#FFD666',
      neutral: '#9CA3AF',
    };
    return colors[emotion?.toLowerCase()] || '#9CA3AF';
  };

  const getRiskLevelBadge = (level: string) => {
    const config: { [key: string]: { color: string; text: string; icon: any } } = {
      critical: { color: '#FF4D4F', text: 'Critical - Immediate Attention Needed', icon: <WarningOutlined /> },
      high: { color: '#F59E0B', text: 'High Risk', icon: <WarningOutlined /> },
      moderate: { color: '#FCD34D', text: 'Moderate Concern', icon: <WarningOutlined /> },
      low: { color: '#4ADEB7', text: 'Low Risk', icon: <HeartOutlined /> },
      none: { color: '#9CA3AF', text: 'No Concerns', icon: <SmileOutlined /> },
    };
    const cfg = config[level?.toLowerCase()] || config.none;

    return (
      <Tag
        icon={cfg.icon}
        style={{
          padding: '6px 12px',
          fontSize: 14,
          backgroundColor: `${cfg.color}20`,
          border: `1px solid ${cfg.color}`,
          color: cfg.color,
          borderRadius: 8,
        }}
      >
        {cfg.text}
      </Tag>
    );
  };

  if (isLoading) {
    return (
      <MainLayout>
        <div style={{ textAlign: 'center', padding: 100 }}>
          <BookOutlined style={{ fontSize: 48, color: '#4ADEB7', marginBottom: 16 }} />
          <Spin size="large" />
          <Text style={{ display: 'block', marginTop: 16, color: '#9CA3AF' }}>
            Loading your journal...
          </Text>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div style={{ padding: '24px', maxWidth: 1200, margin: '0 auto' }}>
        {/* Hero Section */}
        <div
          style={{
            background: 'linear-gradient(135deg, #1C2340 0%, #0A0F29 100%)',
            borderRadius: 16,
            padding: 32,
            marginBottom: 32,
          }}
        >
          <Row align="middle" justify="space-between">
            <Col>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <BookOutlined style={{ fontSize: 48, marginRight: 16, color: '#4ADEB7' }} />
                <div>
                  <Title level={1} style={{ color: '#FFFFFF', marginBottom: 4 }}>
                    Your Journal
                  </Title>
                  <Text style={{ color: '#D1D5DB', fontSize: 16 }}>
                    AI-powered insights from your reflections
                  </Text>
                </div>
              </div>
            </Col>
            <Col>
              <Badge count={checkins.length} style={{ backgroundColor: '#4ADEB7' }}>
                <Button
                  type="primary"
                  size="large"
                  icon={<EditOutlined />}
                  onClick={() => setShowNewEntry(true)}
                  style={{
                    backgroundColor: '#4ADEB7',
                    borderColor: '#4ADEB7',
                    color: '#0A0F29',
                    height: 48,
                    borderRadius: 12,
                  }}
                >
                  New Entry
                </Button>
              </Badge>
            </Col>
          </Row>

          {/* Quick Stats */}
          <Row gutter={16} style={{ marginTop: 24 }}>
            <Col span={8}>
              <Card
                size="small"
                style={{
                  background: 'rgba(74, 222, 183, 0.1)',
                  border: '1px solid rgba(74, 222, 183, 0.3)',
                  borderRadius: 12,
                  textAlign: 'center',
                }}
              >
                <Statistic
                  title={<Text style={{ color: '#9CA3AF' }}>Total Entries</Text>}
                  value={checkins.length}
                  valueStyle={{ color: '#4ADEB7' }}
                  prefix={<BookOutlined />}
                />
              </Card>
            </Col>
            <Col span={8}>
              <Card
                size="small"
                style={{
                  background: 'rgba(252, 211, 77, 0.1)',
                  border: '1px solid rgba(252, 211, 77, 0.3)',
                  borderRadius: 12,
                  textAlign: 'center',
                }}
              >
                <Statistic
                  title={<Text style={{ color: '#9CA3AF' }}>This Week</Text>}
                  value={checkins.filter((c) => {
                    const weekAgo = new Date();
                    weekAgo.setDate(weekAgo.getDate() - 7);
                    return new Date(c.created_at) > weekAgo;
                  }).length}
                  valueStyle={{ color: '#FCD34D' }}
                  prefix={<FireOutlined />}
                />
              </Card>
            </Col>
            <Col span={8}>
              <Card
                size="small"
                style={{
                  background: 'rgba(245, 158, 11, 0.1)',
                  border: '1px solid rgba(245, 158, 11, 0.3)',
                  borderRadius: 12,
                  textAlign: 'center',
                }}
              >
                <Statistic
                  title={<Text style={{ color: '#9CA3AF' }}>Avg Words/Entry</Text>}
                  value={Math.round(
                    checkins.reduce((sum, c) => sum + (c.journal_text?.split(' ').length || 0), 0) / (checkins.length || 1)
                  )}
                  valueStyle={{ color: '#F59E0B' }}
                  prefix={<TagsOutlined />}
                />
              </Card>
            </Col>
          </Row>
        </div>

        {error && (
          <Alert message={error} type="error" showIcon closable style={{ marginBottom: 16, borderRadius: 12 }} />
        )}

        {/* Journal Entries List */}
        <List
          grid={{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 2, xl: 2 }}
          dataSource={checkins}
          renderItem={(checkin) => (
            <List.Item>
              <Card
                hoverable
                style={{
                  borderRadius: 16,
                  background: 'rgba(28, 35, 64, 0.5)',
                  border: '1px solid rgba(74, 222, 183, 0.2)',
                  height: '100%',
                }}
                onClick={() => handleAnalyzeEntry(checkin)}
              >
                <div style={{ marginBottom: 12 }}>
                  <Text style={{ color: '#9CA3AF', fontSize: 12 }}>
                    {new Date(checkin.created_at).toLocaleDateString('en-US', {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </Text>
                </div>

                <Paragraph
                  ellipsis={{ rows: 3 }}
                  style={{ color: '#D1D5DB', fontSize: 14, marginBottom: 16, minHeight: 63 }}
                >
                  {checkin.journal_text}
                </Paragraph>

                <div style={{ marginBottom: 12 }}>
                  <Tag
                    style={{
                      backgroundColor: 'rgba(74, 222, 183, 0.1)',
                      border: '1px solid rgba(74, 222, 183, 0.3)',
                      color: '#4ADEB7',
                    }}
                  >
                    Mood: {checkin.mood_score}/10
                  </Tag>
                  {checkin.emotion_tags && checkin.emotion_tags.map((emotion) => (
                    <Tag
                      key={emotion}
                      style={{
                        backgroundColor: 'rgba(252, 211, 77, 0.1)',
                        border: '1px solid rgba(252, 211, 77, 0.3)',
                        color: '#FCD34D',
                        textTransform: 'capitalize',
                      }}
                    >
                      {emotion}
                    </Tag>
                  ))}
                </div>

                {checkin.journal_sentiment_score !== undefined && checkin.journal_sentiment_score !== null && (
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      {getSentimentIcon(
                        checkin.journal_sentiment_score > 0.6 ? 'positive' : checkin.journal_sentiment_score < 0.4 ? 'negative' : 'neutral'
                      )}
                      <Text style={{ color: '#D1D5DB', fontSize: 12 }}>
                        AI Analysis Available
                      </Text>
                    </div>
                    <Button
                      type="text"
                      size="small"
                      style={{ color: '#4ADEB7' }}
                    >
                      View Analysis →
                    </Button>
                  </div>
                )}
              </Card>
            </List.Item>
          )}
        />

        {checkins.length === 0 && !isLoading && (
          <Card
            style={{
              borderRadius: 16,
              background: 'rgba(28, 35, 64, 0.5)',
              border: '1px solid rgba(74, 222, 183, 0.2)',
              textAlign: 'center',
              padding: 48,
            }}
          >
            <BookOutlined style={{ fontSize: 64, color: '#4ADEB7', marginBottom: 16 }} />
            <Title level={3} style={{ color: '#FFFFFF' }}>
              Start Your Journal Journey
            </Title>
            <Paragraph style={{ color: '#9CA3AF', fontSize: 16, marginBottom: 24 }}>
              Begin writing to unlock AI-powered insights about your emotional patterns
            </Paragraph>
            <Button
              type="primary"
              size="large"
              icon={<EditOutlined />}
              onClick={() => setShowNewEntry(true)}
              style={{
                backgroundColor: '#4ADEB7',
                borderColor: '#4ADEB7',
                color: '#0A0F29',
                height: 48,
              }}
            >
              Write First Entry
            </Button>
          </Card>
        )}

        {/* Analytics Modal */}
        <Modal
          title={
            <div>
              <BookOutlined style={{ color: '#4ADEB7', marginRight: 8 }} />
              <span style={{ color: '#FFFFFF'}}>Journal Analysis</span>
            </div>
          }
          open={showAnalytics}
          onCancel={() => setShowAnalytics(false)}
          footer={[
            <Button key="close" onClick={() => setShowAnalytics(false)}>
              Close
            </Button>,
          ]}
          width={800}
        >
          {selectedEntry && (
            <div>
              {/* Entry Header */}
              <div style={{ marginBottom: 24 }}>
                <Text style={{ color: '#9CA3AF', fontSize: 12, display: 'block', marginBottom: 8 }}>
                  {new Date(selectedEntry.created_at).toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </Text>
                <Paragraph style={{ color: '#D1D5DB', fontSize: 15, lineHeight: 1.8 }}>
                  {selectedEntry.journal_text}
                </Paragraph>
              </div>

              <Divider style={{ borderColor: 'rgba(74, 222, 183, 0.2)' }}>
                <Text style={{ color: '#4ADEB7' }}>Sentiment Analysis</Text>
              </Divider>

              {/* Sentiment */}
              <Row gutter={16} style={{ marginBottom: 24 }}>
                <Col span={8}>
                  <Card
                    size="small"
                    style={{
                      textAlign: 'center',
                      background: 'rgba(74, 222, 183, 0.1)',
                      border: '1px solid rgba(74, 222, 183, 0.3)',
                      borderRadius: 12,
                    }}
                  >
                    {getSentimentIcon(
                      selectedEntry.journal_sentiment_score! > 0.6
                        ? 'positive'
                        : selectedEntry.journal_sentiment_score! < 0.4
                        ? 'negative'
                        : 'neutral'
                    )}
                    <div style={{ color: '#4ADEB7', fontWeight: 600, marginTop: 8, fontSize: 16 }}>
                      {selectedEntry.journal_sentiment_score! > 0.6
                        ? 'Positive'
                        : selectedEntry.journal_sentiment_score! < 0.4
                        ? 'Negative'
                        : 'Neutral'}
                    </div>
                    <Text style={{ color: '#9CA3AF', fontSize: 12 }}>Overall Tone</Text>
                  </Card>
                </Col>
                <Col span={8}>
                  <Card
                    size="small"
                    style={{
                      textAlign: 'center',
                      background: 'rgba(252, 211, 77, 0.1)',
                      border: '1px solid rgba(252, 211, 77, 0.3)',
                      borderRadius: 12,
                    }}
                  >
                    <Progress
                      type="circle"
                      percent={Math.round((selectedEntry.journal_sentiment_score || 0) * 100)}
                      size={60}
                      strokeColor="#FCD34D"
                      format={(percent) => `${percent}%`}
                    />
                    <Text style={{ color: '#9CA3AF', fontSize: 12, display: 'block', marginTop: 8 }}>
                      Confidence
                    </Text>
                  </Card>
                </Col>
                <Col span={8}>
                  <Card
                    size="small"
                    style={{
                      textAlign: 'center',
                      background: 'rgba(245, 158, 11, 0.1)',
                      border: '1px solid rgba(245, 158, 11, 0.3)',
                      borderRadius: 12,
                    }}
                  >
                    <ThunderboltOutlined style={{ fontSize: 24, color: '#F59E0B', marginBottom: 8 }} />
                    <div style={{ color: '#F59E0B', fontWeight: 600, fontSize: 16 }}>
                      {selectedEntry.journal_text?.split(' ').length || 0}
                    </div>
                    <Text style={{ color: '#9CA3AF', fontSize: 12 }}>Words</Text>
                  </Card>
                </Col>
              </Row>

              <Divider style={{ borderColor: 'rgba(74, 222, 183, 0.2)' }}>
                <Text style={{ color: '#4ADEB7' }}>Emotion Detection</Text>
              </Divider>

              {/* Emotions */}
              <div style={{ marginBottom: 24 }}>
                {selectedEntry.journal_emotion_classification && selectedEntry.ai_emotion_primary && (
                  <>
                    <Text style={{ color: '#D1D5DB', fontSize: 14, display: 'block', marginBottom: 12 }}>
                      Primary Emotion:
                    </Text>
                    <Tag
                      style={{
                        padding: '8px 16px',
                        fontSize: 16,
                        backgroundColor: `${getEmotionColor(selectedEntry.ai_emotion_primary)}20`,
                        border: `2px solid ${getEmotionColor(selectedEntry.ai_emotion_primary)}`,
                        color: getEmotionColor(selectedEntry.ai_emotion_primary),
                        borderRadius: 12,
                        textTransform: 'capitalize',
                      }}
                    >
                      {selectedEntry.ai_emotion_primary}
                    </Tag>
                  </>
                )}

                {selectedEntry.emotion_tags && selectedEntry.emotion_tags.length > 0 && (
                  <>
                    <Text style={{ color: '#D1D5DB', fontSize: 14, display: 'block', marginTop: 16, marginBottom: 12 }}>
                      Tagged Emotions:
                    </Text>
                    {selectedEntry.emotion_tags.map((emotion) => (
                      <Tag
                        key={emotion}
                        style={{
                          margin: 4,
                          padding: '4px 12px',
                          backgroundColor: 'rgba(252, 211, 77, 0.1)',
                          border: '1px solid rgba(252, 211, 77, 0.3)',
                          color: '#FCD34D',
                          borderRadius: 8,
                          textTransform: 'capitalize',
                        }}
                      >
                        {emotion}
                      </Tag>
                    ))}
                  </>
                )}
              </div>

              <Divider style={{ borderColor: 'rgba(74, 222, 183, 0.2)' }}>
                <Text style={{ color: '#4ADEB7' }}>Crisis Assessment</Text>
              </Divider>

              {/* Crisis Risk */}
              <div style={{ marginBottom: 24 }}>
                {getRiskLevelBadge(
                  selectedEntry.crisis_risk_score! > 0.75
                    ? 'critical'
                    : selectedEntry.crisis_risk_score! > 0.5
                    ? 'high'
                    : selectedEntry.crisis_risk_score! > 0.25
                    ? 'moderate'
                    : selectedEntry.crisis_risk_score! > 0
                    ? 'low'
                    : 'none'
                )}

                {selectedEntry.crisis_risk_score! > 0.5 && (
                  <Alert
                    message="Support Resources Available"
                    description="If you're experiencing distress, please reach out to a mental health professional or crisis hotline."
                    type="warning"
                    showIcon
                    style={{ marginTop: 16, borderRadius: 12 }}
                    action={
                      <Button size="small" type="link" style={{ color: '#4ADEB7' }}>
                        View Resources
                      </Button>
                    }
                  />
                )}
              </div>

              {/* Mood Context */}
              <Divider style={{ borderColor: 'rgba(74, 222, 183, 0.2)' }}>
                <Text style={{ color: '#4ADEB7' }}>Context</Text>
              </Divider>
              <Row gutter={16}>
                <Col span={8}>
                  <Text style={{ color: '#9CA3AF', fontSize: 12, display: 'block' }}>Mood Score</Text>
                  <Text style={{ color: '#4ADEB7', fontSize: 20, fontWeight: 600 }}>
                    {selectedEntry.mood_score}/10
                  </Text>
                </Col>
                <Col span={8}>
                  <Text style={{ color: '#9CA3AF', fontSize: 12, display: 'block' }}>Energy</Text>
                  <Text style={{ color: '#FCD34D', fontSize: 20, fontWeight: 600 }}>
                    {selectedEntry.energy_level}/10
                  </Text>
                </Col>
                <Col span={8}>
                  <Text style={{ color: '#9CA3AF', fontSize: 12, display: 'block' }}>Anxiety</Text>
                  <Text style={{ color: '#F87171', fontSize: 20, fontWeight: 600 }}>
                    {selectedEntry.anxiety_level}/10
                  </Text>
                </Col>
              </Row>
            </div>
          )}
        </Modal>

        {/* New Entry Modal - redirects to check-in */}
        <Modal
          title="Create Journal Entry"
          open={showNewEntry}
          onCancel={() => setShowNewEntry(false)}
          footer={[
            <Button key="cancel" onClick={() => setShowNewEntry(false)}>
              Cancel
            </Button>,
            <Button
              key="checkin"
              type="primary"
              style={{ backgroundColor: '#4ADEB7', borderColor: '#4ADEB7', color: '#0A0F29' }}
              onClick={() => {
                window.location.href = '/checkin';
              }}
            >
              Go to Check-in
            </Button>,
          ]}
        >
          <Paragraph style={{ color: '#D1D5DB' }}>
            Journal entries are created as part of your mood check-ins. Click below to create a new check-in with a journal entry.
          </Paragraph>
        </Modal>
      </div>
    </MainLayout>
  );
};

import { useEffect, useState } from 'react';
import { MainLayout } from '../components/layout/MainLayout';
import {
  Card,
  Row,
  Col,
  Typography,
  Spin,
  Alert,
  Tag,
  Progress,
  Table,
  Statistic,
  Divider,
  Button,
  List,
  Badge,
  Rate,
  Avatar,
} from 'antd';
import {
  BarChartOutlined,
  ExperimentOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  ClockCircleOutlined,
  TrophyOutlined,
  SyncOutlined,
  StarFilled,
  EnvironmentOutlined,
  TeamOutlined,
  ThunderboltOutlined,
  SafetyOutlined,
  BulbOutlined,
  HeartOutlined,
  RiseOutlined,
} from '@ant-design/icons';
import type {
  MLModelInfo,
  InterventionEffectivenessReport,
  ComprehensiveReport,
  Intervention,
} from '../types';
import { api } from '../services/api';

const { Title, Text, Paragraph } = Typography;

export const AnalyticsPage = () => {
  const [modelInfo, setModelInfo] = useState<MLModelInfo | null>(null);
  const [effectiveness, setEffectiveness] = useState<InterventionEffectivenessReport | null>(null);
  const [comprehensiveReport, setComprehensiveReport] = useState<ComprehensiveReport | null>(null);
  const [copingMap, setCopingMap] = useState<any>(null);
  const [triggers, setTriggers] = useState<any>(null);
  const [optimalTimes, setOptimalTimes] = useState<any>(null);
  const [interventions, setInterventions] = useState<Map<string, Intervention>>(new Map());
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [info, eff, report, coping, trig, times, allInterventions] = await Promise.all([
        api.getMLModelInfo(),
        api.getInterventionEffectiveness(),
        api.getComprehensiveReport(),
        api.getCopingMap(),
        api.getTriggerPatterns(),
        api.getOptimalInterventionTimes(),
        api.getInterventions(),
      ]);
      setModelInfo(info);
      setEffectiveness(eff);
      setComprehensiveReport(report);
      setCopingMap(coping);
      setTriggers(trig);
      setOptimalTimes(times);

      // Create a map of intervention ID to intervention for easy lookup
      const intMap = new Map<string, Intervention>();
      allInterventions.forEach((int: Intervention) => {
        intMap.set(int.id, int);
      });
      setInterventions(intMap);
    } catch (err) {
      setError('Failed to load analytics. Complete more check-ins to unlock full analytics!');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const getInterventionName = (id: string) => {
    const int = interventions.get(id);
    return int ? int.name : id.slice(0, 8) + '...';
  };

  const getInterventionApproach = (id: string) => {
    const int = interventions.get(id);
    return int ? int.therapeutic_approach : '';
  };

  useEffect(() => {
    fetchData();
  }, []);

  const getRiskLevelColor = (level?: string) => {
    switch (level) {
      case 'low':
        return '#4ADEB7';
      case 'moderate':
        return '#FCD34D';
      case 'high':
        return '#F87171';
      default:
        return '#9CA3AF';
    }
  };

  const getEmotionColor = (emotion: string) => {
    const emotionColors: { [key: string]: { bg: string; border: string; text: string } } = {
      anxiety: { bg: 'rgba(248, 113, 113, 0.2)', border: '#F87171', text: '#F87171' },
      stress: { bg: 'rgba(245, 158, 11, 0.2)', border: '#F59E0B', text: '#F59E0B' },
      overwhelm: { bg: 'rgba(255, 133, 192, 0.2)', border: '#FF85C0', text: '#FF85C0' },
      anger: { bg: 'rgba(255, 77, 79, 0.2)', border: '#FF4D4F', text: '#FF4D4F' },
      frustration: { bg: 'rgba(255, 169, 64, 0.2)', border: '#FFA940', text: '#FFA940' },
      sadness: { bg: 'rgba(93, 219, 211, 0.2)', border: '#5CDBD3', text: '#5CDBD3' },
      fear: { bg: 'rgba(179, 127, 235, 0.2)', border: '#B37FEB', text: '#B37FEB' },
      disappointment: { bg: 'rgba(122, 137, 156, 0.2)', border: '#7A899C', text: '#7A899C' },
      happiness: { bg: 'rgba(74, 222, 183, 0.2)', border: '#4ADEB7', text: '#4ADEB7' },
      joy: { bg: 'rgba(252, 211, 77, 0.2)', border: '#FCD34D', text: '#FCD34D' },
      calm: { bg: 'rgba(105, 192, 255, 0.2)', border: '#69C0FF', text: '#69C0FF' },
      restless: { bg: 'rgba(255, 169, 64, 0.2)', border: '#FFA940', text: '#FFA940' },
      tired: { bg: 'rgba(217, 217, 217, 0.2)', border: '#D9D9D9', text: '#D9D9D9' },
      hopeful: { bg: 'rgba(255, 214, 102, 0.2)', border: '#FFD666', text: '#FFD666' },
      focused: { bg: 'rgba(115, 209, 61, 0.2)', border: '#73D13D', text: '#73D13D' },
      lonely: { bg: 'rgba(145, 202, 255, 0.2)', border: '#91CAFF', text: '#91CAFF' },
      grateful: { bg: 'rgba(149, 222, 100, 0.2)', border: '#95DE64', text: '#95DE64' },
      irritated: { bg: 'rgba(255, 192, 105, 0.2)', border: '#FFC069', text: '#FFC069' },
      disconnected: { bg: 'rgba(191, 191, 191, 0.2)', border: '#BFBFBF', text: '#BFBFBF' },
    };
    return emotionColors[emotion.toLowerCase()] || { bg: 'rgba(122, 137, 156, 0.2)', border: '#7A899C', text: '#7A899C' };
  };

  const getPatternColor = (pattern: string) => {
    const patternColors: { [key: string]: { bg: string; border: string; text: string } } = {
      circadian_patterns: { bg: 'rgba(252, 211, 77, 0.2)', border: '#FCD34D', text: '#FCD34D' },
      weekly_cycles: { bg: 'rgba(74, 222, 183, 0.2)', border: '#4ADEB7', text: '#4ADEB7' },
      mood_energy_correlation: { bg: 'rgba(245, 158, 11, 0.2)', border: '#F59E0B', text: '#F59E0B' },
      emotion_sequences: { bg: 'rgba(179, 127, 235, 0.2)', border: '#B37FEB', text: '#B37FEB' },
      trigger_patterns: { bg: 'rgba(248, 113, 113, 0.2)', border: '#F87171', text: '#F87171' },
      intervention_effectiveness: { bg: 'rgba(105, 192, 255, 0.2)', border: '#69C0FF', text: '#69C0FF' },
    };
    return patternColors[pattern.toLowerCase()] || { bg: 'rgba(122, 137, 156, 0.2)', border: '#7A899C', text: '#7A899C' };
  };

  const getTriggerTypeColor = (type: string) => {
    const typeColors: { [key: string]: { bg: string; border: string; text: string } } = {
      location: { bg: 'rgba(105, 192, 255, 0.2)', border: '#69C0FF', text: '#69C0FF' },
      activity: { bg: 'rgba(115, 209, 61, 0.2)', border: '#73D13D', text: '#73D13D' },
      social: { bg: 'rgba(179, 127, 235, 0.2)', border: '#B37FEB', text: '#B37FEB' },
    };
    return typeColors[type.toLowerCase()] || { bg: 'rgba(74, 222, 183, 0.2)', border: '#4ADEB7', text: '#4ADEB7' };
  };

  const effectivenessColumns = [
    {
      title: 'Intervention',
      dataIndex: 'intervention_id',
      key: 'intervention_id',
      render: (id: string) => (
        <div>
          <Text strong style={{ color: '#D1D5DB' }}>{getInterventionName(id)}</Text>
          <br />
          <Tag style={{ fontSize: 10, backgroundColor: 'rgba(74, 222, 183, 0.15)', color: '#4ADEB7', border: '1px solid rgba(74, 222, 183, 0.3)' }}>
            {getInterventionApproach(id)}
          </Tag>
        </div>
      ),
    },
    {
      title: 'Effectiveness',
      dataIndex: 'average_rating',
      key: 'average_rating',
      render: (rating: number) => (
        <div>
          <Rate disabled defaultValue={rating} allowHalf style={{ fontSize: 14, color: '#FCD34D' }} />
          <Text style={{ marginLeft: 8, color: '#D1D5DB' }}>{rating.toFixed(1)}</Text>
        </div>
      ),
    },
    {
      title: 'Usage',
      dataIndex: 'total_uses',
      key: 'total_uses',
      render: (uses: number) => (
        <Badge count={uses} style={{ backgroundColor: '#4ADEB7' }} overflowCount={999} />
      ),
    },
    {
      title: 'Best For',
      dataIndex: 'best_for_emotion',
      key: 'best_for_emotion',
      render: (emotion: string) => {
        const emotionColor = getEmotionColor(emotion);
        return (
          <Tag
            style={{
              textTransform: 'capitalize',
              backgroundColor: emotionColor.bg,
              color: emotionColor.text,
              border: `1px solid ${emotionColor.border}`,
              fontWeight: 600,
            }}
          >
            {emotion}
          </Tag>
        );
      },
    },
    {
      title: 'Reliability',
      dataIndex: 'consistency',
      key: 'consistency',
      render: (cons: number) => (
        <Progress
          percent={cons * 100}
          size="small"
          strokeColor={cons >= 0.8 ? '#4ADEB7' : cons >= 0.6 ? '#FCD34D' : '#F87171'}
          format={(p) => `${p?.toFixed(0)}%`}
        />
      ),
    },
  ];

  if (isLoading) {
    return (
      <MainLayout>
        <div style={{ textAlign: 'center', padding: 100 }}>
          <BarChartOutlined style={{ fontSize: 48, color: '#4ADEB7', marginBottom: 16 }} className="float-animation" />
          <Spin size="large" />
          <Text style={{ display: 'block', marginTop: 16, color: '#9CA3AF' }}>
            Analyzing your patterns...
          </Text>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div style={{ padding: '24px', maxWidth: 1400, margin: '0 auto' }}>
        {/* Hero Section */}
        <div
          className="hero-section fade-in-up"
          style={{
            background: 'linear-gradient(135deg, #1C2340 0%, #0A0F29 100%)',
            marginBottom: 32,
          }}
        >
          <Row align="middle" gutter={24}>
            <Col xs={24} md={16}>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
                <BarChartOutlined style={{ fontSize: 48, marginRight: 16, color: '#4ADEB7' }} className="float-animation" />
                <div>
                  <Title level={1} style={{ color: '#FFFFFF', marginBottom: 0 }}>
                    Your Wellness Analytics
                  </Title>
                  <Text style={{ color: '#D1D5DB', fontSize: 16 }}>
                    Deep insights into what works best for you
                  </Text>
                </div>
              </div>
            </Col>
            <Col xs={24} md={8} style={{ textAlign: 'right' }}>
              <Button
                type="primary"
                size="large"
                icon={<SyncOutlined />}
                onClick={fetchData}
                style={{
                  backgroundColor: 'rgba(74, 222, 183, 0.2)',
                  border: '1px solid rgba(74, 222, 183, 0.3)',
                  height: 48,
                  borderRadius: 12,
                  color: '#4ADEB7',
                }}
              >
                Refresh Data
              </Button>
            </Col>
          </Row>
        </div>

        {error && (
          <Alert
            message={error}
            type="info"
            showIcon
            icon={<BulbOutlined />}
            style={{ marginBottom: 24, borderRadius: 12 }}
            className="fade-in"
          />
        )}

        {/* Key Insights Summary - FIRST */}
        {comprehensiveReport && comprehensiveReport.key_insights.length > 0 && (
          <Card
            className="fade-in-up hover-lift"
            style={{
              marginBottom: 24,
              borderRadius: 20,
              background: 'rgba(74, 222, 183, 0.1)',
              border: '2px solid rgba(74, 222, 183, 0.4)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
              <BulbOutlined style={{ fontSize: 28, color: '#4ADEB7', marginRight: 12 }} />
              <Title level={3} style={{ color: '#4ADEB7', marginBottom: 0 }}>Key Insights</Title>
            </div>
            <List
              dataSource={comprehensiveReport.key_insights}
              renderItem={(insight) => (
                <List.Item style={{ border: 'none', padding: '8px 0' }}>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <CheckCircleOutlined style={{ color: '#4ADEB7', marginRight: 12, fontSize: 16 }} />
                    <Text style={{ fontSize: 15, color: '#D1D5DB' }}>{insight}</Text>
                  </div>
                </List.Item>
              )}
            />
          </Card>
        )}

        {/* Intervention Effectiveness - SECOND */}
        {effectiveness?.report_available && (
          <Card
            className="fade-in-up hover-lift"
            style={{ marginBottom: 24, borderRadius: 20 }}
            title={
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <TrophyOutlined style={{ fontSize: 24, color: '#FCD34D', marginRight: 12 }} />
                <span style={{ fontSize: 18, fontWeight: 600, color: '#D1D5DB' }}>What's Working Best</span>
              </div>
            }
          >
            <Row gutter={[20, 20]} style={{ marginBottom: 24 }}>
              <Col xs={24} sm={8}>
                <Card
                  size="small"
                  style={{
                    background: 'rgba(74, 222, 183, 0.1)',
                    border: '1px solid rgba(74, 222, 183, 0.3)',
                    borderRadius: 16,
                    textAlign: 'center',
                  }}
                >
                  <Avatar
                    size={48}
                    style={{ backgroundColor: 'rgba(74, 222, 183, 0.2)', marginBottom: 12, border: '2px solid #4ADEB7' }}
                    icon={<ThunderboltOutlined style={{ color: '#4ADEB7', fontSize: 24 }} />}
                  />
                  <Statistic
                    title={<Text style={{ color: '#4ADEB7' }}>Tools Tried</Text>}
                    value={effectiveness.total_interventions_tried}
                    valueStyle={{ color: '#4ADEB7', fontWeight: 700 }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={8}>
                <Card
                  size="small"
                  style={{
                    background: 'rgba(245, 158, 11, 0.1)',
                    border: '1px solid rgba(245, 158, 11, 0.3)',
                    borderRadius: 16,
                    textAlign: 'center',
                  }}
                >
                  <Avatar
                    size={48}
                    style={{ backgroundColor: 'rgba(245, 158, 11, 0.2)', marginBottom: 12, border: '2px solid #F59E0B' }}
                    icon={<HeartOutlined style={{ color: '#F59E0B', fontSize: 24 }} />}
                  />
                  <Statistic
                    title={<Text style={{ color: '#F59E0B' }}>Total Sessions</Text>}
                    value={effectiveness.total_sessions}
                    valueStyle={{ color: '#F59E0B', fontWeight: 700 }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={8}>
                <Card
                  size="small"
                  style={{
                    background: 'rgba(252, 211, 77, 0.1)',
                    border: '1px solid rgba(252, 211, 77, 0.3)',
                    borderRadius: 16,
                    padding: 16,
                  }}
                >
                  <Text strong style={{ color: '#FCD34D', display: 'block', marginBottom: 8 }}>
                    <RiseOutlined style={{ marginRight: 8 }} />
                    Recommendation
                  </Text>
                  <Paragraph style={{ marginBottom: 0, color: '#D1D5DB', fontSize: 14 }}>
                    {effectiveness.recommendation}
                  </Paragraph>
                </Card>
              </Col>
            </Row>

            <Divider style={{ borderColor: 'rgba(74, 222, 183, 0.2)' }}>
              <Text style={{ color: '#4ADEB7' }}>Top Performing Tools</Text>
            </Divider>
            <Table
              dataSource={effectiveness.top_interventions}
              columns={effectivenessColumns}
              pagination={false}
              size="small"
              rowKey="intervention_id"
              style={{ background: 'transparent' }}
            />
          </Card>
        )}

        {/* Optimal Intervention Times - THIRD */}
        {optimalTimes?.optimal_times_available && (
          <Card
            className="fade-in-up hover-lift"
            style={{ marginBottom: 24, borderRadius: 20 }}
            title={
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <ClockCircleOutlined style={{ fontSize: 24, color: '#4ADEB7', marginRight: 12 }} />
                <span style={{ fontSize: 18, fontWeight: 600, color: '#D1D5DB' }}>Best Times for Self-Care</span>
              </div>
            }
          >
            <Text style={{ display: 'block', marginBottom: 16, color: '#D1D5DB' }}>{optimalTimes.insight}</Text>
            <Row gutter={16}>
              {optimalTimes.recommended_times.map((time: any, index: number) => (
                <Col span={8} key={index}>
                  <Card
                    size="small"
                    className="hover-lift"
                    style={{
                      textAlign: 'center',
                      background: 'rgba(74, 222, 183, 0.1)',
                      border: '1px solid rgba(74, 222, 183, 0.3)',
                      borderRadius: 16,
                    }}
                  >
                    <Title level={3} style={{ marginBottom: 8, color: '#4ADEB7' }}>
                      {time.hour}:00
                    </Title>
                    <Text style={{ color: '#D1D5DB' }}>Mood: {time.mood.toFixed(1)}</Text>
                    <br />
                    <Text style={{ color: '#D1D5DB' }}>Energy: {time.energy.toFixed(1)}</Text>
                    <br />
                    <Tag style={{ marginTop: 8, backgroundColor: 'rgba(252, 211, 77, 0.15)', color: '#FCD34D', border: '1px solid rgba(252, 211, 77, 0.3)' }}>
                      {time.reason}
                    </Tag>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        )}

        {/* Trigger Patterns - FOURTH */}
        {triggers && !triggers.message && (
          <Card
            className="fade-in-up hover-lift"
            style={{ marginBottom: 24, borderRadius: 20 }}
            title={
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <WarningOutlined style={{ fontSize: 24, color: '#F59E0B', marginRight: 12 }} />
                <span style={{ fontSize: 18, fontWeight: 600, color: '#D1D5DB' }}>Triggers & Protective Factors</span>
              </div>
            }
          >
            <Row gutter={[24, 24]}>
              <Col xs={24} md={8}>
                <Card
                  size="small"
                  style={{
                    background: 'rgba(248, 113, 113, 0.1)',
                    border: '1px solid rgba(248, 113, 113, 0.3)',
                    borderRadius: 16,
                    height: '100%',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', marginBottom: 12 }}>
                    <EnvironmentOutlined style={{ marginRight: 8, color: '#F87171', fontSize: 20 }} />
                    <Text strong style={{ color: '#F87171' }}>Location Triggers</Text>
                  </div>
                  {triggers.locations?.length > 0 ? (
                    <List
                      size="small"
                      dataSource={triggers.locations}
                      renderItem={(loc: any) => (
                        <List.Item style={{ border: 'none', padding: '6px 0' }}>
                          <div style={{ width: '100%' }}>
                            <Text strong style={{ textTransform: 'capitalize', color: '#D1D5DB' }}>
                              {loc.context.replace('_', ' ')}
                            </Text>
                            <Progress
                              percent={loc.risk_score * 100}
                              size="small"
                              strokeColor="#F87171"
                              format={(p) => `${p?.toFixed(0)}% risk`}
                            />
                          </div>
                        </List.Item>
                      )}
                    />
                  ) : (
                    <Text style={{ color: '#9CA3AF' }}>No location triggers identified</Text>
                  )}
                </Card>
              </Col>
              <Col xs={24} md={8}>
                <Card
                  size="small"
                  style={{
                    background: 'rgba(245, 158, 11, 0.1)',
                    border: '1px solid rgba(245, 158, 11, 0.3)',
                    borderRadius: 16,
                    height: '100%',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', marginBottom: 12 }}>
                    <ThunderboltOutlined style={{ marginRight: 8, color: '#F59E0B', fontSize: 20 }} />
                    <Text strong style={{ color: '#F59E0B' }}>Activity Triggers</Text>
                  </div>
                  {triggers.activities?.length > 0 ? (
                    <List
                      size="small"
                      dataSource={triggers.activities}
                      renderItem={(act: any) => (
                        <List.Item style={{ border: 'none', padding: '6px 0' }}>
                          <div style={{ width: '100%' }}>
                            <Text strong style={{ textTransform: 'capitalize', color: '#D1D5DB' }}>
                              {act.context.replace('_', ' ')}
                            </Text>
                            <Progress
                              percent={act.risk_score * 100}
                              size="small"
                              strokeColor="#F59E0B"
                              format={(p) => `${p?.toFixed(0)}% risk`}
                            />
                          </div>
                        </List.Item>
                      )}
                    />
                  ) : (
                    <Text style={{ color: '#9CA3AF' }}>No activity triggers identified</Text>
                  )}
                </Card>
              </Col>
              <Col xs={24} md={8}>
                <Card
                  size="small"
                  style={{
                    background: 'rgba(74, 222, 183, 0.1)',
                    border: '1px solid rgba(74, 222, 183, 0.3)',
                    borderRadius: 16,
                    height: '100%',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', marginBottom: 12 }}>
                    <SafetyOutlined style={{ marginRight: 8, color: '#4ADEB7', fontSize: 20 }} />
                    <Text strong style={{ color: '#4ADEB7' }}>Protective Factors</Text>
                  </div>
                  {triggers.protective_factors?.length > 0 ? (
                    <List
                      size="small"
                      dataSource={triggers.protective_factors}
                      renderItem={(factor: any) => {
                        const typeColor = getTriggerTypeColor(factor.type);
                        return (
                          <List.Item style={{ border: 'none', padding: '6px 0' }}>
                            <div>
                              <Tag
                                style={{
                                  backgroundColor: typeColor.bg,
                                  color: typeColor.text,
                                  border: `1px solid ${typeColor.border}`,
                                  textTransform: 'capitalize',
                                  fontWeight: 600,
                                }}
                              >
                                {factor.type}
                              </Tag>
                              <Text style={{ textTransform: 'capitalize', color: '#D1D5DB' }}>
                                {factor.context.replace(/_/g, ' ')}
                              </Text>
                            </div>
                          </List.Item>
                        );
                      }}
                    />
                  ) : (
                    <Text style={{ color: '#9CA3AF' }}>No protective factors identified yet</Text>
                  )}
                </Card>
              </Col>
            </Row>
          </Card>
        )}

        {/* Coping Map */}
        {copingMap && !copingMap.message && (
          <Card
            className="fade-in-up hover-lift"
            style={{ marginBottom: 24, borderRadius: 20 }}
            title={
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <StarFilled style={{ fontSize: 24, color: '#FCD34D', marginRight: 12 }} />
                <span style={{ fontSize: 18, fontWeight: 600, color: '#D1D5DB' }}>Your Coping Toolkit</span>
              </div>
            }
          >
            <Text style={{ display: 'block', marginBottom: 16, color: '#9CA3AF' }}>
              Which tools work best for specific emotions (based on your ratings)
            </Text>
            <Row gutter={[16, 16]}>
              {Object.entries(copingMap)
                .filter(([key]) => key !== 'updated_at')
                .map(([emotion, interventionData]: [string, any]) => (
                  <Col xs={24} md={12} lg={8} key={emotion}>
                    <Card
                      size="small"
                      style={{
                        height: '100%',
                        background: 'rgba(28, 35, 64, 0.5)',
                        border: '1px solid rgba(74, 222, 183, 0.2)',
                        borderRadius: 16,
                      }}
                    >
                      <Tag
                        style={{
                          fontSize: 14,
                          textTransform: 'capitalize',
                          marginBottom: 12,
                          backgroundColor: 'rgba(245, 158, 11, 0.15)',
                          color: '#F59E0B',
                          border: '1px solid rgba(245, 158, 11, 0.3)',
                        }}
                      >
                        {emotion}
                      </Tag>
                      {Object.entries(interventionData).map(([intId, data]: [string, any]) => (
                        <div
                          key={intId}
                          style={{
                            padding: '8px',
                            marginBottom: 8,
                            backgroundColor: 'rgba(10, 15, 41, 0.5)',
                            borderRadius: 8,
                          }}
                        >
                          <Text strong style={{ display: 'block', marginBottom: 4, color: '#D1D5DB' }}>
                            {getInterventionName(intId)}
                          </Text>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <Rate
                              disabled
                              defaultValue={data.avg_effectiveness}
                              allowHalf
                              style={{ fontSize: 12, color: '#FCD34D' }}
                            />
                            <Text style={{ fontSize: 12, color: '#9CA3AF' }}>
                              ({data.usage_count}x)
                            </Text>
                          </div>
                          <Progress
                            percent={data.reliability * 100}
                            size="small"
                            strokeColor="#4ADEB7"
                            format={() => `${(data.reliability * 100).toFixed(0)}% reliable`}
                          />
                        </div>
                      ))}
                    </Card>
                  </Col>
                ))}
            </Row>
          </Card>
        )}

        {/* Crisis Risk Assessment */}
        {comprehensiveReport?.sections.crisis_risk_assessment.risk_assessment_available && (
          <Card
            className="fade-in-up hover-lift"
            style={{ marginBottom: 24, borderRadius: 20 }}
            title={
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <SafetyOutlined style={{ fontSize: 24, color: '#4ADEB7', marginRight: 12 }} />
                <span style={{ fontSize: 18, fontWeight: 600, color: '#D1D5DB' }}>Wellness Safety Check</span>
              </div>
            }
          >
            <Row gutter={[20, 20]}>
              <Col xs={24} sm={12}>
                <Card
                  size="small"
                  style={{
                    background: `rgba(${comprehensiveReport.sections.crisis_risk_assessment.risk_level === 'low' ? '74, 222, 183' : comprehensiveReport.sections.crisis_risk_assessment.risk_level === 'moderate' ? '252, 211, 77' : '248, 113, 113'}, 0.2)`,
                    border: `2px solid ${getRiskLevelColor(comprehensiveReport.sections.crisis_risk_assessment.risk_level)}`,
                    borderRadius: 16,
                    textAlign: 'center',
                  }}
                >
                  <Avatar
                    size={48}
                    style={{
                      backgroundColor: `rgba(${comprehensiveReport.sections.crisis_risk_assessment.risk_level === 'low' ? '74, 222, 183' : comprehensiveReport.sections.crisis_risk_assessment.risk_level === 'moderate' ? '252, 211, 77' : '248, 113, 113'}, 0.3)`,
                      marginBottom: 12,
                      border: `2px solid ${getRiskLevelColor(comprehensiveReport.sections.crisis_risk_assessment.risk_level)}`,
                    }}
                    icon={<SafetyOutlined style={{ color: getRiskLevelColor(comprehensiveReport.sections.crisis_risk_assessment.risk_level), fontSize: 24 }} />}
                  />
                  <Statistic
                    title={<Text style={{ color: getRiskLevelColor(comprehensiveReport.sections.crisis_risk_assessment.risk_level), fontSize: 14 }}>Risk Level</Text>}
                    value={comprehensiveReport.sections.crisis_risk_assessment.risk_level || 'low'}
                    valueStyle={{
                      color: getRiskLevelColor(comprehensiveReport.sections.crisis_risk_assessment.risk_level),
                      textTransform: 'uppercase',
                      fontWeight: 700,
                      fontSize: 24,
                    }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12}>
                <Card
                  size="small"
                  style={{
                    background: 'rgba(122, 137, 156, 0.15)',
                    border: '2px solid #7A899C',
                    borderRadius: 16,
                    textAlign: 'center',
                  }}
                >
                  <Avatar
                    size={48}
                    style={{
                      backgroundColor: 'rgba(122, 137, 156, 0.3)',
                      marginBottom: 12,
                      border: '2px solid #7A899C',
                    }}
                    icon={<BarChartOutlined style={{ color: '#7A899C', fontSize: 24 }} />}
                  />
                  <Statistic
                    title={<Text style={{ color: '#7A899C', fontSize: 14 }}>Risk Score</Text>}
                    value={(comprehensiveReport.sections.crisis_risk_assessment.risk_score || 0) * 100}
                    suffix="%"
                    precision={0}
                    valueStyle={{ color: '#D1D5DB', fontWeight: 700, fontSize: 24 }}
                  />
                </Card>
              </Col>
            </Row>
            {comprehensiveReport.sections.crisis_risk_assessment.recommendations.length > 0 && (
              <>
                <Divider style={{ borderColor: 'rgba(74, 222, 183, 0.2)' }} />
                <Text strong style={{ color: '#4ADEB7', display: 'block', marginBottom: 12 }}>Recommendations:</Text>
                <List
                  size="small"
                  dataSource={comprehensiveReport.sections.crisis_risk_assessment.recommendations}
                  renderItem={(item) => (
                    <List.Item style={{ border: 'none', padding: '6px 0' }}>
                      <CheckCircleOutlined style={{ color: '#4ADEB7', marginRight: 8 }} />
                      <Text style={{ color: '#D1D5DB' }}>{item}</Text>
                    </List.Item>
                  )}
                />
              </>
            )}
          </Card>
        )}

        {/* Model Info - LAST (Technical details) */}
        <Card
          className="fade-in-up"
          style={{
            marginBottom: 24,
            borderRadius: 20,
            background: 'rgba(28, 35, 64, 0.3)',
            border: '1px solid rgba(74, 222, 183, 0.1)',
          }}
          title={
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <ExperimentOutlined style={{ fontSize: 24, color: '#9CA3AF', marginRight: 12 }} />
              <span style={{ fontSize: 18, fontWeight: 600, color: '#9CA3AF' }}>Technical Details</span>
            </div>
          }
        >
          {modelInfo && (
            <Row gutter={[20, 20]}>
              <Col xs={12} sm={6}>
                <Statistic
                  title={<Text style={{ color: '#9CA3AF', fontSize: 12 }}>Model Version</Text>}
                  value={modelInfo.model_version}
                  prefix="v"
                  valueStyle={{ color: '#D1D5DB', fontSize: 20 }}
                />
              </Col>
              <Col xs={12} sm={6}>
                <Statistic
                  title={<Text style={{ color: '#9CA3AF', fontSize: 12 }}>Total Interactions</Text>}
                  value={modelInfo.total_interactions}
                  prefix={<SyncOutlined style={{ color: '#9CA3AF' }} />}
                  valueStyle={{ color: '#D1D5DB', fontSize: 20 }}
                />
              </Col>
              <Col xs={24} sm={12}>
                <Text style={{ color: '#9CA3AF', fontSize: 12, display: 'block', marginBottom: 8 }}>Patterns Learned:</Text>
                <div>
                  {modelInfo.patterns_available.length > 0 ? (
                    modelInfo.patterns_available.map((pattern) => {
                      const patternColor = getPatternColor(pattern);
                      return (
                        <Tag
                          key={pattern}
                          style={{
                            marginBottom: 4,
                            backgroundColor: patternColor.bg,
                            color: patternColor.text,
                            border: `1px solid ${patternColor.border}`,
                            fontWeight: 600,
                          }}
                        >
                          <CheckCircleOutlined /> {pattern.replace(/_/g, ' ')}
                        </Tag>
                      );
                    })
                  ) : (
                    <Text style={{ color: '#9CA3AF' }}>No patterns learned yet</Text>
                  )}
                </div>
              </Col>
            </Row>
          )}
          {modelInfo?.last_model_update && (
            <div style={{ marginTop: 16 }}>
              <Text style={{ color: '#9CA3AF', fontSize: 12 }}>
                Last updated: {new Date(modelInfo.last_model_update).toLocaleString()}
              </Text>
            </div>
          )}
        </Card>
      </div>
    </MainLayout>
  );
};

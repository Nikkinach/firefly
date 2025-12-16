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
  List,
  Button,
  Statistic,
  Divider,
  Avatar,
  Timeline,
} from 'antd';
import {
  BulbOutlined,
  LineChartOutlined,
  TrophyOutlined,
  ClockCircleOutlined,
  RiseOutlined,
  FallOutlined,
  MinusOutlined,
  ThunderboltOutlined,
  HeartOutlined,
  ReloadOutlined,
  CalendarOutlined,
  FireOutlined,
  SmileOutlined,
  FrownOutlined,
  MehOutlined,
  StarFilled,
  RocketOutlined,
  AimOutlined,
  ExperimentOutlined,
} from '@ant-design/icons';
import type {
  WeeklyInsights,
  MoodPrediction,
  PatternDetection,
  DailyInsight,
  DayForecast,
} from '../types';
import { api } from '../services/api';

const { Title, Text, Paragraph } = Typography;

export const InsightsPage = () => {
  const [weeklyInsights, setWeeklyInsights] = useState<WeeklyInsights | null>(null);
  const [prediction, setPrediction] = useState<MoodPrediction | null>(null);
  const [patterns, setPatterns] = useState<PatternDetection | null>(null);
  const [dailyInsight, setDailyInsight] = useState<DailyInsight | null>(null);
  const [forecast, setForecast] = useState<DayForecast[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isTraining, setIsTraining] = useState(false);

  const fetchInsights = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [weekly, pred, patt, daily, fore] = await Promise.all([
        api.getWeeklyInsights(),
        api.getMoodPrediction(24),
        api.getMoodPatterns(),
        api.getDailyInsight(),
        api.getMoodForecast(7),
      ]);
      setWeeklyInsights(weekly);
      setPrediction(pred);
      setPatterns(patt);
      setDailyInsight(daily);
      setForecast(fore.forecasts);
    } catch (err: any) {
      setError('Keep checking in to unlock personalized insights!');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, []);

  const handleTrainModel = async () => {
    setIsTraining(true);
    try {
      await api.trainModel();
      await fetchInsights();
    } catch (err) {
      console.error('Training failed:', err);
    } finally {
      setIsTraining(false);
    }
  };

  const getTrendIcon = (direction?: string) => {
    switch (direction) {
      case 'improving':
        return <RiseOutlined style={{ color: '#4ADEB7', fontSize: 20 }} />;
      case 'declining':
        return <FallOutlined style={{ color: '#F87171', fontSize: 20 }} />;
      default:
        return <MinusOutlined style={{ color: '#FCD34D', fontSize: 20 }} />;
    }
  };

  const getMoodIcon = (mood: number) => {
    if (mood >= 7) return <SmileOutlined style={{ fontSize: 28, color: '#4ADEB7' }} />;
    if (mood >= 4) return <MehOutlined style={{ fontSize: 28, color: '#FCD34D' }} />;
    return <FrownOutlined style={{ fontSize: 28, color: '#F87171' }} />;
  };

  const getMoodColor = (mood: number) => {
    if (mood >= 7) return '#4ADEB7';
    if (mood >= 5) return '#FCD34D';
    return '#F87171';
  };

  if (isLoading) {
    return (
      <MainLayout>
        <div style={{ textAlign: 'center', padding: 100 }}>
          <ExperimentOutlined style={{ fontSize: 48, color: '#4ADEB7', marginBottom: 16 }} className="float-animation" />
          <Spin size="large" />
          <Text style={{ display: 'block', marginTop: 16, color: '#9CA3AF' }}>
            Analyzing your wellness patterns...
          </Text>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div style={{ padding: '24px', maxWidth: 1400, margin: '0 auto' }}>
        {/* Hero Section - matching Analytics style */}
        <div
          className="hero-section fade-in-up"
          style={{
            background: 'linear-gradient(135deg, #1C2340 0%, #0A0F29 100%)',
          }}
        >
          <Row align="middle" gutter={24}>
            <Col xs={24} md={16}>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
                <BulbOutlined style={{ fontSize: 48, marginRight: 16, color: '#4ADEB7' }} className="float-animation" />
                <div>
                  <Title level={1} style={{ color: '#FFFFFF', marginBottom: 0 }}>
                    Personalized Insights
                  </Title>
                  <Text style={{ color: '#D1D5DB', fontSize: 16 }}>
                    Deep insights into your wellness patterns
                  </Text>
                </div>
              </div>
              {dailyInsight && (
                <div
                  style={{
                    backgroundColor: 'rgba(74, 222, 183, 0.1)',
                    border: '1px solid rgba(74, 222, 183, 0.3)',
                    borderRadius: 12,
                    padding: 16,
                    marginTop: 12,
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
                    <ThunderboltOutlined style={{ color: '#FCD34D', fontSize: 20, marginRight: 8 }} />
                    <Text strong style={{ color: '#FCD34D', fontSize: 14 }}>Today's Insight</Text>
                  </div>
                  <Text style={{ color: '#D1D5DB', fontSize: 15, lineHeight: 1.6 }}>
                    {dailyInsight.insight}
                  </Text>
                </div>
              )}
            </Col>
            <Col xs={24} md={8} style={{ textAlign: 'right' }}>
              <Button
                type="primary"
                size="large"
                icon={<ReloadOutlined spin={isTraining} />}
                onClick={handleTrainModel}
                loading={isTraining}
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
          <Alert message={error} type="info" showIcon icon={<BulbOutlined />} style={{ marginBottom: 20, borderRadius: 12 }} />
        )}

        {/* Weekly Summary with Equal Cards */}
        {weeklyInsights && (
          <Card
            className="hover-lift fade-in-up"
            style={{ borderRadius: 16, marginBottom: 20 }}
            bodyStyle={{ padding: 16 }}
          >
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
              <LineChartOutlined style={{ fontSize: 20, color: '#4ADEB7', marginRight: 10 }} />
              <Title level={4} style={{ color: '#D1D5DB', marginBottom: 0 }}>Weekly Summary</Title>
            </div>
            <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
              <Col xs={8}>
                <Card
                  size="small"
                  style={{
                    background: 'rgba(245, 158, 11, 0.1)',
                    border: '1px solid rgba(245, 158, 11, 0.3)',
                    borderRadius: 10,
                    textAlign: 'center',
                    height: 100,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                  bodyStyle={{ padding: 12 }}
                >
                  <div>
                    <FireOutlined style={{ fontSize: 22, color: '#F59E0B', marginBottom: 4 }} />
                    <div style={{ fontSize: 22, fontWeight: 700, color: '#F59E0B' }}>
                      {weeklyInsights.checkin_summary.total}
                    </div>
                    <div style={{ fontSize: 11, color: '#9CA3AF' }}>Check-ins</div>
                  </div>
                </Card>
              </Col>
              <Col xs={8}>
                <Card
                  size="small"
                  style={{
                    background: 'rgba(74, 222, 183, 0.1)',
                    border: '1px solid rgba(74, 222, 183, 0.3)',
                    borderRadius: 10,
                    textAlign: 'center',
                    height: 100,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                  bodyStyle={{ padding: 12 }}
                >
                  <div>
                    <SmileOutlined style={{ fontSize: 22, color: '#4ADEB7', marginBottom: 4 }} />
                    <div style={{ fontSize: 22, fontWeight: 700, color: '#4ADEB7' }}>
                      {weeklyInsights.checkin_summary.average_mood?.toFixed(1) || '-'}
                    </div>
                    <div style={{ fontSize: 11, color: '#9CA3AF' }}>Avg Mood</div>
                  </div>
                </Card>
              </Col>
              <Col xs={8}>
                <Card
                  size="small"
                  style={{
                    background: 'rgba(122, 137, 156, 0.1)',
                    border: '1px solid rgba(122, 137, 156, 0.3)',
                    borderRadius: 10,
                    textAlign: 'center',
                    height: 100,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                  bodyStyle={{ padding: 12 }}
                >
                  <div>
                    <Tag
                      style={{
                        padding: '4px 12px',
                        borderRadius: 10,
                        fontSize: 12,
                        fontWeight: 600,
                        backgroundColor:
                          weeklyInsights.checkin_summary.consistency === 'excellent'
                            ? 'rgba(74, 222, 183, 0.3)'
                            : weeklyInsights.checkin_summary.consistency === 'good'
                            ? 'rgba(105, 192, 255, 0.3)'
                            : 'rgba(245, 158, 11, 0.3)',
                        color:
                          weeklyInsights.checkin_summary.consistency === 'excellent'
                            ? '#4ADEB7'
                            : weeklyInsights.checkin_summary.consistency === 'good'
                            ? '#69C0FF'
                            : '#F59E0B',
                        border:
                          weeklyInsights.checkin_summary.consistency === 'excellent'
                            ? '2px solid #4ADEB7'
                            : weeklyInsights.checkin_summary.consistency === 'good'
                            ? '2px solid #69C0FF'
                            : '2px solid #F59E0B',
                      }}
                    >
                      {weeklyInsights.checkin_summary.consistency?.toUpperCase()}
                    </Tag>
                    <div style={{ fontSize: 11, color: '#9CA3AF', marginTop: 8 }}>Consistency</div>
                  </div>
                </Card>
              </Col>
            </Row>

            {weeklyInsights.mood_insights.length > 0 && (
              <div style={{ textAlign: 'left' }}>
                <Text strong style={{ color: '#7A899C', fontSize: 13, display: 'block', marginBottom: 8 }}>
                  Key Insights
                </Text>
                {weeklyInsights.mood_insights.map((item, i) => (
                  <div key={i} style={{ marginBottom: 6, display: 'flex', alignItems: 'flex-start' }}>
                    <BulbOutlined style={{ color: '#FCD34D', marginRight: 8, marginTop: 4, fontSize: 12 }} />
                    <Text style={{ color: '#D1D5DB', fontSize: 13 }}>{item}</Text>
                  </div>
                ))}
              </div>
            )}
          </Card>
        )}

        {/* Patterns Detected - Full Width Grid */}
        {patterns?.patterns_detected && (
          <Card
            className="fade-in-up hover-lift"
            style={{ marginBottom: 24, borderRadius: 20 }}
            bodyStyle={{ padding: 20 }}
          >
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: 20 }}>
              <ExperimentOutlined style={{ fontSize: 24, color: '#F59E0B', marginRight: 12 }} />
              <Title level={4} style={{ color: '#D1D5DB', marginBottom: 0, fontSize: 18 }}>Patterns Detected</Title>
            </div>
            <Row gutter={[16, 16]}>
              {patterns.weekly_cycle && (
                <Col xs={24} md={8}>
                  <Card
                    size="small"
                    style={{
                      background: 'rgba(74, 222, 183, 0.1)',
                      border: '2px solid rgba(74, 222, 183, 0.3)',
                      borderRadius: 16,
                      height: '100%',
                    }}
                    bodyStyle={{ padding: 16 }}
                  >
                    <Text strong style={{ color: '#4ADEB7', fontSize: 14, display: 'block', marginBottom: 12 }}>
                      <CalendarOutlined style={{ marginRight: 8 }} />
                      Weekly Cycle
                    </Text>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
                      <div style={{ textAlign: 'center', flex: 1 }}>
                        <SmileOutlined style={{ fontSize: 24, color: '#4ADEB7' }} />
                        <div style={{ fontSize: 13, color: '#4ADEB7', fontWeight: 700, marginTop: 4 }}>
                          {patterns.weekly_cycle.best_day}
                        </div>
                        <div style={{ fontSize: 11, color: '#9CA3AF' }}>Best Day</div>
                      </div>
                      <div style={{ textAlign: 'center', flex: 1 }}>
                        <FrownOutlined style={{ fontSize: 24, color: '#F87171' }} />
                        <div style={{ fontSize: 13, color: '#F87171', fontWeight: 700, marginTop: 4 }}>
                          {patterns.weekly_cycle.worst_day}
                        </div>
                        <div style={{ fontSize: 11, color: '#9CA3AF' }}>Low Day</div>
                      </div>
                    </div>
                    <Tag style={{ backgroundColor: 'rgba(122, 137, 156, 0.2)', color: '#7A899C', border: '1px solid rgba(122, 137, 156, 0.4)', fontSize: 11, width: '100%', textAlign: 'center' }}>
                      Variation: {patterns.weekly_cycle.spread} points
                    </Tag>
                  </Card>
                </Col>
              )}

              {patterns.time_of_day_effect && (
                <Col xs={24} md={8}>
                  <Card
                    size="small"
                    style={{
                      background: 'rgba(252, 211, 77, 0.1)',
                      border: '2px solid rgba(252, 211, 77, 0.3)',
                      borderRadius: 16,
                      height: '100%',
                    }}
                    bodyStyle={{ padding: 16 }}
                  >
                    <Text strong style={{ color: '#FCD34D', fontSize: 14, display: 'block', marginBottom: 12 }}>
                      <ClockCircleOutlined style={{ marginRight: 8 }} />
                      Time of Day
                    </Text>
                    <div style={{ marginBottom: 12 }}>
                      <Text style={{ fontSize: 12, color: '#D1D5DB', display: 'block', marginBottom: 4 }}>Best Time</Text>
                      <Tag style={{ backgroundColor: 'rgba(74, 222, 183, 0.3)', color: '#4ADEB7', border: '2px solid #4ADEB7', fontSize: 12, fontWeight: 600, padding: '4px 12px' }}>
                        {patterns.time_of_day_effect.best_time}
                      </Tag>
                    </div>
                    <div>
                      <Text style={{ fontSize: 12, color: '#D1D5DB', display: 'block', marginBottom: 4 }}>Lower Time</Text>
                      <Tag style={{ backgroundColor: 'rgba(245, 158, 11, 0.3)', color: '#F59E0B', border: '2px solid #F59E0B', fontSize: 12, fontWeight: 600, padding: '4px 12px' }}>
                        {patterns.time_of_day_effect.worst_time}
                      </Tag>
                    </div>
                  </Card>
                </Col>
              )}

              {patterns.volatility && (
                <Col xs={24} md={8}>
                  <Card
                    size="small"
                    style={{
                      background: 'rgba(122, 137, 156, 0.1)',
                      border: '2px solid rgba(122, 137, 156, 0.3)',
                      borderRadius: 16,
                      height: '100%',
                    }}
                    bodyStyle={{ padding: 16 }}
                  >
                    <Text strong style={{ color: '#7A899C', fontSize: 14, display: 'block', marginBottom: 12 }}>
                      <HeartOutlined style={{ marginRight: 8 }} />
                      Mood Stability
                    </Text>
                    <div style={{ textAlign: 'center', marginBottom: 12 }}>
                      <Tag
                        style={{
                          fontSize: 16,
                          padding: '6px 20px',
                          borderRadius: 12,
                          backgroundColor: patterns.volatility.level === 'stable' ? 'rgba(74, 222, 183, 0.3)' : 'rgba(245, 158, 11, 0.3)',
                          color: patterns.volatility.level === 'stable' ? '#4ADEB7' : '#F59E0B',
                          border: patterns.volatility.level === 'stable' ? '2px solid #4ADEB7' : '2px solid #F59E0B',
                          fontWeight: 700,
                        }}
                      >
                        {patterns.volatility.level.toUpperCase()}
                      </Tag>
                    </div>
                    <Tag style={{ backgroundColor: 'rgba(122, 137, 156, 0.2)', color: '#7A899C', border: '1px solid rgba(122, 137, 156, 0.4)', fontSize: 11, width: '100%', textAlign: 'center' }}>
                      Avg change: {patterns.volatility.average_change} points
                    </Tag>
                  </Card>
                </Col>
              )}
            </Row>
          </Card>
        )}

        {/* Mood Prediction */}
        {prediction?.prediction_available && (
          <Card
            className="fade-in-up hover-lift"
            style={{ marginBottom: 20, borderRadius: 16 }}
            bodyStyle={{ padding: 16 }}
          >
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
              <AimOutlined style={{ fontSize: 20, color: '#4ADEB7', marginRight: 10 }} />
              <Title level={4} style={{ color: '#D1D5DB', marginBottom: 0 }}>24-Hour Mood Prediction</Title>
            </div>
            <Row gutter={[16, 16]} align="middle">
              <Col xs={24} sm={8} style={{ textAlign: 'center' }}>
                <div
                  style={{
                    background: 'rgba(37, 43, 77, 0.8)',
                    borderRadius: 16,
                    padding: 16,
                    border: `2px solid ${getMoodColor(prediction.predicted_mood || 5)}`,
                  }}
                >
                  {getMoodIcon(prediction.predicted_mood || 5)}
                  <div style={{ fontSize: 36, fontWeight: 700, marginTop: 4, color: getMoodColor(prediction.predicted_mood || 5) }}>
                    {prediction.predicted_mood?.toFixed(1)}
                  </div>
                  <div style={{ fontSize: 12, color: '#9CA3AF' }}>Predicted Mood</div>
                </div>
              </Col>
              <Col xs={12} sm={8}>
                <Card size="small" style={{ background: 'rgba(74, 222, 183, 0.1)', border: '1px solid rgba(74, 222, 183, 0.3)', borderRadius: 12, marginBottom: 8 }} bodyStyle={{ padding: 10 }}>
                  <div style={{ fontSize: 11, color: '#4ADEB7' }}>Energy</div>
                  <div style={{ fontSize: 20, fontWeight: 700, color: '#4ADEB7' }}>{prediction.predicted_energy || '-'}/10</div>
                </Card>
                <Card size="small" style={{ background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.3)', borderRadius: 12 }} bodyStyle={{ padding: 10 }}>
                  <div style={{ fontSize: 11, color: '#F59E0B' }}>Confidence</div>
                  <div style={{ fontSize: 20, fontWeight: 700, color: '#F59E0B' }}>{((prediction.confidence || 0) * 100).toFixed(0)}%</div>
                </Card>
              </Col>
              <Col xs={12} sm={8} style={{ textAlign: 'center' }}>
                <Avatar size={48} style={{ backgroundColor: 'rgba(37, 43, 77, 0.8)', border: '2px solid rgba(74, 222, 183, 0.3)', marginBottom: 8 }} icon={getTrendIcon(prediction.trend_direction)} />
                <div style={{ fontSize: 14, fontWeight: 600, color: '#D1D5DB', textTransform: 'capitalize' }}>{prediction.trend_direction}</div>
                <div style={{ fontSize: 11, color: '#9CA3AF' }}>Trend</div>
              </Col>
            </Row>
          </Card>
        )}

        {/* 7-Day Forecast - Improved Display */}
        {forecast.length > 0 && (
          <Card
            className="fade-in-up hover-lift"
            style={{ marginBottom: 24, borderRadius: 20 }}
            bodyStyle={{ padding: 20 }}
          >
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: 20 }}>
              <CalendarOutlined style={{ fontSize: 24, color: '#4ADEB7', marginRight: 12 }} />
              <Title level={4} style={{ color: '#D1D5DB', marginBottom: 0, fontSize: 18 }}>7-Day Mood Forecast</Title>
            </div>
            <Row gutter={[12, 12]}>
              {forecast.map((day, index) => {
                const dateObj = new Date(day.date);
                const formattedDate = dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'long' });

                return (
                  <Col xs={24} sm={12} md={24 / Math.min(forecast.length, 7)} key={day.date}>
                    <Card
                      size="small"
                      className="hover-lift"
                      style={{
                        textAlign: 'center',
                        borderRadius: 16,
                        background: index === 0 ? 'rgba(74, 222, 183, 0.15)' : 'rgba(42, 31, 74, 0.5)',
                        border: index === 0 ? '2px solid #4ADEB7' : '1px solid rgba(74, 222, 183, 0.2)',
                      }}
                      bodyStyle={{ padding: 14 }}
                    >
                      <div style={{ fontSize: 14, fontWeight: 700, color: '#FFFFFF', marginBottom: 4 }}>
                        {formattedDate}, {dayName}
                        {index === 0 && (
                          <Tag style={{ fontSize: 10, padding: '2px 6px', backgroundColor: '#4ADEB7', color: '#0A0F29', border: 'none', marginLeft: 6, fontWeight: 600 }}>
                            TODAY
                          </Tag>
                        )}
                      </div>
                      <Divider style={{ margin: '10px 0', borderColor: 'rgba(74, 222, 183, 0.2)' }} />
                      {Object.entries(day.periods).map(([period, data]) => (
                        <div key={period} style={{ marginBottom: 10 }}>
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 6 }}>
                            <span style={{ fontSize: 16, marginRight: 6 }}>
                              {period === 'morning' ? '🌅' : period === 'afternoon' ? '☀️' : '🌙'}
                            </span>
                            <Text style={{ fontSize: 13, color: '#D1D5DB', fontWeight: 600 }}>
                              {period === 'morning' ? 'Morning' : period === 'afternoon' ? 'Afternoon' : 'Evening'}
                            </Text>
                          </div>
                          <Progress
                            percent={data.predicted_mood * 10}
                            size="small"
                            showInfo={false}
                            strokeColor={getMoodColor(data.predicted_mood)}
                            trailColor="rgba(74, 222, 183, 0.1)"
                            strokeWidth={8}
                            style={{ marginBottom: 4 }}
                          />
                          <Text style={{ fontSize: 14, color: getMoodColor(data.predicted_mood), fontWeight: 700 }}>
                            {data.predicted_mood.toFixed(1)}
                          </Text>
                          <Text style={{ fontSize: 11, color: '#9CA3AF', display: 'block' }}>
                            mood score
                          </Text>
                        </div>
                      ))}
                    </Card>
                  </Col>
                );
              })}
            </Row>
          </Card>
        )}

        {/* Personalized Tips */}
        {weeklyInsights && weeklyInsights.personalized_tips.length > 0 && (
          <Card
            className="fade-in-up hover-lift"
            style={{
              marginBottom: 20,
              borderRadius: 16,
              background: 'rgba(74, 222, 183, 0.1)',
              border: '1px solid rgba(74, 222, 183, 0.3)',
            }}
            bodyStyle={{ padding: 16 }}
          >
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: 12 }}>
              <HeartOutlined style={{ fontSize: 20, color: '#4ADEB7', marginRight: 10 }} />
              <Title level={4} style={{ color: '#4ADEB7', marginBottom: 0 }}>Tips for You</Title>
            </div>
            <Row gutter={[12, 12]}>
              {weeklyInsights.personalized_tips.map((tip, index) => (
                <Col xs={24} md={12} key={index}>
                  <div style={{ backgroundColor: 'rgba(10, 15, 41, 0.8)', padding: 12, borderRadius: 10 }}>
                    <Text style={{ fontSize: 13, color: '#D1D5DB' }}>
                      <span style={{ marginRight: 6 }}>💡</span>{tip}
                    </Text>
                  </div>
                </Col>
              ))}
            </Row>
          </Card>
        )}

        {/* Focus Areas */}
        {weeklyInsights && weeklyInsights.focus_areas.length > 0 && (
          <Card className="fade-in-up hover-lift" style={{ marginBottom: 20, borderRadius: 16 }} bodyStyle={{ padding: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: 12 }}>
              <AimOutlined style={{ fontSize: 20, color: '#F59E0B', marginRight: 10 }} />
              <Title level={4} style={{ color: '#D1D5DB', marginBottom: 0 }}>Focus Areas</Title>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {weeklyInsights.focus_areas.map((area, index) => (
                <Tag key={index} style={{ padding: '6px 12px', borderRadius: 12, fontSize: 12, backgroundColor: 'rgba(245, 158, 11, 0.15)', color: '#F59E0B', border: '1px solid rgba(245, 158, 11, 0.3)' }}>
                  {area}
                </Tag>
              ))}
            </div>
          </Card>
        )}

        {/* Achievements - Moved to End */}
        {weeklyInsights && weeklyInsights.achievements.length > 0 && (
          <Card className="hover-lift fade-in-up" style={{ borderRadius: 16 }} bodyStyle={{ padding: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: 12 }}>
              <TrophyOutlined style={{ fontSize: 20, color: '#FCD34D', marginRight: 10 }} />
              <Title level={4} style={{ color: '#D1D5DB', marginBottom: 0 }}>Achievements This Week</Title>
            </div>
            <Row gutter={[12, 12]}>
              {weeklyInsights.achievements.map((achievement, index) => (
                <Col xs={24} sm={12} key={index}>
                  <Card
                    size="small"
                    className="hover-lift"
                    style={{ background: 'rgba(252, 211, 77, 0.1)', border: '1px solid rgba(252, 211, 77, 0.3)', borderRadius: 10 }}
                    bodyStyle={{ padding: 12 }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <div style={{ fontSize: 24, marginRight: 12, backgroundColor: 'rgba(252, 211, 77, 0.2)', borderRadius: '50%', width: 44, height: 44, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        {achievement.icon}
                      </div>
                      <div>
                        <Text strong style={{ fontSize: 13, display: 'block', color: '#FCD34D' }}>{achievement.name}</Text>
                        <Text style={{ color: '#D1D5DB', fontSize: 11 }}>{achievement.description}</Text>
                      </div>
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        )}
      </div>
    </MainLayout>
  );
};

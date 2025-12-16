import { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Typography, Spin, Alert, Progress, Tag, Avatar, Tooltip, List } from 'antd';
import {
  FireOutlined,
  RiseOutlined,
  FallOutlined,
  MinusOutlined,
  SmileOutlined,
  BulbOutlined,
  BarChartOutlined,
  HeartOutlined,
  CalendarOutlined,
  TrophyOutlined,
  ArrowRightOutlined,
  PlusCircleOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '../../stores/authStore';
import type { CheckinStats, DailyInsight, Intervention } from '../../types';
import { api } from '../../services/api';
import { useNavigate } from 'react-router-dom';

const { Title, Text, Paragraph } = Typography;

export const Dashboard = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [stats, setStats] = useState<CheckinStats | null>(null);
  const [dailyInsight, setDailyInsight] = useState<DailyInsight | null>(null);
  const [suggestedInterventions, setSuggestedInterventions] = useState<Intervention[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [statsData, insightData, interventionsData] = await Promise.all([
          api.getCheckinStats(),
          api.getDailyInsight().catch(() => null),
          api.getInterventions().catch(() => []),
        ]);
        setStats(statsData);
        setDailyInsight(insightData);
        // Get top 3 interventions sorted by usage (ascending) to suggest least used ones
        const sorted = interventionsData.sort((a: Intervention, b: Intervention) => a.total_completions - b.total_completions);
        setSuggestedInterventions(sorted.slice(0, 3));
      } catch (err: any) {
        setError('Failed to load stats');
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving':
        return <RiseOutlined style={{ color: '#4ADEB7', fontSize: 24 }} />;
      case 'declining':
        return <FallOutlined style={{ color: '#F87171', fontSize: 24 }} />;
      default:
        return <MinusOutlined style={{ color: '#FCD34D', fontSize: 24 }} />;
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'improving':
        return '#4ADEB7';
      case 'declining':
        return '#F87171';
      default:
        return '#FCD34D';
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const getMoodLevel = (mood: number | null) => {
    if (!mood) return { text: 'No data', color: '#9CA3AF' };
    if (mood >= 8) return { text: 'Excellent', color: '#4ADEB7' };
    if (mood >= 6) return { text: 'Good', color: '#6EE7B7' };
    if (mood >= 4) return { text: 'Moderate', color: '#FCD34D' };
    return { text: 'Low', color: '#F87171' };
  };

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: 100 }}>
        <Spin size="large" />
        <Text style={{ display: 'block', marginTop: 16, color: '#9CA3AF' }}>
          Loading your wellness dashboard...
        </Text>
      </div>
    );
  }

  const moodInfo = getMoodLevel(stats?.average_mood_7_days || null);

  return (
    <div style={{ padding: '24px', maxWidth: 1400, margin: '0 auto' }}>
      {/* Hero Section with AI Insight */}
      <div
        className="hero-section fade-in-up"
        style={{
          background: 'linear-gradient(135deg, #1C2340 0%, #0A0F29 100%)',
        }}
      >
        <Row align="middle" gutter={24}>
          <Col xs={24} md={16}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
              <span style={{ fontSize: 40, marginRight: 12 }} className="sparkle-animation">
                ✨
              </span>
              <div>
                <Title level={1} style={{ color: '#FFFFFF', marginBottom: 0 }}>
                  {getGreeting()}, {user?.display_name || 'Friend'}!
                </Title>
                <Text style={{ color: '#D1D5DB', fontSize: 16 }}>
                  Your personal wellness journey continues
                </Text>
              </div>
              <Tooltip title="Check in for your daily mood" placement="top">
                <Avatar
                  size={44}
                  style={{
                    backgroundColor: '#4ADEB7',
                    cursor: 'pointer',
                    marginLeft: 20,
                    boxShadow: '0 0 20px rgba(74, 222, 183, 0.5)',
                  }}
                  icon={<PlusCircleOutlined style={{ fontSize: 22 }} />}
                  onClick={() => navigate('/checkin')}
                  className="pulse-hover"
                />
              </Tooltip>
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
                  <BulbOutlined style={{ color: '#FCD34D', fontSize: 20, marginRight: 8 }} />
                  <Text strong style={{ color: '#FCD34D', fontSize: 14 }}>
                    Today's AI Insight
                  </Text>
                </div>
                <Paragraph style={{ color: '#D1D5DB', fontSize: 15, marginBottom: 0, lineHeight: 1.6 }}>
                  {dailyInsight.insight}
                </Paragraph>
              </div>
            )}
          </Col>
          <Col xs={24} md={8} style={{ textAlign: 'right' }}>
            {stats?.streak_length != null && stats.streak_length > 0 && (
              <div className="streak-badge glow-animation" style={{ marginBottom: 16 }}>
                <FireOutlined style={{ fontSize: 20 }} />
                <span>{stats.streak_length} day streak!</span>
              </div>
            )}
          </Col>
        </Row>
      </div>

      {error && (
        <Alert
          message={error}
          type="error"
          showIcon
          closable
          style={{ marginBottom: 16 }}
          className="fade-in"
        />
      )}

      {/* Quick Stats Grid - All Same Size */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={12} md={6}>
          <Card
            className="stat-card hover-lift fade-in-up"
            style={{ animationDelay: '0.1s', height: 160 }}
            bodyStyle={{ padding: 16, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
          >
            <div style={{ textAlign: 'center' }}>
              <Avatar
                size={48}
                style={{ backgroundColor: 'rgba(245, 158, 11, 0.15)', marginBottom: 8, border: '2px solid #F59E0B' }}
                icon={<FireOutlined style={{ color: '#F59E0B', fontSize: 24 }} />}
              />
              <Statistic
                title={<Text style={{ fontSize: 12, color: '#9CA3AF' }}>Current Streak</Text>}
                value={stats?.streak_length || 0}
                suffix={<Text style={{ fontSize: 12, color: '#9CA3AF' }}>days</Text>}
                valueStyle={{ fontSize: 24, fontWeight: 700, color: '#F59E0B' }}
              />
            </div>
          </Card>
        </Col>
        <Col xs={12} sm={12} md={6}>
          <Card
            className="stat-card hover-lift fade-in-up"
            style={{ animationDelay: '0.2s', height: 160 }}
            bodyStyle={{ padding: 16, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
          >
            <div style={{ textAlign: 'center' }}>
              <Avatar
                size={48}
                style={{ backgroundColor: 'rgba(74, 222, 183, 0.15)', marginBottom: 8, border: '2px solid #4ADEB7' }}
                icon={<SmileOutlined style={{ color: '#4ADEB7', fontSize: 24 }} />}
              />
              <Statistic
                title={<Text style={{ fontSize: 12, color: '#9CA3AF' }}>Weekly Mood</Text>}
                value={stats?.average_mood_7_days?.toFixed(1) || '-'}
                suffix={<Text style={{ fontSize: 12, color: '#9CA3AF' }}>/ 10</Text>}
                valueStyle={{ fontSize: 24, fontWeight: 700, color: moodInfo.color }}
              />
            </div>
          </Card>
        </Col>
        <Col xs={12} sm={12} md={6}>
          <Card
            className="stat-card hover-lift fade-in-up"
            style={{ animationDelay: '0.3s', height: 160 }}
            bodyStyle={{ padding: 16, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
          >
            <div style={{ textAlign: 'center' }}>
              <Avatar
                size={48}
                style={{ backgroundColor: 'rgba(122, 137, 156, 0.15)', marginBottom: 8, border: '2px solid #7A899C' }}
                icon={getTrendIcon(stats?.mood_trend || 'stable')}
              />
              <Statistic
                title={<Text style={{ fontSize: 12, color: '#9CA3AF' }}>Mood Trend</Text>}
                value={stats?.mood_trend || 'stable'}
                valueStyle={{
                  fontSize: 20,
                  fontWeight: 700,
                  color: getTrendColor(stats?.mood_trend || 'stable'),
                  textTransform: 'capitalize',
                }}
              />
            </div>
          </Card>
        </Col>
        <Col xs={12} sm={12} md={6}>
          <Card
            className="stat-card hover-lift fade-in-up"
            style={{ animationDelay: '0.4s', height: 160 }}
            bodyStyle={{ padding: 16, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
          >
            <div style={{ textAlign: 'center' }}>
              <Avatar
                size={48}
                style={{ backgroundColor: 'rgba(42, 31, 74, 0.4)', marginBottom: 8, border: '2px solid #2A1F4A' }}
                icon={<CalendarOutlined style={{ color: '#7A899C', fontSize: 24 }} />}
              />
              <Statistic
                title={<Text style={{ fontSize: 12, color: '#9CA3AF' }}>Total Check-ins</Text>}
                value={stats?.total_checkins || 0}
                valueStyle={{ fontSize: 24, fontWeight: 700, color: '#7A899C' }}
              />
            </div>
          </Card>
        </Col>
      </Row>

      {/* Daily Check-in & Today's Focus - 2-Card Grid */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <Card
            className="hover-lift fade-in-up"
            style={{
              background: 'rgba(74, 222, 183, 0.1)',
              borderRadius: 16,
              height: '100%',
              border: '1px solid rgba(74, 222, 183, 0.3)',
            }}
            bodyStyle={{ padding: 20 }}
          >
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: 12 }}>
              <Avatar
                size={40}
                style={{ backgroundColor: 'rgba(74, 222, 183, 0.2)', border: '2px solid #4ADEB7', marginRight: 12 }}
                icon={<HeartOutlined style={{ color: '#4ADEB7', fontSize: 20 }} />}
              />
              <Title level={4} style={{ color: '#4ADEB7', marginBottom: 0 }}>
                Daily Check-in
              </Title>
            </div>
            <Paragraph style={{ color: '#D1D5DB', fontSize: 14, marginBottom: 12 }}>
              Take a moment to check in with yourself. How are you feeling right now?
            </Paragraph>
            <div
              onClick={() => navigate('/checkin')}
              style={{
                backgroundColor: '#4ADEB7',
                color: '#0A0F29',
                fontWeight: 600,
                border: 'none',
                borderRadius: 10,
                padding: '10px 20px',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: 8,
              }}
              className="pulse-hover"
            >
              Start Check-in <ArrowRightOutlined />
            </div>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card
            className="hover-lift fade-in-up"
            style={{ borderRadius: 16, height: '100%' }}
            bodyStyle={{ padding: 20 }}
          >
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: 12 }}>
              <Avatar
                size={40}
                style={{ backgroundColor: 'rgba(252, 211, 77, 0.2)', border: '2px solid #FCD34D', marginRight: 12 }}
                icon={<TrophyOutlined style={{ color: '#FCD34D', fontSize: 20 }} />}
              />
              <Title level={4} style={{ color: '#D1D5DB', marginBottom: 0 }}>
                Today's Focus
              </Title>
            </div>
            {user?.has_adhd && (
              <div
                style={{
                  padding: 12,
                  background: 'rgba(245, 158, 11, 0.1)',
                  borderRadius: 10,
                  marginBottom: 8,
                  border: '1px solid rgba(245, 158, 11, 0.2)',
                }}
              >
                <Text strong style={{ color: '#F59E0B', fontSize: 13 }}>ADHD Support Tools</Text>
                <br />
                <Text style={{ color: '#D1D5DB', fontSize: 12 }}>
                  Time blindness support, task breakdown, focus reminders
                </Text>
              </div>
            )}
            {user?.has_autism_spectrum && (
              <div
                style={{
                  padding: 12,
                  background: 'rgba(74, 222, 183, 0.1)',
                  borderRadius: 10,
                  marginBottom: 8,
                  border: '1px solid rgba(74, 222, 183, 0.2)',
                }}
              >
                <Text strong style={{ color: '#4ADEB7', fontSize: 13 }}>ASD Support Tools</Text>
                <br />
                <Text style={{ color: '#D1D5DB', fontSize: 12 }}>
                  Sensory load tracking, emotion scaffolding, routine support
                </Text>
              </div>
            )}
            {user?.has_anxiety && (
              <div
                style={{
                  padding: 12,
                  background: 'rgba(42, 31, 74, 0.3)',
                  borderRadius: 10,
                  marginBottom: 8,
                  border: '1px solid rgba(42, 31, 74, 0.5)',
                }}
              >
                <Text strong style={{ color: '#7A899C', fontSize: 13 }}>Anxiety Support</Text>
                <br />
                <Text style={{ color: '#D1D5DB', fontSize: 12 }}>
                  Grounding exercises, breathing techniques, thought reframing
                </Text>
              </div>
            )}
            {!user?.has_adhd && !user?.has_autism_spectrum && !user?.has_anxiety && (
              <Text style={{ fontSize: 13, color: '#9CA3AF' }}>
                Complete regular check-ins to unlock personalized insights and recommendations
                tailored just for you.
              </Text>
            )}
          </Card>
        </Col>
      </Row>

      {/* Suggested Interventions */}
      {suggestedInterventions.length > 0 && (
        <Card
          className="hover-lift fade-in-up"
          style={{
            marginBottom: 24,
            borderRadius: 16,
            background: 'rgba(252, 211, 77, 0.1)',
            border: '2px solid rgba(252, 211, 77, 0.3)',
          }}
          bodyStyle={{ padding: 20 }}
        >
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
            <Avatar
              size={40}
              style={{ backgroundColor: 'rgba(252, 211, 77, 0.2)', border: '2px solid #FCD34D', marginRight: 12 }}
              icon={<ThunderboltOutlined style={{ color: '#FCD34D', fontSize: 20 }} />}
            />
            <Title level={4} style={{ color: '#FCD34D', marginBottom: 0 }}>
              Try These Exercises
            </Title>
          </div>
          <Row gutter={[12, 12]}>
            {suggestedInterventions.map((intervention) => (
              <Col xs={24} sm={8} key={intervention.id}>
                <Card
                  size="small"
                  hoverable
                  onClick={() => navigate('/interventions')}
                  style={{
                    cursor: 'pointer',
                    background: 'rgba(10, 15, 41, 0.6)',
                    border: '1px solid rgba(252, 211, 77, 0.2)',
                    borderRadius: 12,
                  }}
                  bodyStyle={{ padding: 12 }}
                >
                  <Text strong style={{ color: '#FCD34D', fontSize: 14, display: 'block', marginBottom: 4 }}>
                    {intervention.name}
                  </Text>
                  <Tag
                    style={{
                      backgroundColor: 'rgba(74, 222, 183, 0.2)',
                      color: '#4ADEB7',
                      border: '1px solid rgba(74, 222, 183, 0.4)',
                      fontSize: 10,
                    }}
                  >
                    {intervention.therapeutic_approach}
                  </Tag>
                  <Text style={{ color: '#9CA3AF', fontSize: 11, display: 'block', marginTop: 6 }}>
                    {intervention.total_completions} uses
                  </Text>
                </Card>
              </Col>
            ))}
          </Row>
        </Card>
      )}

      {/* Feature Cards - Same Size */}
      <Row gutter={[16, 16]}>
        <Col xs={24} md={8}>
          <Card
            hoverable
            onClick={() => navigate('/insights')}
            className="hover-lift fade-in-up"
            style={{ borderRadius: 16, textAlign: 'center', cursor: 'pointer', height: 180 }}
            bodyStyle={{ padding: 20, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
          >
            <BulbOutlined
              style={{ fontSize: 40, color: '#FCD34D', marginBottom: 12 }}
              className="float-animation"
            />
            <Title level={5} style={{ color: '#D1D5DB', marginBottom: 8 }}>Personal Insights</Title>
            <Text style={{ color: '#9CA3AF', fontSize: 13 }}>
              AI-powered mood predictions and patterns
            </Text>
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card
            hoverable
            onClick={() => navigate('/analytics')}
            className="hover-lift fade-in-up"
            style={{ borderRadius: 16, textAlign: 'center', cursor: 'pointer', height: 180 }}
            bodyStyle={{ padding: 20, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
          >
            <BarChartOutlined
              style={{ fontSize: 40, color: '#4ADEB7', marginBottom: 12 }}
              className="float-animation"
            />
            <Title level={5} style={{ color: '#D1D5DB', marginBottom: 8 }}>ML Analytics</Title>
            <Text style={{ color: '#9CA3AF', fontSize: 13 }}>
              Deep dive into your wellness data
            </Text>
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card
            hoverable
            onClick={() => navigate('/interventions')}
            className="hover-lift fade-in-up"
            style={{ borderRadius: 16, textAlign: 'center', cursor: 'pointer', height: 180 }}
            bodyStyle={{ padding: 20, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
          >
            <HeartOutlined
              style={{ fontSize: 40, color: '#7A899C', marginBottom: 12 }}
              className="float-animation"
            />
            <Title level={5} style={{ color: '#D1D5DB', marginBottom: 8 }}>Interventions</Title>
            <Text style={{ color: '#9CA3AF', fontSize: 13 }}>
              Evidence-based wellness techniques
            </Text>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

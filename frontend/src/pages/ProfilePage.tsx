import { useState, useEffect } from 'react';
import { MainLayout } from '../components/layout/MainLayout';
import {
  Card,
  Row,
  Col,
  Typography,
  Button,
  Input,
  Avatar,
  Divider,
  Tag,
  Progress,
  Alert,
  Statistic,
  Switch,
  Form,
  message,
} from 'antd';
import {
  UserOutlined,
  LockOutlined,
  SettingOutlined,
  TrophyOutlined,
  FireOutlined,
  HeartOutlined,
  BulbOutlined,
  CheckCircleOutlined,
  EditOutlined,
  SafetyOutlined,
  BellOutlined,
  MoonOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '../stores/authStore';
import { api } from '../services/api';
import type { CheckinStats } from '../types';

const { Title, Text, Paragraph } = Typography;

export const ProfilePage = () => {
  const { user, logout } = useAuthStore();
  const [stats, setStats] = useState<CheckinStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [passwordForm] = Form.useForm();
  const [showPasswordChange, setShowPasswordChange] = useState(false);

  const [displayName, setDisplayName] = useState(user?.display_name || '');
  const [notifications, setNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(true);
  const [dailyReminder, setDailyReminder] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const statsData = await api.getCheckinStats();
        setStats(statsData);
      } catch (err) {
        console.error('Failed to fetch stats:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  const handleSaveProfile = () => {
    // In a real app, this would call the API
    message.success('Profile updated successfully!');
    setIsEditing(false);
  };

  const handlePasswordChange = () => {
    passwordForm.validateFields().then((values) => {
      if (values.newPassword !== values.confirmPassword) {
        message.error('Passwords do not match!');
        return;
      }
      // In a real app, this would call the API
      message.success('Password changed successfully!');
      setShowPasswordChange(false);
      passwordForm.resetFields();
    });
  };

  const getAchievementBadge = (count: number) => {
    if (count >= 100) return { icon: '🏆', title: 'Wellness Champion', color: '#FCD34D' };
    if (count >= 50) return { icon: '🌟', title: 'Dedicated Tracker', color: '#F59E0B' };
    if (count >= 25) return { icon: '💪', title: 'Consistency Builder', color: '#4ADEB7' };
    if (count >= 10) return { icon: '🌱', title: 'Growing Stronger', color: '#7A899C' };
    return { icon: '🌼', title: 'Getting Started', color: '#9CA3AF' };
  };

  const badge = getAchievementBadge(stats?.total_checkins || 0);

  return (
    <MainLayout>
      <div style={{ padding: '24px', maxWidth: 1400, margin: '0 auto' }}>
        {/* Hero Section */}
        <div
          className="hero-section fade-in-up"
          style={{
            background: 'linear-gradient(135deg, #1C2340 0%, #0A0F29 100%)',
          }}
        >
          <Row align="middle" gutter={24}>
            <Col xs={24} md={16}>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
                <Avatar
                  size={80}
                  style={{
                    backgroundColor: '#4ADEB7',
                    fontSize: 36,
                    marginRight: 20,
                    border: '4px solid rgba(74, 222, 183, 0.3)',
                  }}
                  icon={<UserOutlined />}
                >
                  {user?.display_name?.charAt(0).toUpperCase()}
                </Avatar>
                <div>
                  <Title level={1} style={{ color: '#FFFFFF', marginBottom: 0 }}>
                    {user?.display_name || 'User'}
                  </Title>
                  <Text style={{ color: '#D1D5DB', fontSize: 16 }}>
                    {user?.email}
                  </Text>
                  <div style={{ marginTop: 8 }}>
                    <Tag
                      style={{
                        backgroundColor: 'rgba(74, 222, 183, 0.2)',
                        color: '#4ADEB7',
                        border: '1px solid rgba(74, 222, 183, 0.4)',
                        padding: '4px 12px',
                        borderRadius: 12,
                        fontSize: 12,
                      }}
                    >
                      Member since {user?.created_at ? new Date(user.created_at).toLocaleDateString('en-US', { month: 'long', year: 'numeric' }) : 'N/A'}
                    </Tag>
                  </div>
                </div>
              </div>
            </Col>
            <Col xs={24} md={8} style={{ textAlign: 'right' }}>
              <div style={{ display: 'inline-block', textAlign: 'center' }}>
                <div style={{ fontSize: 48, marginBottom: 8 }}>{badge.icon}</div>
                <Tag
                  style={{
                    backgroundColor: `${badge.color}30`,
                    color: badge.color,
                    border: `2px solid ${badge.color}`,
                    padding: '6px 16px',
                    borderRadius: 12,
                    fontSize: 14,
                    fontWeight: 600,
                  }}
                >
                  {badge.title}
                </Tag>
              </div>
            </Col>
          </Row>
        </div>

        {/* Quick Stats */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={8}>
            <Card
              className="hover-lift"
              style={{ textAlign: 'center', borderRadius: 16 }}
              bodyStyle={{ padding: 16 }}
            >
              <Avatar
                size={48}
                style={{
                  backgroundColor: 'rgba(245, 158, 11, 0.15)',
                  marginBottom: 8,
                  border: '2px solid #F59E0B',
                }}
                icon={<FireOutlined style={{ color: '#F59E0B', fontSize: 24 }} />}
              />
              <Statistic
                title={<Text style={{ color: '#9CA3AF', fontSize: 12 }}>Current Streak</Text>}
                value={stats?.streak_length || 0}
                suffix="days"
                valueStyle={{ color: '#F59E0B', fontWeight: 700, fontSize: 24 }}
              />
            </Card>
          </Col>
          <Col xs={8}>
            <Card
              className="hover-lift"
              style={{ textAlign: 'center', borderRadius: 16 }}
              bodyStyle={{ padding: 16 }}
            >
              <Avatar
                size={48}
                style={{
                  backgroundColor: 'rgba(74, 222, 183, 0.15)',
                  marginBottom: 8,
                  border: '2px solid #4ADEB7',
                }}
                icon={<HeartOutlined style={{ color: '#4ADEB7', fontSize: 24 }} />}
              />
              <Statistic
                title={<Text style={{ color: '#9CA3AF', fontSize: 12 }}>Total Check-ins</Text>}
                value={stats?.total_checkins || 0}
                valueStyle={{ color: '#4ADEB7', fontWeight: 700, fontSize: 24 }}
              />
            </Card>
          </Col>
          <Col xs={8}>
            <Card
              className="hover-lift"
              style={{ textAlign: 'center', borderRadius: 16 }}
              bodyStyle={{ padding: 16 }}
            >
              <Avatar
                size={48}
                style={{
                  backgroundColor: 'rgba(122, 137, 156, 0.15)',
                  marginBottom: 8,
                  border: '2px solid #7A899C',
                }}
                icon={<TrophyOutlined style={{ color: '#7A899C', fontSize: 24 }} />}
              />
              <Statistic
                title={<Text style={{ color: '#9CA3AF', fontSize: 12 }}>Avg Mood</Text>}
                value={stats?.average_mood_7_days?.toFixed(1) || '-'}
                suffix="/10"
                valueStyle={{ color: '#7A899C', fontWeight: 700, fontSize: 24 }}
              />
            </Card>
          </Col>
        </Row>

        {/* Profile Settings */}
        <Row gutter={[16, 16]}>
          <Col xs={24} md={12}>
            <Card
              className="hover-lift"
              style={{ borderRadius: 16, height: '100%' }}
              bodyStyle={{ padding: 20 }}
            >
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: 20 }}>
                <Avatar
                  size={40}
                  style={{ backgroundColor: 'rgba(74, 222, 183, 0.2)', border: '2px solid #4ADEB7', marginRight: 12 }}
                  icon={<EditOutlined style={{ color: '#4ADEB7', fontSize: 20 }} />}
                />
                <Title level={4} style={{ color: '#D1D5DB', marginBottom: 0 }}>
                  Profile Information
                </Title>
              </div>

              <div style={{ marginBottom: 16 }}>
                <Text style={{ color: '#9CA3AF', fontSize: 12, display: 'block', marginBottom: 4 }}>
                  Display Name
                </Text>
                {isEditing ? (
                  <Input
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    style={{ borderRadius: 10 }}
                    size="large"
                  />
                ) : (
                  <Text style={{ color: '#D1D5DB', fontSize: 16, display: 'block' }}>
                    {user?.display_name}
                  </Text>
                )}
              </div>

              <div style={{ marginBottom: 16 }}>
                <Text style={{ color: '#9CA3AF', fontSize: 12, display: 'block', marginBottom: 4 }}>
                  Email
                </Text>
                <Text style={{ color: '#D1D5DB', fontSize: 16 }}>{user?.email}</Text>
              </div>

              <div style={{ marginBottom: 16 }}>
                <Text style={{ color: '#9CA3AF', fontSize: 12, display: 'block', marginBottom: 4 }}>
                  Mental Health Focus
                </Text>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                  {user?.has_adhd && (
                    <Tag style={{ backgroundColor: 'rgba(245, 158, 11, 0.2)', color: '#F59E0B', border: '1px solid rgba(245, 158, 11, 0.4)', borderRadius: 8 }}>
                      ADHD Support
                    </Tag>
                  )}
                  {user?.has_autism_spectrum && (
                    <Tag style={{ backgroundColor: 'rgba(74, 222, 183, 0.2)', color: '#4ADEB7', border: '1px solid rgba(74, 222, 183, 0.4)', borderRadius: 8 }}>
                      ASD Support
                    </Tag>
                  )}
                  {user?.has_anxiety && (
                    <Tag style={{ backgroundColor: 'rgba(122, 137, 156, 0.2)', color: '#7A899C', border: '1px solid rgba(122, 137, 156, 0.4)', borderRadius: 8 }}>
                      Anxiety Support
                    </Tag>
                  )}
                  {!user?.has_adhd && !user?.has_autism_spectrum && !user?.has_anxiety && (
                    <Text style={{ color: '#9CA3AF', fontSize: 13 }}>No specific focus areas set</Text>
                  )}
                </div>
              </div>

              {isEditing ? (
                <div style={{ display: 'flex', gap: 12 }}>
                  <Button
                    type="primary"
                    onClick={handleSaveProfile}
                    style={{
                      backgroundColor: '#4ADEB7',
                      border: 'none',
                      color: '#0A0F29',
                      fontWeight: 600,
                      borderRadius: 10,
                    }}
                  >
                    Save Changes
                  </Button>
                  <Button onClick={() => setIsEditing(false)} style={{ borderRadius: 10 }}>
                    Cancel
                  </Button>
                </div>
              ) : (
                <Button
                  icon={<EditOutlined />}
                  onClick={() => setIsEditing(true)}
                  style={{
                    backgroundColor: 'rgba(74, 222, 183, 0.2)',
                    border: '1px solid rgba(74, 222, 183, 0.3)',
                    color: '#4ADEB7',
                    borderRadius: 10,
                  }}
                >
                  Edit Profile
                </Button>
              )}
            </Card>
          </Col>

          <Col xs={24} md={12}>
            <Card
              className="hover-lift"
              style={{ borderRadius: 16, height: '100%' }}
              bodyStyle={{ padding: 20 }}
            >
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: 20 }}>
                <Avatar
                  size={40}
                  style={{ backgroundColor: 'rgba(245, 158, 11, 0.2)', border: '2px solid #F59E0B', marginRight: 12 }}
                  icon={<SettingOutlined style={{ color: '#F59E0B', fontSize: 20 }} />}
                />
                <Title level={4} style={{ color: '#D1D5DB', marginBottom: 0 }}>
                  Settings
                </Title>
              </div>

              <div style={{ marginBottom: 20 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <BellOutlined style={{ color: '#FCD34D', marginRight: 8 }} />
                    <Text style={{ color: '#D1D5DB' }}>Push Notifications</Text>
                  </div>
                  <Switch
                    checked={notifications}
                    onChange={setNotifications}
                    style={{ backgroundColor: notifications ? '#4ADEB7' : undefined }}
                  />
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <MoonOutlined style={{ color: '#7A899C', marginRight: 8 }} />
                    <Text style={{ color: '#D1D5DB' }}>Dark Mode</Text>
                  </div>
                  <Switch
                    checked={darkMode}
                    onChange={setDarkMode}
                    style={{ backgroundColor: darkMode ? '#4ADEB7' : undefined }}
                  />
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <HeartOutlined style={{ color: '#4ADEB7', marginRight: 8 }} />
                    <Text style={{ color: '#D1D5DB' }}>Daily Check-in Reminder</Text>
                  </div>
                  <Switch
                    checked={dailyReminder}
                    onChange={setDailyReminder}
                    style={{ backgroundColor: dailyReminder ? '#4ADEB7' : undefined }}
                  />
                </div>
              </div>

              <Divider style={{ borderColor: 'rgba(74, 222, 183, 0.2)' }} />

              <div style={{ marginBottom: 16 }}>
                <Button
                  icon={<LockOutlined />}
                  onClick={() => setShowPasswordChange(!showPasswordChange)}
                  style={{
                    backgroundColor: 'rgba(122, 137, 156, 0.2)',
                    border: '1px solid rgba(122, 137, 156, 0.3)',
                    color: '#7A899C',
                    borderRadius: 10,
                    width: '100%',
                  }}
                >
                  Change Password
                </Button>
              </div>

              {showPasswordChange && (
                <Form form={passwordForm} layout="vertical" className="fade-in">
                  <Form.Item
                    name="currentPassword"
                    rules={[{ required: true, message: 'Please enter current password' }]}
                  >
                    <Input.Password
                      placeholder="Current Password"
                      style={{ borderRadius: 10 }}
                    />
                  </Form.Item>
                  <Form.Item
                    name="newPassword"
                    rules={[{ required: true, message: 'Please enter new password' }]}
                  >
                    <Input.Password
                      placeholder="New Password"
                      style={{ borderRadius: 10 }}
                    />
                  </Form.Item>
                  <Form.Item
                    name="confirmPassword"
                    rules={[{ required: true, message: 'Please confirm new password' }]}
                  >
                    <Input.Password
                      placeholder="Confirm New Password"
                      style={{ borderRadius: 10 }}
                    />
                  </Form.Item>
                  <div style={{ display: 'flex', gap: 12 }}>
                    <Button
                      type="primary"
                      onClick={handlePasswordChange}
                      style={{
                        backgroundColor: '#4ADEB7',
                        border: 'none',
                        color: '#0A0F29',
                        fontWeight: 600,
                        borderRadius: 10,
                      }}
                    >
                      Update Password
                    </Button>
                    <Button
                      onClick={() => {
                        setShowPasswordChange(false);
                        passwordForm.resetFields();
                      }}
                      style={{ borderRadius: 10 }}
                    >
                      Cancel
                    </Button>
                  </div>
                </Form>
              )}

              <Button
                danger
                icon={<SafetyOutlined />}
                onClick={() => {
                  logout();
                  window.location.href = '/login';
                }}
                style={{
                  marginTop: 16,
                  width: '100%',
                  borderRadius: 10,
                }}
              >
                Sign Out
              </Button>
            </Card>
          </Col>
        </Row>

        {/* Achievements Section */}
        <Card
          className="hover-lift fade-in-up"
          style={{ marginTop: 24, borderRadius: 16 }}
          bodyStyle={{ padding: 20 }}
        >
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 20 }}>
            <Avatar
              size={40}
              style={{ backgroundColor: 'rgba(252, 211, 77, 0.2)', border: '2px solid #FCD34D', marginRight: 12 }}
              icon={<TrophyOutlined style={{ color: '#FCD34D', fontSize: 20 }} />}
            />
            <Title level={4} style={{ color: '#D1D5DB', marginBottom: 0 }}>
              Achievements & Milestones
            </Title>
          </div>

          <Row gutter={[16, 16]}>
            <Col xs={12} sm={8} md={6}>
              <Card
                size="small"
                style={{
                  textAlign: 'center',
                  background: stats && stats.total_checkins >= 1 ? 'rgba(74, 222, 183, 0.15)' : 'rgba(42, 31, 74, 0.3)',
                  border: stats && stats.total_checkins >= 1 ? '2px solid #4ADEB7' : '1px solid rgba(74, 222, 183, 0.1)',
                  borderRadius: 12,
                }}
                bodyStyle={{ padding: 12 }}
              >
                <div style={{ fontSize: 32, marginBottom: 4 }}>🌱</div>
                <Text strong style={{ color: '#4ADEB7', fontSize: 12, display: 'block' }}>First Check-in</Text>
                {stats && stats.total_checkins >= 1 ? (
                  <CheckCircleOutlined style={{ color: '#4ADEB7', fontSize: 16, marginTop: 4 }} />
                ) : (
                  <Text style={{ color: '#9CA3AF', fontSize: 10 }}>Not yet</Text>
                )}
              </Card>
            </Col>
            <Col xs={12} sm={8} md={6}>
              <Card
                size="small"
                style={{
                  textAlign: 'center',
                  background: stats && stats.streak_length >= 7 ? 'rgba(245, 158, 11, 0.15)' : 'rgba(42, 31, 74, 0.3)',
                  border: stats && stats.streak_length >= 7 ? '2px solid #F59E0B' : '1px solid rgba(245, 158, 11, 0.1)',
                  borderRadius: 12,
                }}
                bodyStyle={{ padding: 12 }}
              >
                <div style={{ fontSize: 32, marginBottom: 4 }}>🔥</div>
                <Text strong style={{ color: '#F59E0B', fontSize: 12, display: 'block' }}>7-Day Streak</Text>
                {stats && stats.streak_length >= 7 ? (
                  <CheckCircleOutlined style={{ color: '#F59E0B', fontSize: 16, marginTop: 4 }} />
                ) : (
                  <Text style={{ color: '#9CA3AF', fontSize: 10 }}>{stats?.streak_length || 0}/7 days</Text>
                )}
              </Card>
            </Col>
            <Col xs={12} sm={8} md={6}>
              <Card
                size="small"
                style={{
                  textAlign: 'center',
                  background: stats && stats.total_checkins >= 25 ? 'rgba(252, 211, 77, 0.15)' : 'rgba(42, 31, 74, 0.3)',
                  border: stats && stats.total_checkins >= 25 ? '2px solid #FCD34D' : '1px solid rgba(252, 211, 77, 0.1)',
                  borderRadius: 12,
                }}
                bodyStyle={{ padding: 12 }}
              >
                <div style={{ fontSize: 32, marginBottom: 4 }}>💪</div>
                <Text strong style={{ color: '#FCD34D', fontSize: 12, display: 'block' }}>25 Check-ins</Text>
                {stats && stats.total_checkins >= 25 ? (
                  <CheckCircleOutlined style={{ color: '#FCD34D', fontSize: 16, marginTop: 4 }} />
                ) : (
                  <Text style={{ color: '#9CA3AF', fontSize: 10 }}>{stats?.total_checkins || 0}/25</Text>
                )}
              </Card>
            </Col>
            <Col xs={12} sm={8} md={6}>
              <Card
                size="small"
                style={{
                  textAlign: 'center',
                  background: stats && stats.total_checkins >= 100 ? 'rgba(122, 137, 156, 0.15)' : 'rgba(42, 31, 74, 0.3)',
                  border: stats && stats.total_checkins >= 100 ? '2px solid #7A899C' : '1px solid rgba(122, 137, 156, 0.1)',
                  borderRadius: 12,
                }}
                bodyStyle={{ padding: 12 }}
              >
                <div style={{ fontSize: 32, marginBottom: 4 }}>🏆</div>
                <Text strong style={{ color: '#7A899C', fontSize: 12, display: 'block' }}>Wellness Champion</Text>
                {stats && stats.total_checkins >= 100 ? (
                  <CheckCircleOutlined style={{ color: '#7A899C', fontSize: 16, marginTop: 4 }} />
                ) : (
                  <Text style={{ color: '#9CA3AF', fontSize: 10 }}>{stats?.total_checkins || 0}/100</Text>
                )}
              </Card>
            </Col>
          </Row>
        </Card>
      </div>
    </MainLayout>
  );
};

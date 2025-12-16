import { ReactNode } from 'react';
import { Layout, Menu, Avatar, Dropdown, Typography } from 'antd';
import {
  HomeOutlined,
  HeartOutlined,
  AppstoreOutlined,
  SettingOutlined,
  LogoutOutlined,
  UserOutlined,
  SafetyOutlined,
  BulbOutlined,
  BarChartOutlined,
  BookOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';
import { FireflyLogo } from '../common/FireflyLogo';

const { Header, Content, Footer } = Layout;
const { Text } = Typography;

interface Props {
  children: ReactNode;
}

export const MainLayout = ({ children }: Props) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();

  const menuItems = [
    {
      key: '/dashboard',
      icon: <HomeOutlined style={{ fontSize: 16 }} />,
      label: 'Home',
    },
    {
      key: '/checkin',
      icon: <HeartOutlined style={{ fontSize: 16 }} />,
      label: 'Check-in',
    },
    {
      key: '/journal',
      icon: <BookOutlined style={{ fontSize: 16 }} />,
      label: 'Journal',
    },
    {
      key: '/insights',
      icon: <BulbOutlined style={{ fontSize: 16 }} />,
      label: 'Insights',
    },
    {
      key: '/analytics',
      icon: <BarChartOutlined style={{ fontSize: 16 }} />,
      label: 'Analytics',
    },
    {
      key: '/interventions',
      icon: <AppstoreOutlined style={{ fontSize: 16 }} />,
      label: 'Tools',
    },
    {
      key: '/crisis',
      icon: <SafetyOutlined style={{ fontSize: 16 }} />,
      label: 'Safety',
    },
  ];

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profile',
      onClick: () => navigate('/profile'),
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Settings',
      onClick: () => navigate('/profile'),
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      onClick: async () => {
        await logout();
        navigate('/login');
      },
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: '#050816',
          padding: '0 20px',
          borderBottom: '1px solid rgba(74, 222, 183, 0.2)',
          height: 64,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
          <div
            style={{
              marginRight: 24,
              cursor: 'pointer',
              flexShrink: 0,
            }}
            onClick={() => navigate('/dashboard')}
          >
            <FireflyLogo size={44} showText={false} />
          </div>
          <Menu
            theme="dark"
            mode="horizontal"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={({ key }) => navigate(key)}
            style={{
              backgroundColor: 'transparent',
              borderBottom: 'none',
              flex: 1,
              minWidth: 0,
              lineHeight: '62px',
            }}
          />
        </div>

        <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
          <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', flexShrink: 0 }}>
            <Avatar
              icon={<UserOutlined />}
              style={{ backgroundColor: '#4ADEB7', marginRight: 8 }}
            />
            <Text style={{ color: '#D1D5DB' }}>
              {user?.display_name || user?.email?.split('@')[0] || 'User'}
            </Text>
          </div>
        </Dropdown>
      </Header>

      <Content style={{ backgroundColor: '#0A0F29', padding: 0 }}>
        {children}
      </Content>

      <Footer style={{ textAlign: 'center', backgroundColor: '#0A0F29', borderTop: '1px solid rgba(74, 222, 183, 0.2)', padding: '16px 50px' }}>
        <Text style={{ color: '#9CA3AF' }}>
          Firefly Mental Health Platform &copy; {new Date().getFullYear()} | Your data is encrypted and secure
        </Text>
      </Footer>
    </Layout>
  );
};

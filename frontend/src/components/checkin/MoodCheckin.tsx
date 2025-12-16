import { useState } from 'react';
import { Card, Button, Input, Typography, Space, Row, Col, Alert, Progress, Steps } from 'antd';
import {
  SmileOutlined,
  FrownOutlined,
  MehOutlined,
  ThunderboltOutlined,
  HeartOutlined,
  CheckCircleFilled,
  LeftOutlined,
  RightOutlined,
  HomeOutlined,
  CarOutlined,
  ShopOutlined,
  CoffeeOutlined,
  LaptopOutlined,
  TeamOutlined,
  UserOutlined,
  TrophyOutlined,
} from '@ant-design/icons';
import type { CheckinCreate, CheckinResponse } from '../../types';
import { api } from '../../services/api';
import { InterventionCard } from '../interventions/InterventionCard';
import { CrisisAlert } from '../crisis/CrisisAlert';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

// Mood emojis with descriptions
const MOOD_OPTIONS = [
  { score: 1, emoji: '😭', label: 'Terrible', color: '#ff4d4f' },
  { score: 2, emoji: '😢', label: 'Bad', color: '#ff7875' },
  { score: 3, emoji: '😟', label: 'Poor', color: '#ffa39e' },
  { score: 4, emoji: '😕', label: 'Meh', color: '#ffbb96' },
  { score: 5, emoji: '😐', label: 'Okay', color: '#ffd591' },
  { score: 6, emoji: '🙂', label: 'Fine', color: '#ffe58f' },
  { score: 7, emoji: '😊', label: 'Good', color: '#b7eb8f' },
  { score: 8, emoji: '😄', label: 'Great', color: '#95de64' },
  { score: 9, emoji: '🥳', label: 'Amazing', color: '#73d13d' },
  { score: 10, emoji: '🤩', label: 'Fantastic', color: '#52c41a' },
];

// Energy levels with visual representation
const ENERGY_OPTIONS = [
  { level: 1, icon: '🪫', label: 'Empty', color: '#ff4d4f' },
  { level: 2, icon: '🔋', label: 'Very Low', color: '#ff7875' },
  { level: 3, icon: '🔋', label: 'Low', color: '#ffa39e' },
  { level: 4, icon: '🔋', label: 'Below Avg', color: '#ffbb96' },
  { level: 5, icon: '🔋', label: 'Medium', color: '#ffd591' },
  { level: 6, icon: '🔋', label: 'Decent', color: '#ffe58f' },
  { level: 7, icon: '🔋', label: 'Good', color: '#b7eb8f' },
  { level: 8, icon: '🔋', label: 'High', color: '#95de64' },
  { level: 9, icon: '⚡', label: 'Very High', color: '#73d13d' },
  { level: 10, icon: '⚡', label: 'Supercharged', color: '#52c41a' },
];

// Emotions with emojis
const EMOTION_OPTIONS = [
  { name: 'anxiety', emoji: '😰', color: '#ff7875' },
  { name: 'stress', emoji: '😫', color: '#ff9c6e' },
  { name: 'sadness', emoji: '😢', color: '#5cdbd3' },
  { name: 'anger', emoji: '😤', color: '#ff4d4f' },
  { name: 'overwhelm', emoji: '🤯', color: '#ff85c0' },
  { name: 'fear', emoji: '😨', color: '#b37feb' },
  { name: 'calm', emoji: '😌', color: '#69c0ff' },
  { name: 'joy', emoji: '😊', color: '#ffc53d' },
  { name: 'hopeful', emoji: '🌟', color: '#ffd666' },
  { name: 'tired', emoji: '😴', color: '#d9d9d9' },
  { name: 'restless', emoji: '😣', color: '#ffa940' },
  { name: 'focused', emoji: '🎯', color: '#73d13d' },
  { name: 'disconnected', emoji: '🫥', color: '#bfbfbf' },
  { name: 'lonely', emoji: '🥺', color: '#91caff' },
  { name: 'grateful', emoji: '🙏', color: '#95de64' },
  { name: 'irritated', emoji: '😒', color: '#ffc069' },
];

// Context options
const LOCATION_OPTIONS = [
  { value: 'home', label: 'Home', icon: <HomeOutlined />, emoji: '🏠' },
  { value: 'office', label: 'Office', icon: <LaptopOutlined />, emoji: '💼' },
  { value: 'commute', label: 'Commute', icon: <CarOutlined />, emoji: '🚗' },
  { value: 'outdoors', label: 'Outdoors', icon: <span>🌳</span>, emoji: '🌳' },
  { value: 'cafe', label: 'Cafe', icon: <CoffeeOutlined />, emoji: '☕' },
  { value: 'friend_home', label: 'Friend\'s', icon: <TeamOutlined />, emoji: '👥' },
];

const ACTIVITY_OPTIONS = [
  { value: 'working', emoji: '💻', label: 'Working' },
  { value: 'meeting', emoji: '📊', label: 'Meeting' },
  { value: 'relaxing', emoji: '🛋️', label: 'Relaxing' },
  { value: 'exercise', emoji: '🏃', label: 'Exercise' },
  { value: 'hobby', emoji: '🎨', label: 'Hobby' },
  { value: 'socializing', emoji: '💬', label: 'Socializing' },
];

const SOCIAL_OPTIONS = [
  { value: 'alone', emoji: '🧘', label: 'Alone' },
  { value: 'with_friends', emoji: '👯', label: 'With Friends' },
  { value: 'with_family', emoji: '👨‍👩‍👧‍👦', label: 'With Family' },
  { value: 'colleagues', emoji: '👔', label: 'With Colleagues' },
];

interface Props {
  onComplete?: (response: CheckinResponse) => void;
}

export const MoodCheckin = ({ onComplete }: Props) => {
  const [step, setStep] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [moodScore, setMoodScore] = useState<number | null>(null);
  const [energyLevel, setEnergyLevel] = useState<number | null>(null);
  const [selectedEmotions, setSelectedEmotions] = useState<string[]>([]);
  const [location, setLocation] = useState<string | null>(null);
  const [activity, setActivity] = useState<string | null>(null);
  const [social, setSocial] = useState<string | null>(null);
  const [journalText, setJournalText] = useState('');

  const [response, setResponse] = useState<CheckinResponse | null>(null);
  const [showCrisisAlert, setShowCrisisAlert] = useState(false);

  const toggleEmotion = (emotion: string) => {
    setSelectedEmotions((prev) =>
      prev.includes(emotion) ? prev.filter((e) => e !== emotion) : [...prev, emotion]
    );
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    setError(null);

    const checkinData: CheckinCreate = {
      mood_score: moodScore!,
      energy_level: energyLevel!,
      emotion_tags: selectedEmotions,
      journal_text: journalText || undefined,
      context_location: location || undefined,
      context_activity: activity || undefined,
      context_social: social || undefined,
    };

    try {
      const result = await api.createCheckin(checkinData);
      setResponse(result);

      if (result.crisis_alert) {
        setShowCrisisAlert(true);
      } else {
        setStep(5);
      }

      onComplete?.(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save check-in');
    } finally {
      setIsLoading(false);
    }
  };

  const canProceed = () => {
    switch (step) {
      case 0:
        return moodScore !== null;
      case 1:
        return energyLevel !== null;
      case 2:
        return selectedEmotions.length > 0;
      case 3:
        return true; // Context is optional
      case 4:
        return true; // Journal is optional
      default:
        return false;
    }
  };

  if (showCrisisAlert && response?.crisis_resources) {
    return (
      <CrisisAlert
        resources={response.crisis_resources}
        onSafeNow={() => {
          setShowCrisisAlert(false);
          setStep(5);
        }}
      />
    );
  }

  const stepTitles = ['Mood', 'Energy', 'Emotions', 'Context', 'Journal', 'Complete'];

  return (
    <div style={{ maxWidth: 900, margin: '0 auto' }}>
      {step < 5 && (
        <div className="fade-in" style={{ marginBottom: 20 }}>
          <Progress
            percent={(step / 4) * 100}
            showInfo={false}
            strokeColor={{
              '0%': '#FCD34D',
              '100%': '#F59E0B',
            }}
            trailColor="rgba(252, 211, 77, 0.1)"
            strokeWidth={6}
            style={{ borderRadius: 10 }}
          />
          <Steps
            current={step}
            size="small"
            style={{ marginTop: 12 }}
            items={stepTitles.slice(0, 5).map((title, i) => ({
              title: i === step ? title : '',
              icon: i < step ? <CheckCircleFilled style={{ color: '#52c41a' }} /> : undefined,
            }))}
          />
        </div>
      )}

      {error && (
        <Alert
          message={error}
          type="error"
          showIcon
          closable
          style={{ marginBottom: 16, borderRadius: 12 }}
          className="fade-in"
        />
      )}

      {/* Step 0: Mood Selection */}
      {step === 0 && (
        <Card
          className="fade-in-up hover-lift"
          style={{ borderRadius: 16, textAlign: 'center' }}
          bodyStyle={{ padding: '20px 24px' }}
        >
          <div style={{ marginBottom: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12 }}>
            <SmileOutlined style={{ fontSize: 32, color: '#FCD34D' }} />
            <div>
              <Title level={4} style={{ marginBottom: 0 }}>
                How are you feeling right now?
              </Title>
              <Text type="secondary" style={{ fontSize: 13 }}>
                Tap the emoji that best matches your mood
              </Text>
            </div>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(10, 1fr)',
              gap: 10,
              marginBottom: 16,
            }}
          >
            {MOOD_OPTIONS.map((option) => (
              <div
                key={option.score}
                onClick={() => setMoodScore(option.score)}
                className={moodScore === option.score ? 'pulse-hover' : ''}
                style={{
                  cursor: 'pointer',
                  padding: 12,
                  borderRadius: 12,
                  border: moodScore === option.score ? `3px solid ${option.color}` : '2px solid #f0f0f0',
                  backgroundColor: moodScore === option.score ? `${option.color}20` : 'white',
                  transition: 'all 0.3s ease',
                  transform: moodScore === option.score ? 'scale(1.08)' : 'scale(1)',
                }}
              >
                <div style={{ fontSize: 32 }}>{option.emoji}</div>
                <div style={{ fontSize: 11, marginTop: 4, fontWeight: 600, color: option.color }}>
                  {option.label}
                </div>
                <div style={{ fontSize: 10, color: '#888' }}>{option.score}</div>
              </div>
            ))}
          </div>

          {moodScore && (
            <div
              className="fade-in"
              style={{
                padding: 16,
                background: `${MOOD_OPTIONS[moodScore - 1].color}20`,
                borderRadius: 12,
              }}
            >
              <Text style={{ fontSize: 24 }}>
                {MOOD_OPTIONS[moodScore - 1].emoji} {MOOD_OPTIONS[moodScore - 1].label} ({moodScore}/10)
              </Text>
            </div>
          )}
        </Card>
      )}

      {/* Step 1: Energy Level */}
      {step === 1 && (
        <Card
          className="fade-in-up hover-lift"
          style={{ borderRadius: 16, textAlign: 'center' }}
          bodyStyle={{ padding: '20px 24px' }}
        >
          <div style={{ marginBottom: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12 }}>
            <ThunderboltOutlined style={{ fontSize: 32, color: '#faad14' }} />
            <div>
              <Title level={4} style={{ marginBottom: 0 }}>
                What's your energy level?
              </Title>
              <Text type="secondary" style={{ fontSize: 13 }}>
                Select how energized you feel
              </Text>
            </div>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(10, 1fr)',
              gap: 10,
              marginBottom: 16,
            }}
          >
            {ENERGY_OPTIONS.map((option) => (
              <div
                key={option.level}
                onClick={() => setEnergyLevel(option.level)}
                style={{
                  cursor: 'pointer',
                  padding: 12,
                  borderRadius: 12,
                  border: energyLevel === option.level ? `3px solid ${option.color}` : '2px solid #f0f0f0',
                  backgroundColor: energyLevel === option.level ? `${option.color}20` : 'white',
                  transition: 'all 0.3s ease',
                  transform: energyLevel === option.level ? 'scale(1.08)' : 'scale(1)',
                }}
              >
                <div style={{ fontSize: 28 }}>{option.icon}</div>
                <div style={{ fontSize: 11, marginTop: 4, fontWeight: 600, color: option.color }}>
                  {option.label}
                </div>
                <div style={{ fontSize: 10, color: '#888' }}>{option.level}</div>
              </div>
            ))}
          </div>

          {energyLevel && (
            <div
              className="fade-in"
              style={{
                padding: 16,
                background: `${ENERGY_OPTIONS[energyLevel - 1].color}20`,
                borderRadius: 12,
              }}
            >
              <Text style={{ fontSize: 24 }}>
                {ENERGY_OPTIONS[energyLevel - 1].icon} {ENERGY_OPTIONS[energyLevel - 1].label} ({energyLevel}/10)
              </Text>
            </div>
          )}
        </Card>
      )}

      {/* Step 2: Emotions */}
      {step === 2 && (
        <Card
          className="fade-in-up hover-lift"
          style={{ borderRadius: 16, textAlign: 'center' }}
          bodyStyle={{ padding: '20px 24px' }}
        >
          <div style={{ marginBottom: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12 }}>
            <HeartOutlined style={{ fontSize: 32, color: '#eb2f96' }} />
            <div>
              <Title level={4} style={{ marginBottom: 0 }}>
                What emotions are present?
              </Title>
              <Text type="secondary" style={{ fontSize: 13 }}>
                Select all that apply (tap to toggle)
              </Text>
            </div>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(8, 1fr)',
              gap: 10,
              marginBottom: 16,
            }}
          >
            {EMOTION_OPTIONS.map((option) => (
              <div
                key={option.name}
                onClick={() => toggleEmotion(option.name)}
                style={{
                  cursor: 'pointer',
                  padding: 10,
                  borderRadius: 10,
                  border: selectedEmotions.includes(option.name)
                    ? `3px solid ${option.color}`
                    : '2px solid #f0f0f0',
                  backgroundColor: selectedEmotions.includes(option.name) ? `${option.color}20` : 'white',
                  transition: 'all 0.3s ease',
                  transform: selectedEmotions.includes(option.name) ? 'scale(1.08)' : 'scale(1)',
                }}
              >
                <div style={{ fontSize: 22 }}>{option.emoji}</div>
                <div style={{ fontSize: 10, marginTop: 2, fontWeight: 600, textTransform: 'capitalize' }}>
                  {option.name}
                </div>
              </div>
            ))}
          </div>

          {selectedEmotions.length > 0 && (
            <div className="fade-in" style={{ padding: 12, background: '#f9f0ff', borderRadius: 12 }}>
              <Text strong>Selected: </Text>
              {selectedEmotions.map((e) => {
                const opt = EMOTION_OPTIONS.find((o) => o.name === e);
                return (
                  <span key={e} style={{ margin: '0 4px', fontSize: 18 }}>
                    {opt?.emoji}
                  </span>
                );
              })}
            </div>
          )}
        </Card>
      )}

      {/* Step 3: Context */}
      {step === 3 && (
        <Card
          className="fade-in-up hover-lift"
          style={{ borderRadius: 16, textAlign: 'center' }}
          bodyStyle={{ padding: '20px 24px' }}
        >
          <div style={{ marginBottom: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12 }}>
            <span style={{ fontSize: 32 }}>🌍</span>
            <div>
              <Title level={4} style={{ marginBottom: 0 }}>
                What's your context? (Optional)
              </Title>
              <Text type="secondary" style={{ fontSize: 13 }}>
                This helps identify patterns and triggers
              </Text>
            </div>
          </div>

          <div style={{ marginBottom: 20 }}>
            <Text strong style={{ display: 'block', marginBottom: 12 }}>
              Where are you?
            </Text>
            <Row gutter={[12, 12]}>
              {LOCATION_OPTIONS.map((opt) => (
                <Col span={8} key={opt.value}>
                  <div
                    onClick={() => setLocation(location === opt.value ? null : opt.value)}
                    style={{
                      cursor: 'pointer',
                      padding: 12,
                      borderRadius: 12,
                      border: location === opt.value ? '3px solid #2D7D90' : '2px solid #f0f0f0',
                      backgroundColor: location === opt.value ? '#e6f7ff' : 'white',
                      transition: 'all 0.3s ease',
                    }}
                  >
                    <div style={{ fontSize: 24 }}>{opt.emoji}</div>
                    <div style={{ fontSize: 12, marginTop: 4 }}>{opt.label}</div>
                  </div>
                </Col>
              ))}
            </Row>
          </div>

          <div style={{ marginBottom: 20 }}>
            <Text strong style={{ display: 'block', marginBottom: 12 }}>
              What are you doing?
            </Text>
            <Row gutter={[12, 12]}>
              {ACTIVITY_OPTIONS.map((opt) => (
                <Col span={8} key={opt.value}>
                  <div
                    onClick={() => setActivity(activity === opt.value ? null : opt.value)}
                    style={{
                      cursor: 'pointer',
                      padding: 12,
                      borderRadius: 12,
                      border: activity === opt.value ? '3px solid #52c41a' : '2px solid #f0f0f0',
                      backgroundColor: activity === opt.value ? '#f6ffed' : 'white',
                      transition: 'all 0.3s ease',
                    }}
                  >
                    <div style={{ fontSize: 24 }}>{opt.emoji}</div>
                    <div style={{ fontSize: 12, marginTop: 4 }}>{opt.label}</div>
                  </div>
                </Col>
              ))}
            </Row>
          </div>

          <div>
            <Text strong style={{ display: 'block', marginBottom: 12 }}>
              Who are you with?
            </Text>
            <Row gutter={[12, 12]}>
              {SOCIAL_OPTIONS.map((opt) => (
                <Col span={12} key={opt.value}>
                  <div
                    onClick={() => setSocial(social === opt.value ? null : opt.value)}
                    style={{
                      cursor: 'pointer',
                      padding: 12,
                      borderRadius: 12,
                      border: social === opt.value ? '3px solid #722ed1' : '2px solid #f0f0f0',
                      backgroundColor: social === opt.value ? '#f9f0ff' : 'white',
                      transition: 'all 0.3s ease',
                    }}
                  >
                    <div style={{ fontSize: 24 }}>{opt.emoji}</div>
                    <div style={{ fontSize: 12, marginTop: 4 }}>{opt.label}</div>
                  </div>
                </Col>
              ))}
            </Row>
          </div>
        </Card>
      )}

      {/* Step 4: Journal */}
      {step === 4 && (
        <Card
          className="fade-in-up hover-lift"
          style={{ borderRadius: 16 }}
          bodyStyle={{ padding: '20px 24px' }}
        >
          <div style={{ textAlign: 'center', marginBottom: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12 }}>
            <span style={{ fontSize: 32 }}>📝</span>
            <div>
              <Title level={4} style={{ marginBottom: 0 }}>
                Anything on your mind? (Optional)
              </Title>
              <Text type="secondary" style={{ fontSize: 13 }}>
                Writing can help process emotions. This is private and encrypted.
              </Text>
            </div>
          </div>

          <TextArea
            rows={4}
            value={journalText}
            onChange={(e) => setJournalText(e.target.value)}
            placeholder="Share your thoughts, feelings, or anything that's happening..."
            style={{ marginBottom: 12, borderRadius: 10, fontSize: 14 }}
          />

          <div style={{ textAlign: 'center' }}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              {journalText.length} characters
            </Text>
          </div>
        </Card>
      )}

      {/* Step 5: Complete */}
      {step === 5 && response && (
        <div className="fade-in-up">
          <Card
            style={{
              background: 'linear-gradient(135deg, #4ADEB7 0%, #2DD4BF 100%)',
              borderRadius: 20,
              textAlign: 'center',
              marginBottom: 24,
            }}
          >
            <TrophyOutlined style={{ fontSize: 64, color: '#FCD34D', marginBottom: 16 }} className="float-animation" />
            <Title level={2} style={{ color: '#0A0F29', marginBottom: 8 }}>
              Check-in Complete!
            </Title>
            <Paragraph style={{ color: '#0A0F29', fontSize: 16 }}>
              Great job taking care of yourself today!
            </Paragraph>
            <Row gutter={16} justify="center" style={{ marginTop: 24 }}>
              <Col>
                <div style={{ background: 'rgba(10, 15, 41, 0.2)', padding: 16, borderRadius: 12 }}>
                  <div style={{ fontSize: 32 }}>
                    {MOOD_OPTIONS[response.checkin.mood_score - 1]?.emoji}
                  </div>
                  <Text style={{ color: '#0A0F29', fontSize: 14 }}>
                    Mood: {response.checkin.mood_score}/10
                  </Text>
                </div>
              </Col>
              <Col>
                <div style={{ background: 'rgba(10, 15, 41, 0.2)', padding: 16, borderRadius: 12 }}>
                  <div style={{ fontSize: 32 }}>⚡</div>
                  <Text style={{ color: '#0A0F29', fontSize: 14 }}>
                    Energy: {response.checkin.energy_level}/10
                  </Text>
                </div>
              </Col>
            </Row>
          </Card>

          {response.recommendations.length > 0 && (
            <div>
              <Title level={4} style={{ marginBottom: 16 }}>
                <span style={{ marginRight: 8 }}>✨</span>
                Recommended for you:
              </Title>
              {response.recommendations.map((rec) => (
                <InterventionCard key={rec.intervention_id} recommendation={rec} />
              ))}
            </div>
          )}

          <Button
            type="primary"
            block
            size="large"
            onClick={() => {
              setStep(0);
              setMoodScore(null);
              setEnergyLevel(null);
              setSelectedEmotions([]);
              setLocation(null);
              setActivity(null);
              setSocial(null);
              setJournalText('');
              setResponse(null);
            }}
            style={{
              marginTop: 24,
              height: 56,
              borderRadius: 12,
              fontSize: 18,
              background: 'linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%)',
              border: 'none',
              color: '#0A0F29',
            }}
          >
            Start New Check-in
          </Button>
        </div>
      )}

      {/* Navigation Buttons */}
      {step < 5 && (
        <Row gutter={16} style={{ marginTop: 20 }}>
          <Col span={step > 0 ? 12 : 0}>
            {step > 0 && (
              <Button
                size="large"
                block
                icon={<LeftOutlined />}
                onClick={() => setStep(step - 1)}
                style={{ height: 48, borderRadius: 10, fontSize: 15 }}
              >
                Back
              </Button>
            )}
          </Col>
          <Col span={step > 0 ? 12 : 24}>
            {step < 4 && (
              <Button
                type="primary"
                size="large"
                block
                disabled={!canProceed()}
                onClick={() => setStep(step + 1)}
                style={{
                  height: 48,
                  borderRadius: 10,
                  fontSize: 15,
                  background: canProceed()
                    ? 'linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%)'
                    : undefined,
                  border: 'none',
                  color: canProceed() ? '#0A0F29' : undefined,
                }}
              >
                Continue <RightOutlined />
              </Button>
            )}
            {step === 4 && (
              <Button
                type="primary"
                size="large"
                block
                loading={isLoading}
                onClick={handleSubmit}
                style={{
                  height: 48,
                  borderRadius: 10,
                  fontSize: 15,
                  background: 'linear-gradient(135deg, #4ADEB7 0%, #2DD4BF 100%)',
                  border: 'none',
                  color: '#0A0F29',
                }}
              >
                Complete Check-in <CheckCircleFilled />
              </Button>
            )}
          </Col>
        </Row>
      )}
    </div>
  );
};

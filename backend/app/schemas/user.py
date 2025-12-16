"""
User schemas for API validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    email: EmailStr
    display_name: Optional[str] = None
    has_adhd: bool = False
    has_autism_spectrum: bool = False
    has_anxiety: bool = False
    has_depression: bool = False
    other_conditions: List[str] = []
    age_range: Optional[str] = None
    timezone: str = "UTC"


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    has_adhd: Optional[bool] = None
    has_autism_spectrum: Optional[bool] = None
    has_anxiety: Optional[bool] = None
    has_depression: Optional[bool] = None
    other_conditions: Optional[List[str]] = None
    age_range: Optional[str] = None
    timezone: Optional[str] = None
    data_sharing_consent: Optional[bool] = None
    research_participation: Optional[bool] = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    display_name: Optional[str]
    created_at: datetime
    is_active: bool
    is_premium: bool
    subscription_tier: str
    has_adhd: bool
    has_autism_spectrum: bool
    has_anxiety: bool
    has_depression: bool
    other_conditions: List[str]
    age_range: Optional[str]
    timezone: str
    data_sharing_consent: bool
    research_participation: bool

    class Config:
        from_attributes = True


class UserPreferencesBase(BaseModel):
    theme: str = "calm_light"
    font_family: str = "Inter"
    font_size: int = 16
    animation_speed: str = "normal"
    high_contrast: bool = False
    sound_enabled: bool = True
    haptic_feedback: bool = True
    notification_sound: str = "gentle_chime"
    reduce_motion: bool = False
    preferred_language: str = "en"
    communication_style: str = "warm"
    morning_checkin_enabled: bool = True
    morning_checkin_time: str = "08:00"
    evening_reflection_enabled: bool = True
    evening_reflection_time: str = "20:00"
    max_notifications_per_day: int = 3
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "07:00"
    time_blindness_support: bool = False
    task_breakdown_auto: bool = False
    hyperfocus_reminders: bool = False
    dopamine_reward_style: str = "standard"
    sensory_load_tracking: bool = False
    routine_deviation_alerts: bool = False
    emotion_scaffolding_level: int = 1


class UserPreferencesCreate(UserPreferencesBase):
    pass


class UserPreferencesUpdate(BaseModel):
    theme: Optional[str] = None
    font_family: Optional[str] = None
    font_size: Optional[int] = None
    animation_speed: Optional[str] = None
    high_contrast: Optional[bool] = None
    sound_enabled: Optional[bool] = None
    haptic_feedback: Optional[bool] = None
    notification_sound: Optional[str] = None
    reduce_motion: Optional[bool] = None
    preferred_language: Optional[str] = None
    communication_style: Optional[str] = None
    morning_checkin_enabled: Optional[bool] = None
    morning_checkin_time: Optional[str] = None
    evening_reflection_enabled: Optional[bool] = None
    evening_reflection_time: Optional[str] = None
    max_notifications_per_day: Optional[int] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    time_blindness_support: Optional[bool] = None
    task_breakdown_auto: Optional[bool] = None
    hyperfocus_reminders: Optional[bool] = None
    dopamine_reward_style: Optional[str] = None
    sensory_load_tracking: Optional[bool] = None
    routine_deviation_alerts: Optional[bool] = None
    emotion_scaffolding_level: Optional[int] = None


class UserPreferencesResponse(UserPreferencesBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

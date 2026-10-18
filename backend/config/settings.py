import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Wearable AI Security Assistant"
    VERSION: str = "1.0.0-mvp"
    DEBUG: bool = True
    
    # API & Host
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "*"]
    
    # AI Model Settings
    # Supports custom trained firearm/knife weights or fallback demo weights
    MODEL_PATH: str = os.getenv("MODEL_PATH", "models/trained/weapon_threat_yolov8.pt")
    FALLBACK_MODEL_PATH: str = "yolov8n.pt"
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.50
    IOU_THRESHOLD: float = 0.45
    INPUT_IMAGE_SIZE: int = 640
    
    # Predefined threat classes
    TARGET_THREAT_CLASSES: List[str] = [
        "firearm", "gun", "pistol", "rifle", "knife", "blade", "dagger", "grenade", "weapon"
    ]
    
    # Camera settings (Upgraded to 2K QHD 60 FPS)
    CAMERA_SOURCE: int = int(os.getenv("CAMERA_SOURCE", "0"))
    CAMERA_WIDTH: int = 2560
    CAMERA_HEIGHT: int = 1440
    CAMERA_FPS: int = 60
    
    # Alert & Cooldown
    ALERT_COOLDOWN_SECONDS: float = 3.0
    AUDIO_ALERTS_ENABLED_DEFAULT: bool = True
    SPEECH_WARNING_ENABLED: bool = True
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./security_assistant.db")
    
    # Strict Privacy Policy (hardcoded constraints)
    FACIAL_RECOGNITION_ENABLED: bool = False
    CONCEALED_WEAPON_MODE: bool = False
    STORE_FULL_VIDEO: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()



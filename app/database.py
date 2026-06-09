from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

from .config import settings

# Database URL from settings
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# 🔧 PRODUCTION FIX: Handle PostgreSQL URL format (Render provides postgres://)
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 🔧 PRODUCTION FIX: Better connection arguments
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,  # 🔧 Verifies connection before using
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Chat(Base):
    __tablename__ = "chats"

    id = Column(String(100), primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False, default="New Chat")
    messages = Column(JSON, default=[])
    
    # Chat metadata and statistics
    total_requests = Column(Integer, default=0)
    user_prompts = Column(JSON, default=[])
    models_used = Column(JSON, default=[])
    
    # Aggregated statistics
    total_carbon_emitted_kgco2 = Column(Float, default=0.0)
    total_energy_consumed_kwh = Column(Float, default=0.0)
    average_accuracy = Column(Float, default=0.0)
    total_tokens = Column(Integer, default=0)
    
    # Comparison data
    is_comparison = Column(Integer, default=0)
    comparison_models = Column(JSON, default=[])
    comparison_results = Column(JSON, default={})
    
    # Additional metadata
    code_generated = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class CarbonEstimate(Base):
    __tablename__ = "carbon_estimates"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False)
    response_text = Column(Text, nullable=True)
    model_name = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=True)

    # Token information
    tokens_input = Column(Integer, default=0)
    tokens_output = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)

    # Timing information
    inference_time_ms = Column(Integer, default=0)

    # Carbon estimates
    energy_consumed_kwh = Column(Float, default=0.0)
    carbon_emitted_kgco2 = Column(Float, default=0.0)

    # Accuracy information
    accuracy_scores = Column(JSON, default={})
    overall_accuracy = Column(Float, default=0.0)
    accuracy_level = Column(String(50), default="unknown")
    validation_results = Column(JSON, default={})
    detected_issues = Column(JSON, default=[])

    # Context and selection
    conversation_id = Column(String(100), nullable=True)
    is_best_model_selected = Column(String(5), default="false")
    selection_confidence = Column(Float, default=0.0)
    model_selection_rationale = Column(Text, nullable=True)
    candidate_models = Column(JSON, default=[])

    # Additional metadata
    estimation_method = Column(String(50), default="codecarbon")
    country_iso_code = Column(String(10), default="IND")
    grid_intensity = Column(Float, default=0.708)

    created_at = Column(DateTime, default=datetime.utcnow)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(100), primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    title = Column(String(200), nullable=True)
    summary = Column(Text, nullable=True)
    metadata_json = Column('metadata', JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class ModelSelectionHistory(Base):
    __tablename__ = "model_selection_history"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(100), nullable=True)
    prompt = Column(Text, nullable=True)
    selected_model = Column(String(100), nullable=False)
    confidence_score = Column(Float, default=0.0)
    candidate_models = Column(JSON, default=[])
    model_scores = Column(JSON, default={})
    selection_rationale = Column(Text, nullable=True)
    prompt_analysis = Column(JSON, default={})
    timestamp = Column(DateTime, default=datetime.utcnow)


def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print(f"✅ Database tables created at: {SQLALCHEMY_DATABASE_URL[:50]}...")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise


def get_db():
    """Dependency for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
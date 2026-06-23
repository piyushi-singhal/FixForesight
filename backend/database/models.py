from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.connection import Base

class Machine(Base):
    __tablename__ = "machines"
    
    machine_id = Column(String(50), primary_key=True)
    machine_name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)
    air_temperature = Column(Float, nullable=False)
    process_temperature = Column(Float, nullable=False)
    rotational_speed = Column(Integer, nullable=False)
    torque = Column(Float, nullable=False)
    tool_wear = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    predictions = relationship("Prediction", back_populates="machine", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="machine", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="machine", cascade="all, delete-orphan")
    work_orders = relationship("WorkOrder", back_populates="machine", cascade="all, delete-orphan")

class Prediction(Base):
    __tablename__ = "predictions"
    
    prediction_id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"))
    failure_probability = Column(Float, nullable=False)
    predicted_failure = Column(String(255), nullable=False)
    time_to_failure = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    machine = relationship("Machine", back_populates="predictions")
    recommendation = relationship("Recommendation", back_populates="prediction", cascade="all, delete-orphan", uselist=False)

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    recommendation_id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"))
    prediction_id = Column(Integer, ForeignKey("predictions.prediction_id", ondelete="CASCADE"), nullable=True)
    recommendation = Column(Text, nullable=False)
    priority = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    machine = relationship("Machine", back_populates="recommendations")
    prediction = relationship("Prediction", back_populates="recommendation")
    work_orders = relationship("WorkOrder", back_populates="recommendation")

class Alert(Base):
    __tablename__ = "alerts"
    
    alert_id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"))
    severity = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    machine = relationship("Machine", back_populates="alerts")

class PartInventory(Base):
    __tablename__ = "parts_inventory"
    
    part_id = Column(Integer, primary_key=True, autoincrement=True)
    part_name = Column(String(100), nullable=False, unique=True)
    quantity = Column(Integer, nullable=False)
    min_required = Column(Integer, nullable=False)
    unit_cost = Column(Float, nullable=False)

class WorkOrder(Base):
    __tablename__ = "work_orders"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"))
    recommendation_id = Column(Integer, ForeignKey("recommendations.recommendation_id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), nullable=False, default="open")
    priority = Column(String(50), nullable=False)
    action_required = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    machine = relationship("Machine", back_populates="work_orders")
    recommendation = relationship("Recommendation", back_populates="work_orders")

import enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

# --- 枚举定义 ---

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    DISPATCHER = "DISPATCHER"

class CourierStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"  # 空闲
    BUSY = "BUSY"            # 配送中
    OFF_DUTY = "OFF_DUTY"    # 下班

class PackageStatus(str, enum.Enum):
    PENDING = "PENDING"      # 待处理
    ASSIGNED = "ASSIGNED"    # 已分配
    IN_TRANSIT = "IN_TRANSIT"# 配送中
    DELIVERED = "DELIVERED"  # 已送达
    FAILED = "FAILED"        # 失败

class PlanStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    OPTIMIZING = "OPTIMIZING"
    READY = "READY"
    COMPLETED = "COMPLETED"

# --- 模型定义 ---

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.DISPATCHER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DeliveryStation(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    couriers = relationship("Courier", back_populates="station")
    plans = relationship("DeliveryPlan", back_populates="station")

class Courier(Base):
    __tablename__ = "couriers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(String)
    station_id = Column(Integer, ForeignKey("stations.id"))
    status = Column(Enum(CourierStatus), default=CourierStatus.OFF_DUTY)
    max_capacity = Column(Float, default=50.0) # 最大载货量
    
    station = relationship("DeliveryStation", back_populates="couriers")
    routes = relationship("DeliveryRoute", back_populates="courier")

class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)
    tracking_number = Column(String, unique=True, index=True)
    recipient_name = Column(String)
    recipient_phone = Column(String)
    recipient_address = Column(String)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    weight = Column(Float, default=1.0) # kg
    volume = Column(Float, default=0.1) # m3
    status = Column(Enum(PackageStatus), default=PackageStatus.PENDING)
    
    # 一个包裹属于某个计划中的某条路线（分配后）
    route_id = Column(Integer, ForeignKey("delivery_routes.id"), nullable=True)
    
    route = relationship("DeliveryRoute", back_populates="packages")

class DeliveryPlan(Base):
    __tablename__ = "delivery_plans"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    station_id = Column(Integer, ForeignKey("stations.id"))
    status = Column(Enum(PlanStatus), default=PlanStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 算法执行的元数据
    algorithm_meta = Column(JSON, nullable=True) # 记录使用的参数、K值等
    
    station = relationship("DeliveryStation", back_populates="plans")
    routes = relationship("DeliveryRoute", back_populates="plan", cascade="all, delete-orphan")

class DeliveryRoute(Base):
    __tablename__ = "delivery_routes"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("delivery_plans.id"))
    courier_id = Column(Integer, ForeignKey("couriers.id"), nullable=True)
    
    # 路径几何信息 (JSON format for frontend)
    # { "coordinates": [[lat, lon], ...], "distance": 12.5 }
    geo_json = Column(JSON, nullable=True) 
    
    total_distance = Column(Float, default=0.0)
    estimated_time = Column(Float, default=0.0) # minutes
    
    plan = relationship("DeliveryPlan", back_populates="routes")
    courier = relationship("Courier", back_populates="routes")
    packages = relationship("Package", back_populates="route")

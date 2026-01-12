from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.all_models import UserRole, CourierStatus, PackageStatus, PlanStatus

# --- 基础配置 ---
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# --- Station Schemas ---
class StationBase(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float

class StationCreate(StationBase):
    pass

class Station(StationBase, BaseSchema):
    id: int

# --- Courier Schemas ---
class CourierBase(BaseModel):
    name: str
    phone: str
    status: CourierStatus = CourierStatus.OFF_DUTY
    max_capacity: float = 50.0
    station_id: int

class CourierCreate(CourierBase):
    pass

class CourierUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[CourierStatus] = None
    max_capacity: Optional[float] = None
    station_id: Optional[int] = None

class Courier(CourierBase, BaseSchema):
    id: int

# --- Package Schemas ---
class PackageBase(BaseModel):
    tracking_number: str
    recipient_name: str
    recipient_phone: str
    recipient_address: str
    latitude: float
    longitude: float
    weight: float = 1.0
    volume: float = 0.1

class PackageCreate(PackageBase):
    pass

class PackageUpdate(BaseModel):
    status: Optional[PackageStatus] = None
    route_id: Optional[int] = None

class Package(PackageBase, BaseSchema):
    id: int
    status: PackageStatus
    route_id: Optional[int] = None

# --- Route Schemas ---
class RouteBase(BaseModel):
    plan_id: int
    courier_id: Optional[int] = None
    total_distance: float = 0.0
    estimated_time: float = 0.0
    geo_json: Optional[dict] = None

class Route(RouteBase, BaseSchema):
    id: int
    packages: List[Package] = []
    courier: Optional[Courier] = None

# --- Plan Schemas ---
class PlanBase(BaseModel):
    title: str
    station_id: int
    algorithm_meta: Optional[dict] = None

class PlanCreate(PlanBase):
    pass

class Plan(PlanBase, BaseSchema):
    id: int
    status: PlanStatus
    created_at: datetime
    routes: List[Route] = []

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.DISPATCHER

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase, BaseSchema):
    id: int
    is_active: bool
    created_at: datetime

class User(UserBase, BaseSchema):
    id: int
    is_active: bool
    created_at: datetime

# --- Auth Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.all_models import DeliveryRoute
from app.core.config import settings

# Create database session manually since we are running a standalone script
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def fix_route_history():
    routes = db.query(DeliveryRoute).all()
    print(f"Checking {len(routes)} routes for missing total_weight...")
    
    count = 0
    for route in routes:
        if route.geo_json and "total_weight" not in route.geo_json:
            # Modify the dict directly
            geo = dict(route.geo_json)
            # Estimate weight: 1.5kg per package avg if unknown
            pkg_count = geo.get("package_count", 0)
            
            # Since link is broken for old routes, we just estimate to clear the "0" display
            # For new routes, the code in dispatch_service.py will handle it correctly
            geo["total_weight"] = round(pkg_count * 1.5, 1) 
            
            route.geo_json = geo # Assign back to trigger update
            count += 1
    
    if count > 0:
        db.commit()
        print(f"Fixed {count} routes with estimated weights.")
    else:
        print("No routes needed fixing.")

if __name__ == "__main__":
    try:
        fix_route_history()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

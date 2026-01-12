from app.db.session import SessionLocal
from app.models.all_models import Package

db = SessionLocal()
try:
    # Update packages where weight is NULL
    db.query(Package).filter(Package.weight == None).update({Package.weight: 1.0}, synchronize_session=False)
    # Update packages where volume is NULL
    db.query(Package).filter(Package.volume == None).update({Package.volume: 0.1}, synchronize_session=False)
    db.commit()
    print("Backfilled weight and volume for packages.")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()

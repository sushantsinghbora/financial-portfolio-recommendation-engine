from app.database import SessionLocal
from app.services.ds_pipeline_service import (
    generate_ds_pipeline
)


db = SessionLocal()

try:

    portfolio_id = 3
    user_id = 1

    result = generate_ds_pipeline(
        db=db,
        portfolio_id=portfolio_id,
        user_id=user_id,
        risk_profile="moderate"
    )

    print("\n")
    print("=" * 60)
    print("DATA SCIENCE PIPELINE RESULT")
    print("=" * 60)

    print(result)

finally:
    db.close()
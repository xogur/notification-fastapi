from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.database.conn import db
from app.database.schema import Users

router = APIRouter()

@router.get("/")
async def index(session: Session = Depends(db.session)):
    """
    헬스체크 + 샘플 insert
    """
    user = Users(status="active", name="HelloWorld")
    session.add(user)
    session.commit()

    current_time = datetime.utcnow()
    return Response(
        f"Notification API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})"
    )

from dataclasses import asdict
from fastapi import FastAPI

from app.database.conn import db
from app.common.config import conf
from app.routes import index  # <- 라우터 import

def create_app():
    """
    앱 팩토리
    """
    c = conf()
    app = FastAPI()
    conf_dict = asdict(c)

    # DB 초기화 (startup 훅에서 테이블 자동 생성)
    db.init_app(app, **conf_dict)

    # 라우터 등록
    app.include_router(index.router)

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

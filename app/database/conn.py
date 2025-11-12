from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import logging

Base = declarative_base()  # <- 모델들이 반드시 이 Base를 상속하도록!

class SQLAlchemy:
    def __init__(self, app: FastAPI = None, **kwargs):
        self._engine = None
        self._SessionLocal = None
        if app is not None:
            self.init_app(app=app, **kwargs)

    def init_app(self, app: FastAPI, **kwargs):
        """
        DB 초기화 함수
        """
        database_url = kwargs.get("DB_URL")
        pool_recycle = kwargs.setdefault("DB_POOL_RECYCLE", 900)
        echo = kwargs.setdefault("DB_ECHO", True)

        self._engine = create_engine(
            database_url,
            echo=echo,
            pool_recycle=pool_recycle,
            pool_pre_ping=True,
        )
        self._SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )

        @app.on_event("startup")
        def startup():
            # 모델을 먼저 import 해서 metadata에 등록되게 한 뒤 create_all 호출
            from app.database import schema  # noqa: F401 (등록 목적)
            Base.metadata.create_all(bind=self._engine)
            logging.info("DB connected & tables created.")

        @app.on_event("shutdown")
        def shutdown():
            # 세션 팩토리의 close_all과 엔진 정리
            if self._SessionLocal:
                self._SessionLocal.close_all()
            if self._engine:
                self._engine.dispose()
            logging.info("DB disconnected")

    def get_db(self):
        """
        요청마다 DB 세션 유지
        """
        if self._SessionLocal is None:
            raise Exception("must call init_app first")
        db = None
        try:
            db = self._SessionLocal()
            yield db
        finally:
            if db is not None:
                db.close()

    @property
    def session(self):
        return self.get_db

    @property
    def engine(self):
        return self._engine


db = SQLAlchemy()

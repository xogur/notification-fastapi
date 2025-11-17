from datetime import datetime, timedelta

import bcrypt
import jwt
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app import models
from app.common.consts import JWT_SECRET, JWT_ALGORITHM
from app.database.conn import db
from app.database.schema import Users
from app.models import SnsType, Token, UserToken, UserRegister

router = APIRouter()


@router.post("/register/{sns_type}", status_code=201, response_model=Token)
async def register(sns_type: SnsType, reg_info: UserRegister, session: Session = Depends(db.session)):
    """
    회원가입 API
    """
    if sns_type == SnsType.email:
        # 1) 필수값 체크
        if not reg_info.email or not reg_info.pw:
            return JSONResponse(
                status_code=400,
                content=dict(msg="Email and PW must be provided"),
            )

        # 2) 이메일 중복 체크
        is_exist = await is_email_exist(reg_info.email)
        if is_exist:
            return JSONResponse(
                status_code=400,
                content=dict(msg="EMAIL_EXISTS"),
            )

        # 3) 비밀번호 해시 (DB에는 문자열로 저장)
        hashed_pw_bytes: bytes = bcrypt.hashpw(
            reg_info.pw.encode("utf-8"), bcrypt.gensalt()
        )
        hashed_pw_str: str = hashed_pw_bytes.decode("utf-8")

        # 4) 유저 생성
        new_user = Users.create(
            session,
            auto_commit=True,
            pw=hashed_pw_str,
            email=reg_info.email,
        )

        # 5) JWT 발급 (민감 정보는 제외)
        access_token = create_access_token(
            data=UserToken.from_orm(new_user).dict(
                exclude={"pw", "marketing_agree"}
            )
        )
        token = dict(Authorization=f"Bearer {access_token}")
        return token

    return JSONResponse(status_code=400, content=dict(msg="NOT_SUPPORTED"))


@router.post("/login/{sns_type}", status_code=200, response_model=Token)
async def login(sns_type: SnsType, user_info: UserRegister):
    """
    로그인 API
    """
    if sns_type == SnsType.email:
        # 1) 필수값 체크
        if not user_info.email or not user_info.pw:
            return JSONResponse(
                status_code=400,
                content=dict(msg="Email and PW must be provided"),
            )

        # 2) 가입 여부 확인
        is_exist = await is_email_exist(user_info.email)
        if not is_exist:
            return JSONResponse(
                status_code=400,
                content=dict(msg="NO_MATCH_USER"),
            )

        # 3) 사용자 조회
        user = Users.get(email=user_info.email)
        if not user:
            return JSONResponse(
                status_code=400,
                content=dict(msg="NO_MATCH_USER"),
            )

        # 4) 비밀번호 검증
        # - user.pw 는 DB에 문자열로 저장되어 있음
        # - checkpw 의 hashed_password 인자는 bytes 여야 하므로 encode 필요
        is_verified = bcrypt.checkpw(
            user_info.pw.encode("utf-8"),  # 입력한 비밀번호(plain)
            user.pw.encode("utf-8"),      # DB에 저장된 해시 문자열 → bytes
        )

        if not is_verified:
            return JSONResponse(
                status_code=400,
                content=dict(msg="NO_MATCH_USER"),
            )

        # 5) JWT 발급
        access_token = create_access_token(
            data=UserToken.from_orm(user).dict(
                exclude={"pw", "marketing_agree"}
            )
        )
        token = dict(Authorization=f"Bearer {access_token}")
        return token

    return JSONResponse(status_code=400, content=dict(msg="NOT_SUPPORTED"))


async def is_email_exist(email: str) -> bool:
    """
    이메일 존재 여부 확인
    """
    get_email = Users.get(email=email)
    if get_email:
        return True
    return False


def create_access_token(*, data: dict = None, expires_delta: int = None) -> str:
    """
    JWT Access Token 생성
    :param data: 토큰 payload
    :param expires_delta: 만료 시간 (시간 단위, 없으면 exp 미설정)
    """
    to_encode = data.copy()
    if expires_delta:
        to_encode.update(
            {"exp": datetime.utcnow() + timedelta(hours=expires_delta)}
        )
    encoded_jwt = jwt.encode(
        to_encode,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )
    return encoded_jwt

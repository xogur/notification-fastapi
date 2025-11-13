from enum import Enum

from pydantic import ConfigDict
from pydantic.main import BaseModel
from pydantic.networks import EmailStr
from typing import Optional


class UserRegister(BaseModel):
    # pip install 'pydantic[email]'
    email: EmailStr = None
    pw: str = None

    class Config:
        # v2에서도 여전히 동작 (orm_mode → from_attributes 로 바꾸는 것이 권장)
        from_attributes = True


class SnsType(str, Enum):
    email: str = "email"
    facebook: str = "facebook"
    google: str = "google"
    kakao: str = "kakao"


class Token(BaseModel):
    Authorization: str = None


class UserToken(BaseModel):
    id: int
    pw: str = None
    email: EmailStr

    name: Optional[str] = None
    phone_number: Optional[str] = None
    profile_img: Optional[str] = None
    sns_type: Optional[str] = None

    class Config:
        from_attributes = True
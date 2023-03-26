from typing import Type, Any, Optional
from pydantic import BaseModel, SecretStr


class CommandData(BaseModel):
    schema_type: str = 'CommandData'
    kwargs: Optional[dict]
    expression: Optional[str] 
    exit_status: int = 0


class AuthData(BaseModel):
    schema_type: str = 'AuthData'
    username: Optional[str]
    password: Optional[str]


class StartupData(BaseModel):
    schema_type: str = 'StartupData'
    initial: bool = False
    username: Optional[str]
    url: Optional[str]


class ResponseData(BaseModel):
    schema_type: str = 'ResponseData'
    response_message: Any
    exit_status: int = 0


class FormRequest(BaseModel):
    schema_type: str = 'FormRequest'
    arguments_list: list


class FormResponse(BaseModel):
    schema_type: str = 'FormResponse'
    arguments_list: dict | str


class AuthRequest(BaseModel):
    schema_type: str = 'AuthRequest'

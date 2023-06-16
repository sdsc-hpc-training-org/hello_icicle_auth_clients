'''
SCHEMAS
These are standardized JSON serializable data formats to make socket operations on the localhost client-server smoother.
'''
from typing import Any, Optional, Literal

from pydantic import BaseModel, Field, validator


class BaseSchema(BaseModel):
    schema_type: str
    request_content: dict = dict()
    message: dict = dict()
    error: str = str()
    system: str = str()
    pwd: str = str()


class CommandData(BaseSchema):
    """
    Command execution request sent from the client to the server to execute a specified command
    """
    schema_type = 'CommandData'


class PasswordAuthData(BaseSchema):
    """
    Sends credentials from the client to the server for auth to Tapis services
    """
    schema_type: str = 'PasswordAuthData'
    username: Optional[str]
    password: Optional[str]


class StartupData(BaseSchema):
    """
    used only during connection inintialization between the client and server to transmit startup data
    """
    schema_type: str = 'StartupData'
    initial: bool = False
    username: Optional[str]
    url: Optional[str]


class ResponseData(BaseSchema):
    """
    data from the server to the client with return data from commands, as well as errors
    """
    schema_type: str = 'ResponseData'
    url: str = str()
    active_username: str = str()
    exit_status = 0
    

class FormRequest(BaseSchema):
    """
    Request seperate input for some command parameters. If the arguments_list is empty, this will be interpreted as an expression request for something like neo4j
    """
    schema_type: str = 'FormRequest'


class FormResponse(BaseSchema):
    """
    respond to a form request with proper data
    """
    schema_type: str = 'FormResponse'


class AuthRequest(BaseSchema):
    """
    Request auth credentials from the client
    """
    schema_type: str = 'AuthRequest'
    auth_request_type: Literal["password", "device_code", "federated", "requested", "success"]


class ConfirmationRequest(BaseSchema):
    """
    ask the client for confirmation to carry out an action
    """
    schema_type: str = 'ConfirmationRequest'
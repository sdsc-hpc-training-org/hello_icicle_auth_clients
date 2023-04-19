'''
SCHEMAS
These are standardized JSON serializable data formats to make socket operations on the localhost client-server smoother.
'''
from typing import Any, Optional
from pydantic import BaseModel


class CommandData(BaseModel):
    """
    Command execution request sent from the client to the server to execute a specified command
    """
    schema_type: str = 'CommandData'
    kwargs: Optional[dict]
    expression: Optional[str] 
    exit_status: int = 0


class AuthData(BaseModel):
    """
    Sends credentials from the client to the server for auth to Tapis services
    """
    schema_type: str = 'AuthData'
    username: Optional[str]
    password: Optional[str]


class StartupData(BaseModel):
    """
    used only during connection inintialization between the client and server to transmit startup data
    """
    schema_type: str = 'StartupData'
    initial: bool = False
    username: Optional[str]
    url: Optional[str]


class ResponseData(BaseModel):
    """
    data from the server to the client with return data from commands, as well as errors
    """
    schema_type: str = 'ResponseData'
    response_message: Any
    exit_status: int = 0


class FormRequest(BaseModel):
    """
    Request seperate input for some command parameters. If the arguments_list is empty, this will be interpreted as an expression request for something like neo4j
    """
    schema_type: str = 'FormRequest'
    arguments_list: list


class FormResponse(BaseModel):
    """
    respond to a form request with proper data
    """
    schema_type: str = 'FormResponse'
    arguments_list: dict | str


class AuthRequest(BaseModel):
    """
    Request auth credentials from the client
    """
    schema_type: str = 'AuthRequest'
    requires_username: bool = True
    secure_input: bool = False


class ConfirmationRequest(BaseModel):
    """
    ask the client for confirmation to carry out an action
    """
    schema_type: str = 'ConfirmationRequest'
    message: str

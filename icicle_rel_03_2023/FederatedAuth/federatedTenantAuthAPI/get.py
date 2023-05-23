import requests


def get_client_code(tenant: str) -> str:
    """
    Retrieve a Tapis tenant's corresponding client ID 
    for federated authentication
    """
    
# Federated Tenant Auth API
This is a simple API to access a json file mapping Tapis tenants to their respective authenticator clients. The user can call "get_client_code" in order to retrieve the client ID, which can then be used in code to authenticate to a Tapis tenant using Tapis federated authentication.

## installation
Pypi: https://pypi.org/project/TapisFederatedAuthClientAPI/0.0.1/

`pip install TapisFederatedAuthClientAPI`

`from federatedTenantAuthAPI import get`

`get.get_client_code({client code})`

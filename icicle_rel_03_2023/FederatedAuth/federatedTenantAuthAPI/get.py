import requests
import json


def get_client_code(tenant: str) -> str:
    """
    Retrieve a Tapis tenant's corresponding client ID 
    for federated authentication
    """
    tenant_client_json = requests.get(r"https://raw.githubusercontent.com/sdsc-hpc-training-org/hello_icicle_auth_clients/main/icicle_rel_03_2023/FederatedAuth/tenantAuth.json")
    client_data = json.loads(tenant_client_json.content)
    try:
        return client_data[tenant]
    except KeyError:
        return None


if __name__ == "__main__":
    print(get_client_code("icicle.tapis.io"))
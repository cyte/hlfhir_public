import os,globals as globals
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential


def set_azure_params():
    os.environ["AZURE_TENANT_ID"]=globals.conf_dict['az_tenant_id']
    os.environ["AZURE_CLIENT_ID"] = globals.conf_dict['az_client_id']
    os.environ["AZURE_CLIENT_SECRET"]=globals.conf_dict['az_client_secret']

    globals.keyVaultName = globals.conf_dict['az_kv_name']
    globals.KVUri = f"https://{globals.keyVaultName}.vault.azure.net"

def obtain_key(secretName):
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=globals.KVUri, credential=credential)
    retrieved_secret = client.get_secret(secretName)
    return retrieved_secret.value
    



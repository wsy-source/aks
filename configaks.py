import yaml
import os
from azure.identity import ClientSecretCredential, AzureAuthorityHosts
from azure.mgmt.storage import StorageManagementClient
import subprocess
from kubernetes import config, client


def generic_storage_account_key(tenant_id: str, client_id: str, client_secret: str, account_name: str,
                                subscription_id: str, resource_group_name: str):
    credential = ClientSecretCredential(tenant_id=tenant_id,
                                        client_id=client_id,
                                        client_secret=client_secret,
                                        authority=AzureAuthorityHosts.AZURE_CHINA)
    client = StorageManagementClient(credential=credential,
                                     subscription_id=subscription_id,
                                     base_url='https://management.chinacloudapi.cn',
                                     credential_scopes=['https://management.core.chinacloudapi.cn/.default'])
    key_client = client.storage_accounts.list_keys(resource_group_name=resource_group_name,
                                                   account_name=account_name)
    for key in key_client.keys:
        if key.key_name == 'key1':
            return key.value


config.load_kube_config()
client_secret = "l2Qsz5.-2~jQZuPOuz.6z.7Tu30FI3lr0R"
client_id = "aa74a549-0561-4de0-bd85-e50fe96fc71e"
tenant_id = "1a6857ff-9169-4a8a-83bf-5de6129d38f6"
subscription_id = '1204c64b-8557-4ee6-975f-c531df82f703'
resource_group_name = 'rg-viper-portal-dms-uat'

# os.chdir('C:\\Users\\10950')

if __name__ == '__main__':
    for i in range(1, 11):
        storage_account_name = f'originfileshare{i}uat'
        key = generic_storage_account_key(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret,
                                          account_name=storage_account_name, subscription_id=subscription_id,
                                          resource_group_name=resource_group_name)
        cmd = []
        cmd.append('az account set -s 1204c64b-8557-4ee6-975f-c531df82f703')
        cmd.append('az aks get-credentials -g rg-viper-portal-dms-uat -n viper-aks-uat')
        for c in cmd:
            resusult = subprocess.getoutput(cmd=c)
            print(resusult)
        cmd = f'kubectl create secret generic {storage_account_name} --from-literal=azurestorageaccountname={storage_account_name} --from-literal=azurestorageaccountkey={key}'
        resusult = subprocess.getoutput(cmd=cmd)
        print(resusult)
        with open('pv.yaml', 'r') as fp:
            pv = yaml.load(fp.read(), yaml.Loader)
            pv['metadata']['name'] = storage_account_name
            pv['spec']['csi']['nodeStageSecretRef']['name'] = storage_account_name
            client.CoreV1Api().create_persistent_volume(body=pv)

        with open('pvc.yaml', 'r') as fp:
            pvc = yaml.load(fp.read(), yaml.Loader)
            pvc['metadata']['name'] = storage_account_name
            pvc['spec']['volumeName'] = storage_account_name
            result = client.CoreV1Api().create_namespaced_persistent_volume_claim(body=pvc, namespace='default')

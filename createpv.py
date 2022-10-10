from azure.keyvault.secrets import SecretClient
from azure.identity import ClientSecretCredential, AzureAuthorityHosts
from kubernetes import config, client

# credential = ClientSecretCredential(tenant_id='1a6857ff-9169-4a8a-83bf-5de6129d38f6',
#                                     client_id='2adc7898-6cb4-4b5e-8231-6d6d5bbdd149',
#                                     client_secret='18A_C30jGDJ7ulLb-y~O3X-25zA9ztNDEh',
#                                     authority=AzureAuthorityHosts.AZURE_CHINA)
# secret_client = SecretClient('https://wsykeyvault2.vault.azure.cn/', credential=credential)
#
# secret = secret_client.get_secret('aks')
# config_dict = eval(secret.value)
# config.load_kube_config_from_dict(config_dict)
config.load_config()


def create_persistent_volume(resource_group: str, share_name: str, access_modes: list, capacity: str,
                             storage_class_name: str, secret_name: str, persistent_volume: str, **kwargs):
    read_only = False
    secret_namespace = 'default'
    persistent_volume_reclaim_policy = 'Retain'

    if kwargs.__contains__('secret_namespace'):
        secret_namespace = kwargs.pop('secret_namespace')
    if kwargs.__contains__('read_only'):
        read_only = kwargs.pop('read_only')
    if kwargs.__contains__('persistent_volume_reclaim_policy'):
        persistent_volume_reclaim_policy = kwargs.pop('read_only')
    source = client.V1AzureFilePersistentVolumeSource(read_only=read_only, secret_name=secret_name,
                                                      secret_namespace=secret_namespace, share_name=share_name)

    volume_spec = client.V1PersistentVolumeSpec(access_modes=access_modes, capacity={'storage': capacity},
                                                storage_class_name=storage_class_name,
                                                persistent_volume_reclaim_policy=persistent_volume_reclaim_policy, csi={
            'driver': 'file.csi.azure.com',
            'readOnly': False,
            'volumeHandle': 'unique-volumeid',
            'volumeAttributes': {
                'resourceGroup': resource_group,
                'shareName': share_name
            },
            'nodeStageSecretRef': {
                'name': 'azure-secret',
                'namespace': 'default'
            }
        })
    volume = client.V1PersistentVolume(api_version='v1', metadata={'name': persistent_volume},
                                       spec=volume_spec)
    client.CoreV1Api().create_persistent_volume(body=volume)


create_persistent_volume(resource_group='rg-wsy-aks', share_name='fileshare_01', access_modes=['ReadWriteMany'],
                         storage_class_name='azurefile-csi-premium', secret_name='azure-secret2',
                         persistent_volume='fileshare01', capacity='100Gi'
                         )

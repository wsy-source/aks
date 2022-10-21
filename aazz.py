import os

import yaml
from kubernetes import client, config, watch
import json
import logging

import azure.functions as func
import datetime
import uuid
from azure.identity import ClientSecretCredential, AzureAuthorityHosts
from azure.mgmt.containerservice import ContainerServiceClient
from kubernetes import watch, client, config
from azure.keyvault.secrets import SecretClient
from azure.servicebus import ServiceBusClient, ServiceBusSubQueue

DATABASE_NAME = 'aks'
NODE_CONTAINER_NAME = 'akscontainer'

# def get_aks_config() -> dict:
#     credential = ClientSecretCredential(tenant_id='1a6857ff-9169-4a8a-83bf-5de6129d38f6',
#                                         client_id='2adc7898-6cb4-4b5e-8231-6d6d5bbdd149',
#                                         client_secret='18A_C30jGDJ7ulLb-y~O3X-25zA9ztNDEh',
#                                         authority=AzureAuthorityHosts.AZURE_CHINA)
#     secret_client = SecretClient('https://wsykeyvault2.vault.azure.cn/', credential=credential)
#     secret = secret_client.get_secret('aks')
#     config_dict = eval(secret.value)
#     return config_dict
#
#
# config.load_kube_config_from_dict(get_aks_config())
# v1 = client.BatchV1Api()
#
# count = 0
# print('开始监视')
# watcher = watch.Watch()
# for e in watcher.stream(v1.list_namespaced_job, namespace='default'):
#     type = e['type']
#
#     print(e['object'].to_dict()['metadata']['name'])
#     raw_object = e['raw_object']
# if type == 'DELETED':
#     print('监视到node拉去镜像成功！')
#     count += 1
# if type == 'MODIFIED':
#     ###
#     # 预先拉去镜像失败逻辑
#     # count += 1
#     pass
# if count == 1:
#     watcher.stop()

# client = ServiceBusClient.from_connection_string(
#     'Endpoint=sb://downloadservicebus.servicebus.chinacloudapi.cn/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=HGRF97Eq73vAipRazihPCwucf89OlMqy6xWsO5KXOhI=')
#
#
#
# receiver = client.get_subscription_receiver(topic_name='to_be_create_pod',subscription_name='startcreate')
# messages = receiver.receive_messages(max_message_count=70)
# sender = client.get_topic_sender(topic_name='to_be_create_pod')
#
#
#
#
#
#
# for message in messages:
#     print(message)
#     client.get_topic_sender(topic_name='to_be_create_pod')
#     receiver.complete_message(message=message)
#     # sender.schedule_messages(message, datetime.datetime.utcnow() + datetime.timedelta(minutes=3))
#
demo = yaml.load(open('config_ops_user_modify.yml', 'r'), yaml.Loader)

print(demo)
print(demo['user_arguments']['scene_parser']['directory'])

with open('demo.yaml', 'w') as fp:
    fp.write(yaml.dump(demo))

# from azure.cosmos import CosmosClient
from azure.core.paging import ItemPaged

from azure.storage.fileshare import ShareServiceClient, ShareFileClient

# cosmos_client = CosmosClient.from_connection_string(
#     'AccountEndpoint=https://aksdb.documents.azure.cn:443/;AccountKey=9tTJZA1SZCbKxNsdUSuCIU21jsIw1Qk5vkPNGSaSooX1alUaWmYuTlhx6Mm35VShfX44rmJ7VhDiYAcziXPHHQ==;')
#

# aks = cosmos_client.get_database_client('aks')

# nodes = aks.get_container_client('nodes')

# items = nodes.query_items(query='SELECT * FROM c WHERE c.node_status = "running" and c.node_pool != "agentpool"  OFFSET 0 limit 1',enable_cross_partition_query=True)


# if len(list(items)):
#     print(list(items))
#     print('hello')

# def get_file_share_client(share_name: str, file_path: str) -> ShareFileClient:
#     share_client = ShareServiceClient(account_url='https://iptempfsxets000000.file.core.chinacloudapi.cn/',
#                                       credential='Jw9VThM4rkwnqG68FrahyzQzrlSsh++xCD/DyegvJMU+znMwgo+ogpSkUsCRSHtUTpatBgLgrSKG+AStgZdK8w==')
#
#     file_share = share_client.get_share_client(share_name)
#     directory = file_share.get_directory_client(file_path)
#     directory.create_subdirectory(directory_name='result',metadata={})
#
#

# with open('zeno_test.seq','w') as fpq:
#     with open('zeno_test (7).seq','rb') as fp:
#         content = fp.read()
#     fpq.write(str(content))


from azure.storage.fileshare import ShareServiceClient, ShareClient, ShareDirectoryClient, ShareFileClient
from azure.storage.fileshare._models import DirectoryProperties, FileProperties

service_client = ShareServiceClient(account_url='https://iptempfsxets000000.file.core.chinacloudapi.cn/',
                                    credential='Jw9VThM4rkwnqG68FrahyzQzrlSsh++xCD/DyegvJMU+znMwgo+ogpSkUsCRSHtUTpatBgLgrSKG+AStgZdK8w==')

shares = list(service_client.list_shares())


def delete_directory(share_client: ShareClient, directory_name: str):
    directory_client = share_client.get_directory_client(directory_name)
    resources = list(directory_client.list_directories_and_files())
    if len(resources) == 0:
        directory_client.delete_directory()
        return
    for resource in resources:
        if type(resource) == DirectoryProperties:
            delete_directory(share_client, directory_name + '/' + resource['name'])
            directory_client.delete_directory()
        if type(resource) == FileProperties:
            file_client = directory_client.get_file_client(file_name=resource['name'])
            file_client.delete_file()


def delete_resource(share_client: ShareClient):
    resources = list(share_client.list_directories_and_files())
    if len(resources) == 0:
        return
    for resource in resources:
        if type(resource) == DirectoryProperties:
            delete_directory(share_client, resource['name'])
        if type(resource) == FileProperties:
            share_file_client = share_client.get_file_client(resource['name'])
            share_file_client.delete_file()
            pass


for share in shares:
    share_client = service_client.get_share_client(share=share)
    delete_resource(share_client)

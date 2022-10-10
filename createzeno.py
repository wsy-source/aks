from kubernetes import client, config
from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.mgmt.containerservice import ContainerServiceClient
from azure.identity import AzureAuthorityHosts

JOB_NAME = "zeno"

# 已经创建pod的node列表
status_table = ["aks-agentpool-22697514-vmss000000"]

def get_aks_config() -> dict:
    credential = ClientSecretCredential(tenant_id='1a6857ff-9169-4a8a-83bf-5de6129d38f6',
                                        client_id='2adc7898-6cb4-4b5e-8231-6d6d5bbdd149',
                                        client_secret='18A_C30jGDJ7ulLb-y~O3X-25zA9ztNDEh',
                                        authority=AzureAuthorityHosts.AZURE_CHINA)
    secret_client = SecretClient('https://wsykeyvault2.vault.azure.cn/', credential=credential)
    secret = secret_client.get_secret('aks')
    config_dict = eval(secret.value)
    return config_dict


# node

def create_job_object(node_name):
    """
    创建Job对象
    :param node_name:
    :return:
    """
    azure_file = client.V1AzureFileVolumeSource(read_only=False, secret_name='azure-secret',
                                                share_name='fileshare-01')
    # 数据卷的挂载
    volumeMount = client.V1VolumeMount(mount_path='/mnt/input', name='azure', read_only=False,
                                       sub_path='Extraction/source2')
    volumeMount2 = client.V1VolumeMount(mount_path='/mnt/project', name='azure', read_only=False,
                                        sub_path='Extraction/extract_result/aazz')
    volume = client.V1Volume(name='azure', azure_file=azure_file)
    # 创建容器
    container = client.V1Container(
        name="zeno",
        image="acrinnorth2.azurecr.cn/ai-dataops/zeno:0.9.1",
        volume_mounts=[volumeMount, volumeMount2],
        command=["/bin/sh", "-c",
                 "zeno extract headless --ops_config_path /mnt/project/config_ops_user_modify.yml -c FC1 -l true -o /mnt/project"],
        working_dir='/mnt/project',
        image_pull_policy='IfNotPresent',
    )
    # 创建的模板配置
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "pi"}),
        spec=client.V1PodSpec(restart_policy="Never", containers=[container], volumes=[volume],
                              node_name=node_name))
    # 创建具体的job
    spec = client.V1JobSpec(
        template=template,
        backoff_limit=4)

    # job配置初始化
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=JOB_NAME),
        spec=spec)

    return job


def create_job(node_name: str):
    """
    根据节点名字创建pod
    :param node_name:
    :return:
    """
    print('开始创建job')
    job = create_job_object(node_name)
    api_instance = client.BatchV1Api()
    api_response = api_instance.create_namespaced_job(
        body=job,
        namespace="default")
    print("Job created. status='%s'" % str(api_response.status))


def scale_node(node_count: int):
    """
    缩放节点
    :return:
    """
    print('开始创建node')

    credential = ClientSecretCredential(tenant_id='1a6857ff-9169-4a8a-83bf-5de6129d38f6',
                                        client_id='2adc7898-6cb4-4b5e-8231-6d6d5bbdd149',
                                        client_secret='18A_C30jGDJ7ulLb-y~O3X-25zA9ztNDEh',
                                        authority=AzureAuthorityHosts.AZURE_CHINA)

    client = ContainerServiceClient(credential=credential, subscription_id='c45f94fd-0b5c-421e-b1e5-d5baec383b27',
                                    base_url='https://management.chinacloudapi.cn',
                                    credential_scopes=['https://management.chinacloudapi.cn/.default'])

    cluster = client.managed_clusters.get(resource_name='adasaks', resource_group_name='rg-wsy-aks')
    # cluster = ManagedCluster()
    for profile in cluster.agent_pool_profiles:
        if profile.name == 'agentpool':
            print(profile.count)
            profile.count = profile.count + node_count
    response = client.managed_clusters.begin_create_or_update(resource_name='adasaks', resource_group_name='rg-wsy-aks',
                                                              parameters=cluster)
    print(response.result())


def find_node_by_status() -> list:
    """
    通过节点状态获取空闲节点
    :return: 返回空闲节点名称列表
    """


def get_node_to_create_pod() -> str:
    """
    列出当前运行的节点，与列表已维护的创建pod的节点做差集，返回第一个节点名
    :return: 返回需要创建pod的节点名称
    """
    print('开始创建node')
    node_name = []
    mydict = client.CoreV1Api().list_node().to_dict()
    for item in mydict['items']:
        node_name.append(item['metadata']['name'])
    for node in node_name:
        if node not in status_table:
            status_table.append(node)
            return node


def delete_pod(pod_name: str, name_space: str):
    """
    删除指定namespace下的pod
    :param pod_name:
    :param name_space:
    :return:
    """
    client.CoreV1Api().delete_namespaced_pod(pod_name, name_space)


if __name__ == '__main__':
    # 从key_vault中加载aks配置文件
    config.load_kube_config_from_dict(get_aks_config())
    scale_node(1)
    pod_name = get_node_to_create_pod()
    create_job('aks-agentpool-22697514-vmss000000')

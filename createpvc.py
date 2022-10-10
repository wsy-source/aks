import logging

from kubernetes import config, client

config.load_config()


def create_persistent_volume_claim(access_modes: list, storage_class_name: str, volume_name: str,
                                   persistent_volume_name: str, capacity: str, **kwargs):
    limits = None
    namespace = 'default'
    if kwargs.__contains__('limits'):
        limits = kwargs.pop('limits')
        if type(limits) != dict:
            logging.error('limits required dict but' + str(type(limits)))
    if kwargs.__contains__('namespace'):
        namespace = kwargs.pop('namespace')
        if type(namespace) != dict:
            logging.error('limits required dict but' + str(type(namespace)))
    resources = client.V1ResourceRequirements(requests={'storage': capacity}, limits=namespace)
    volume_claim_spec = client.V1PersistentVolumeClaimSpec(access_modes=access_modes,
                                                           storage_class_name=storage_class_name,
                                                           volume_name=volume_name, resources=resources)
    claim = client.V1PersistentVolumeClaim(api_version='v1', kind='PersistentVolumeClaim',
                                           metadata={'name': persistent_volume_name}, spec=volume_claim_spec)
    client.CoreV1Api().create_namespaced_persistent_volume_claim(namespace=namespace, body=claim)


create_persistent_volume_claim(access_modes=['ReadWriteMany'], storage_class_name='azurefile-csi-premium',
                               volume_name='fileshare01', persistent_volume_name='fileshare01')

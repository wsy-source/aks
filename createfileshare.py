import os

from azure.storage.fileshare import ShareClient, ShareDirectoryClient, ShareServiceClient
from azure.identity import ClientSecretCredential, AzureAuthorityHosts

credential = ClientSecretCredential(tenant_id='1a6857ff-9169-4a8a-83bf-5de6129d38f6',
                                    client_id='2adc7898-6cb4-4b5e-8231-6d6d5bbdd149',
                                    client_secret='18A_C30jGDJ7ulLb-y~O3X-25zA9ztNDEh',
                                    authority=AzureAuthorityHosts.AZURE_CHINA)

client = ShareServiceClient(account_url='https://testaksinjection.file.core.chinacloudapi.cn/',
                            share_name='testaksinjection',
                            credential='VQHXJ9KZIoH+X9MQjh0DlyY8XCZsgo5XXOXG27nTioxXXu2esrtun5HAgEmFW8BvHbXvyVA9PHUT+AStC4LDVg==')
for i in range(10, 51):
    # client.delete_share(share_name='fileshare-0' + str(i))
    popen = os.popen(
        'azcopy cp "https://seanextractionfile.file.core.chinacloudapi.cn/fileshare-01/Extraction/extract_result/?sv=2021-06-08&ss=f&srt=sco&sp=rwdlc&se=2022-10-10T11:48:46Z&st=2022-10-10T03:48:46Z&spr=https&sig=aIw5uFBU7CDhcRlbR0kgzZWLsis0T18K5F3FlmwQe%2FE%3D" "https://testaksinjection.file.core.chinacloudapi.cn/fileshare-' + str(
            i) + '/?sv=2021-06-08&ss=f&srt=sco&sp=rwdlc&se=2022-10-10T11:53:19Z&st=2022-10-10T03:53:19Z&spr=https&sig=KtbDKTGsc%2Flv15svJTcRL4qNPR6Pg15r2F3HprImaUs%3D" --recursive')
    print(popen.read())
    print('fileshare-' + str(i))

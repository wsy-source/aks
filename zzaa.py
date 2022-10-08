import json
import logging

import yaml

# name = None
#
#
# def check(name: str, time: str, status: str) -> str:
#     if name and time and status:
#         return "success"
#     else:
#         if not name:
#             return 'name'
#         if not status:
#             return 'status'
#         if not time:
#             return 'time'
#
#
# info = check('', '', '')
#
# if info == 'success':
#     print('************')
# else:
#     print(info)

with open('config','rb') as fp:
    print(yaml.load(fp.read(), yaml.Loader))
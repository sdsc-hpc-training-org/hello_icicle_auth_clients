import os
from tapipy.tapis import Tapis
import json
import datetime
import logging
import typing

import pydantic

from utilities.logger import ServiceLogger


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(f"{__file__}")))
ROOT_USER_FILE_PATH = os.path.join(__location__, r'user_files')


class ServiceConfigFile(pydantic.BaseModel):
    version: int
    configuration: dict
    

class User:
    def __init__(self, parent_path, username):
        self.root_path = f"{parent_path}\\{username}"
        self.user_info_path = f"{self.root_path}\\{username}_info.json"
        self.cache_path = f"{self.root_path}\\cache.json"
        self.tenants_path = f"{self.root_path}\\tenants"

    def write_user_info(self, user):
        with open(f"{self.user_info_path}", 'w') as f:
            json.dump(user, f)

    def handle_user_cache(self, cache_data: list, mode: typing.Literal['READ', 'WRITE']):
        if os.path.getsize(self.cache_path) != 0:
            with open(self.cache_path, 'r') as f:
                json_data = json.load(f)
                if mode == 'READ':
                    return json_data
        else:
            json_data = []
        with open(self.cache_path, 'w') as f:
            json_data += cache_data
            json.dump(f, json_data)
        return 'cache successfully written'
    

class Tenant(ServiceLogger):
    def __init__(self, parent_path, tenant_id):
        super().__init__('Tenant Logger', '/')
        self.root_path = f"{parent_path}\\{tenant_id}"
        self.tenant_info_path = f"{self.root_path}\\{tenant_id}_info.json"
        self.service_type = None

    def set_service_type(self, service):
        self.service_type = service
    
    def write_tenant_info(self, tenant_info):
        with open(self.tenant_info_path, 'w') as f:
            json.dump(tenant_info, f)
            
    def write_service_information(self, service_instance_id, information):
        with open(f"{self.root_path}\\{self.service_type}\\{service_instance_id}\\{service_instance_id}_info.json", 'w') as f:
            json.dump(information, f)
            
    def service_log(self, service_instance_id, information, level):
        current_date = datetime.now()
        formatted_date = current_date.strftime('%m_%d_%y')
        self.log(information, level, filename=f"{self.root_path}\\{self.service_type}\\{service_instance_id}\\logs\\{service_instance_id}_{formatted_date}.log")

    def get_config_files(self, service_instance_id):
        configs_path = f"{self.root_path}\\{self.service_type}\\{service_instance_id}\\configs"
        config_list = os.listdir(f"{configs_path}")
        return config_list

    def handle_config_file(self, service_instance_id, config: ServiceConfigFile, mode: typing.Literal['READ', 'WRITE'], select_file: str = None):
        configs_path = f"{self.root_path}\\{self.service_type}\\{service_instance_id}\\configs"
        config_list = self.get_config_files(service_instance_id)
        if config_list:
            config_file = f"{configs_path}\\{config_list[-1]}"
            if select_file:
                config_file = select_file
            with open(config_file, 'r') as f:
                previous_config = json.load(f)
                if mode == 'READ':
                    return previous_config
                new_version = previous_config['version'] + 1
        else:
            new_version = 1
        config_file_path = f"{configs_path}\\{service_instance_id}_v{new_version}"
        with open(config_file_path, 'w') as f:
            json.dump(config.json(), f)
        return f"Config file written to {config_file_path}"
    
            
class FileManager:
    user: User = None
    tenant: Tenant = None
    root_path = ROOT_USER_FILE_PATH

    def set_information(self, user, tenant):
        self.user = User(self.root_path, username=user)
        self.tenant = Tenant(self.root_path, tenant_id=tenant)

    


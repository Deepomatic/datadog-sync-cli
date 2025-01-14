# Unless explicitly stated otherwise all files in this repository are licensed
# under the 3-clause BSD style license (see LICENSE).
# This product includes software developed at Datadog (https://www.datadoghq.com/).
# Copyright 2019 Datadog, Inc.

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Dict, cast

from datadog_sync.utils.base_resource import BaseResource, ResourceConfig

if TYPE_CHECKING:
    from datadog_sync.utils.custom_client import CustomClient


class HostTags(BaseResource):
    resource_type = "host_tags"
    resource_config = ResourceConfig(
        base_path="/api/v1/tags/hosts",
    )
    # Additional HostTags specific attributes

    def get_resources(self, client: CustomClient) -> List[Dict]:
        resp = client.get(self.resource_config.base_path).json()

        return list(resp["tags"].items())

    def import_resource(self, _id: Optional[str] = None, resource: Optional[Dict] = None) -> None:
        if _id:
            return  # This should never occur. No resource depends on it.

        resource = cast(dict, resource)
        tag = resource[0]
        hosts = resource[1]
        for host in hosts:
            if host not in self.resource_config.source_resources:
                self.resource_config.source_resources[host] = []
            self.resource_config.source_resources[host].append(tag)

    def pre_resource_action_hook(self, _id, resource: Dict) -> None:
        pass

    def pre_apply_hook(self) -> None:
        pass

    def create_resource(self, _id: str, resource: Dict) -> None:
        self.update_resource(_id, resource)

    def update_resource(self, _id: str, resource: Dict) -> None:
        destination_client = self.config.destination_client
        body = {"tags": resource}
        resp = destination_client.put(self.resource_config.base_path + f"/{_id}", body).json()

        self.resource_config.destination_resources[_id] = resp["tags"]

    def delete_resource(self, _id: str) -> None:
        destination_client = self.config.destination_client
        destination_client.delete(self.resource_config.base_path + f"/{_id}")

    def connect_id(self, key: str, r_obj: Dict, resource_to_connect: str) -> Optional[List[str]]:
        pass

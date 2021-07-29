# Unless explicitly stated otherwise all files in this repository are licensed
# under the 3-clause BSD style license (see LICENSE).
# This product includes software developed at Datadog (https://www.datadoghq.com/).
# Copyright 2019 Datadog, Inc.
from typing import Optional

from requests.exceptions import HTTPError

from datadog_sync.utils.base_resource import BaseResource, ResourceConfig


class SLOCorrections(BaseResource):
    resource_type = "slo_corrections"
    resource_config = ResourceConfig(
        resource_connections={"service_level_objectives": ["attributes.slo_id"]},
        base_path="/api/v1/slo/correction",
        excluded_attributes=["root['id']", "root['attributes']['creator']"],
    )
    # Additional SLOCorrections specific attributes

    def get_resources(self, client) -> list:
        try:
            resp = client.get(self.resource_config.base_path).json()
        except HTTPError as e:
            self.config.logger.error("error importing slo_correction %s", e)
            return []

        return resp["data"]

    def import_resource(self, resource) -> None:
        self.resource_config.source_resources[resource["id"]] = resource

    def pre_resource_action_hook(self, resource) -> None:
        pass

    def pre_apply_hook(self, resources) -> Optional[list]:
        pass

    def create_resource(self, _id, resource) -> None:
        destination_client = self.config.destination_client

        payload = {"data": resource}
        try:
            resp = destination_client.post(self.resource_config.base_path, payload).json()
        except HTTPError as e:
            self.config.logger.error("error creating slo_correction: %s", e.response.text)
            return

        self.resource_config.destination_resources[_id] = resp["data"]

    def update_resource(self, _id, resource) -> None:
        destination_client = self.config.destination_client

        payload = {"data": resource}
        try:
            resp = destination_client.patch(
                self.resource_config.base_path + f"/{self.resource_config.destination_resources[_id]['id']}", payload
            ).json()
        except HTTPError as e:
            self.config.logger.error("error updating slo_correction: %s", e.response.text)
            return
        self.resource_config.destination_resources[_id] = resp["data"]

    def connect_id(self, key, r_obj, resource_to_connect) -> None:
        super(SLOCorrections, self).connect_id(key, r_obj, resource_to_connect)

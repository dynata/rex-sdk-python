"""
Package: src.smor
Filename: api.py
Author(s): Grant W

Description: API interaction for smor
"""
# Python Imports
import json
from typing import List, Union
import os

# Third Party Imports
import pydantic

# Local Imports
import dynata_rex.models as models
from .signer import RexRequest
from .logs import logger
from .exceptions import InvalidShardException


class RegistryAPI:

    def __init__(self,
                 access_key: str,
                 secret_key: str,
                 base_url: str,
                 shard_count: int = 1,
                 current_shard: int = 1,
                 signature_ttl: Union[int, None] = None):
        """
        @access_key: liam access key for REX
        @secret_key: liam secret key for REX
        @base_url  : url of Opportunity Registry

        # Optional
        @shard_count  : number of total shards consuming Opportunity Registry
        @current_shard: curent shard
        """
        if signature_ttl is None:
            signature_ttl = int(os.environ.get('REX_SIGNATURE_TTL', '10'))
        self.signature_ttl = signature_ttl
        self.make_request = RexRequest(access_key,
                                       secret_key,
                                       ttl=signature_ttl)
        self.base_url = self._format_base_url(base_url)

        if current_shard > shard_count:
            raise InvalidShardException
        self.shard_count = shard_count
        self.current_shard = current_shard

    def _format_base_url(self, base_url: str) -> str:
        if base_url.startswith('http'):
            return base_url
        return f'https://{base_url}'

    def _get_opportunity(self, opportunity_id: int) -> dict:
        """Raw get opportunity"""
        endpoint = f"{self.base_url}/get-opportunity"
        data = {"id": opportunity_id}
        return self.make_request.post(endpoint, data)

    def _list_opportunities(self, limit: int = 10) -> List[dict]:
        """Raw get opportunities"""
        endpoint = f"{self.base_url}/list-opportunities"
        data = {
            "limit": limit,
            "shards": {
                "count": self.shard_count,
                "current": self.current_shard
            }
        }
        return self.make_request.post(endpoint, data)

    def list_opportunities(self, limit: int = 10) -> List[models.Opportunity]:
        """Get opportunities from Opportunity Registry
        """
        opportunities = self._list_opportunities(limit=limit)
        out = []
        for opp in opportunities:
            try:
                out.append(models.Opportunity(**opp))
            except pydantic.error_wrappers.ValidationError:
                opportunity_id = opp['id']
                logger.warning(
                    f"Unable to parse {opportunity_id}, excluding...")
                logger.warning(json.dumps(opp, indent=4))
                # Ack opportunity so we don't see it again
                self.ack_opportunity(opportunity_id)

        return out

    def get_opportunity(self, opportunity_id: int) -> models.Opportunity:
        """Get specific opportunity from SMOR
        """
        opportunity = self._get_opportunity(opportunity_id)
        return models.Opportunity(**opportunity)

    def list_project_opportunities(self, project_id: int) -> List[int]:
        endpoint = f"{self.base_url}/list-project-opportunities"
        data = {"project_id": project_id}
        return self.make_request.post(endpoint, data)

    def ack_opportunity(self, opportunity_id: int) -> None:
        """Acknowledge a single oppportunity
        """
        data = [opportunity_id]
        return self.ack_opportunities(data)

    def ack_opportunities(self, opportunities: List[int]) -> None:
        """Acknowledge a list of oppportunities
        """
        endpoint = f"{self.base_url}/ack-opportunities"
        res = self.make_request.post(endpoint, opportunities)
        return res

    def download_collection(self, collection_id: int) -> list:
        endpoint = f"{self.base_url}/download-collection"
        data = {"id": collection_id}
        return self.make_request.post(endpoint, data)

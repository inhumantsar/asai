"""Main module."""

import json
import logging
import re
from typing import Dict, Generator, List, Tuple, Union

import requests
from fuzzywuzzy import fuzz

from asai.models import AWSService

log = logging.getLogger()

_POLICIES_URL = "https://awspolicygen.s3.amazonaws.com/js/policies.js"
# policies.js sets one big var, trim that var def and we have valid JSON
_POLICIES_PREFIX = "app.PolicyEditorConfig="


def get_policies() -> Dict:
    """Download all possible IAM actions, conditions, etc."""
    resp = requests.get(_POLICIES_URL)
    if resp.status_code != 200:
        log.error(f"Bad response from {_POLICIES_URL}")
        return

    resp_json = resp.content[len(_POLICIES_PREFIX) :]
    return json.loads(resp_json)


def get_service_by_prefix(
    prefix: str, service_list: List[AWSService] = None
) -> Union[AWSService, None]:
    """Find a single service by its StringPrefix. Returns None if no matches are found."""
    services = service_list or get_services()
    try:
        return next(s for s in services if s.StringPrefix == prefix)
    except StopIteration as e:
        return


def get_global_services(service_list: List[AWSService] = None) -> List[AWSService]:
    """List all services which aren't tied to specific regions."""
    services = service_list or get_services()
    return [s for s in services if not s.is_regional]


def get_regional_services(service_list: List[AWSService] = None) -> List[AWSService]:
    """List all services which are tied to specific regions."""
    services = service_list or get_services()
    return [s for s in services if s.is_regional]


def get_services() -> List[AWSService]:
    """Parse out all services from policies."""
    service_map = get_policies()["serviceMap"]
    return [AWSService(name=k, **v) for k, v in service_map.items()]


def get_actions() -> Dict[str, List[str]]:
    """Parse out all service prefixes and actions from policies."""
    services = get_services()
    return {v.StringPrefix: v.Actions for _, v in services.items()}


def search_services(
    search_term: str, min_confidence=70, service_list: List[AWSService] = None
) -> Generator[Tuple[int, AWSService], None, None]:
    """Use fuzzy matching to search the list of service names and prefixes."""
    services = service_list or get_services()
    search_term = search_term.lower()
    for service in get_services():
        name_words = service.name.lower().split()
        name_score = max([fuzz.ratio(i, search_term) for i in name_words])
        prefix_score = fuzz.ratio(service.StringPrefix, search_term)
        score = max(name_score, prefix_score)
        if score > min_confidence:
            yield (score, service)

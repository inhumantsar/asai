"""Main module."""

import json
import logging
import re
from typing import Dict, Generator, List, Tuple, Union

import requests
from fuzzywuzzy import fuzz

from asai import AWSService

log = logging.getLogger()

_POLICIES_URL = "https://awspolicygen.s3.amazonaws.com/js/policies.js"
# policies.js sets one big var, trim that var def and we have valid JSON
_POLICIES_PREFIX = "app.PolicyEditorConfig="
_CAMEL_REGEX = re.compile(r".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)")


def get_policies() -> Dict:
    """Download all possible IAM actions, conditions, etc."""
    resp = requests.get(_POLICIES_URL)
    if resp.status_code != 200:
        log.error(f"Bad response from {_POLICIES_URL}")
        return

    resp_json = resp.content[len(_POLICIES_PREFIX) :]
    return json.loads(resp_json)


def get_service_by_prefix(prefix: str) -> Union[AWSService, None]:
    """Find a single service by its StringPrefix. Returns None if no matches are found."""
    try:
        return next(s for s in get_services() if s.StringPrefix == prefix)
    except StopIteration as e:
        return


def get_services() -> List[AWSService]:
    """Parse out all services from policies."""
    service_map = get_policies()["serviceMap"]
    return [AWSService(name=k, **v) for k, v in service_map.items()]


def get_actions() -> Dict[str, List[str]]:
    """Parse out all service prefixes and actions from policies."""
    services = get_services()
    return {v.StringPrefix: v.Actions for _, v in services.items()}


def get_actions_with_wildcards(service: AWSService) -> List[str]:
    """Return a service's list of actions, wildcarding any common prefixes."""
    actions = []
    for action in service.Actions:
        prefix = _get_action_prefix(action)
        wildcard = f"{prefix}*"
        if wildcard in actions:
            continue

        if _count_prefix_occurances(prefix, service.Actions) > 1:
            actions.append(wildcard)
        else:
            actions.append(action)
    return sorted(actions)


def search_services(
    search_term: str, min_confidence=70
) -> Generator[Tuple[int, AWSService], None, None]:
    """Use fuzzy matching to search the list of service names and prefixes."""
    search_term = search_term.lower()
    for service in get_services():
        name_words = service.name.lower().split()
        name_score = max([fuzz.ratio(i, search_term) for i in name_words])
        prefix_score = fuzz.ratio(service.StringPrefix, search_term)
        score = max(name_score, prefix_score)
        if score > min_confidence:
            yield (score, service)


def service_is_regional(svc: AWSService) -> bool:
    """Return true if a region field is present in the service's ARN format."""
    # region field can appear as ${region}, <region>, or region, in either title or lower case
    return "region" in svc.ARNFormat.lower()


def _get_action_prefix(action: str) -> str:
    """Split action by CamelCase, return prefix."""
    matches = re.findall(_CAMEL_REGEX, action)
    return matches[0]  # .group(0)


def _count_prefix_occurances(prefix: str, actions: List[str]) -> int:
    """Get the number of times a prefix occurs within a list of strings."""
    return len([i for i, x in enumerate(actions) if x.startswith(prefix)])

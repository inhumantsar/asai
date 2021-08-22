"""ASAI can find the available actions, conditions, and other useful IAM information for AWS services.

This was written to make building detailed IAM policies with regional permissions boundaries less tedious.

## Features

* Search or list all AWS services
* List all regional or global AWS services
* Create a list of available IAM actions, wildcarding common prefixes
* Display all available IAM actions for a service
* Print all IAM information for a service.
"""

from dataclasses import dataclass, field
from typing import List

__author__ = """Shaun Martin"""
__email__ = "inhumantsar@protonmail.com"
__version__ = "0.1.3"


@dataclass(order=True)
class AWSService:
    """Representation of service information as received from policies.js."""

    name: str
    # matching JSON keys for the rest because i'm lazy
    StringPrefix: str
    Actions: List[str]
    HasResource: bool
    ARNFormat: str = field(default="")
    ARNRegex: str = field(default="")
    conditionKeys: List[str] = field(default_factory=lambda: [])


from ._backend import (
    get_actions,
    get_actions_with_wildcards,
    get_policies,
    get_service_by_prefix,
    get_services,
    search_services,
    service_is_regional,
)

__all__ = [
    "AWSService",
    "get_actions",
    "get_policies",
    "get_service_by_prefix",
    "get_services",
    "get_actions_with_wildcards",
    "search_services",
    "service_is_regional",
]

"""ASAI can find the available actions, conditions, and other useful IAM information for AWS services.

This was written to make building detailed IAM policies with regional permissions boundaries less tedious.

## Features

* Search or list all AWS services
* List all regional or global AWS services
* Create a list of available IAM actions, wildcarding common prefixes
* Display all available IAM actions for a service
* Print all IAM information for a service.
"""
__author__ = """Shaun Martin"""
__email__ = "inhumantsar@protonmail.com"
__version__ = "0.2.0"

import models

from ._backend import (
    get_actions,
    get_global_services,
    get_policies,
    get_regional_services,
    get_service_by_prefix,
    get_services,
    search_services,
)

__all__ = [
    "models",
    "get_actions",
    "get_policies",
    "get_service_by_prefix",
    "get_services",
    "get_global_services",
    "get_regional_services",
    "search_services",
]

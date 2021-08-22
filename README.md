# AWS Service Authorization Information (ASAI) v0.1.3

[![PyPI](https://img.shields.io/pypi/v/asai.svg)](https://pypi.python.org/pypi/asai)

ASAI can find the available actions, conditions, and other useful IAM information for AWS services.

This was written to make building detailed IAM policies with regional permissions boundaries less tedious.

## Features

* Search or list all AWS services
* List all regional or global AWS services
* Create a list of available IAM actions, wildcarding common prefixes
* Display all available IAM actions for a service
* Print all IAM information for a service.

## Usage

### Multiple Services

List or search for services by attribute.

    $ asai services <command>

Available commands:

* `all`       List all service prefixes.
* `global`    List all services which aren't tied to specific regions.
* `no-arn`    List all services which don't have an ARN format.
* `regional`  List all services which are tied to specific regions.
* `search`    Search for a service by name or prefix.

### Individual Services

Get information on a single service.

    $ asai service <command>

Available commands:

* `actions`           List a service's actions.
* `actions-wildcard`  List a service's actions, wildcarding common prefixes.
* `arn-format`        Display a service's ARN format description.
* `arn-regex`         Display a service's ARN Regex string.
* `info`              Print all available service information.

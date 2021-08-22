"""Console script for asai."""
import sys
from typing import List

import click

import asai


@click.group()
def cli():
    """ASAI can find the available actions, conditions, and other useful IAM information for AWS services."""
    pass


@cli.group("services")
def aws_services():
    """List or search for services by attribute."""
    pass


@aws_services.command("all")
def all_services():
    """List all service prefixes."""
    _echo_service_prefixes(asai.get_services())


@aws_services.command()
def no_arn():
    """List all services which don't have an ARN format."""
    services = asai.get_services()
    _echo_service_prefixes([s for s in services if not s.ARNFormat])


@aws_services.command("global")
def global_services():
    """List all services which aren't tied to specific regions."""
    services = asai.get_services()
    _echo_service_prefixes([s for s in services if not asai.service_is_regional(s)])


@aws_services.command()
def regional():
    """List all services which are tied to specific regions."""
    services = asai.get_services()
    _echo_service_prefixes([s for s in services if asai.service_is_regional(s)])


@aws_services.command()
@click.argument("search_term")
def search(search_term: str):
    """Search for a service by name or prefix."""
    results = asai.search_services(search_term)
    for _, svc in sorted(results, reverse=True, key=lambda x: x[0]):
        click.echo(f"{svc.name} ({svc.StringPrefix})")


@cli.group()
def service():
    """Get information on a single service."""
    pass


@service.command()
@click.argument("prefix")
def arn_format(prefix: str):
    """Display a service's ARN format description.

    PREFIX is a service's short name. eg: ec2, ssm, or s3.
    """
    service = _get_service_by_prefix(prefix)
    click.echo(service.ARNFormat)


@service.command()
@click.argument("prefix")
def arn_regex(prefix: str):
    """Display a service's ARN Regex string.

    PREFIX is a service's short name. eg: ec2, ssm, or s3.
    """
    service = _get_service_by_prefix(prefix)
    click.echo(service.ARNRegex)


@service.command()
@click.argument("prefix")
def actions(prefix: str):
    """List a service's actions.

    PREFIX is a service's short name. eg: ec2, ssm, or s3.
    """
    service = _get_service_by_prefix(prefix)
    for action in sorted(service.Actions):
        click.echo(action)


@service.command()
@click.argument("prefix")
def actions_wildcard(prefix: str):  # noqa: D301
    """List a service's actions, wildcarding common prefixes.

    \b
        $ asai service actions-wildcard s3
        AbortMultipartUpload
        BypassGovernanceRetention
        Create*
        Delete*
        DescribeJob
        Get*
        List*
        ObjectOwnerOverrideToBucketOwner
        Put*
        Replicate*
        RestoreObject
        Update*

    PREFIX is a service's short name. eg: ec2, ssm, or s3.
    """
    service = _get_service_by_prefix(prefix)
    for action in asai.get_actions_with_wildcards(service):
        click.echo(action)


@service.command()
@click.argument("prefix")
def info(prefix: str):
    """Print all available service information.

    PREFIX is a service's short name. eg: ec2, ssm, or s3.
    """
    service = _get_service_by_prefix(prefix)

    click.echo(f"{service.name} ({service.StringPrefix})\n")
    click.echo(f"Has Resource: {service.HasResource}")
    click.echo("\nActions:")
    for action in sorted(service.Actions):
        click.echo(f"  - {action}")
    click.echo(f"\nARN Format: {service.ARNFormat}")
    click.echo(f"ARN Regex: {service.ARNRegex}")
    click.echo("\nCondition Keys:")
    for condition_key in service.conditionKeys:
        click.echo(f"  - {condition_key}")


def _echo_service_prefixes(services: List[asai.AWSService]):
    svc_ids = sorted(set([s.StringPrefix for s in services]))
    for svc in svc_ids:
        click.echo(svc)


def _get_service_by_prefix(prefix: str) -> asai.AWSService:
    service = asai.get_service_by_prefix(prefix)
    if not service:
        click.echo(f"{prefix} was not found in the service list.", err=True)
        sys.exit(1)
    return service


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover

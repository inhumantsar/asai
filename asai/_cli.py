"""Console script for asai."""
import sys
from pprint import pprint
from types import FunctionType
from typing import List

import click

import asai
from asai.models import AWSPolicy, AWSPolicyStatement, AWSService


@click.group()
def cli():
    """ASAI can find the available actions, conditions, and other useful IAM information for AWS services."""
    pass


@cli.command("policy")
@click.option(
    "-p",
    "--prefix",
    multiple=True,
    default=[],
    help="Specific service prefix. Can be used multiple times.",
)
@click.option(
    "--all-global",
    is_flag=True,
    help="Include all global services in policy scaffold.",
)
@click.option(
    "--all-regional",
    is_flag=True,
    help="Include all global services in policy scaffold.",
)
@click.option(
    "-s",
    "--search",
    multiple=True,
    default=[],
    help="Include all search results. Can be used multiple times.",
)
@click.option(
    "--wildcard",
    is_flag=True,
    help="Wildcard the actions list of all specified services.",
)
@click.option(
    "--group",
    is_flag=True,
    help="Group services by parameter.",
)
def policy(
    prefix: List[str],
    all_global: bool,
    all_regional: bool,
    search: List[str],
    wildcard: bool,
    group: bool,
):
    """
    Generate an IAM policy scaffold using specified services.

    When multiple service options are specified, they will be combined into a
    single policy.

    If `--group` is set, then the policy will contain multiple statements for each
    parameter. eg: Setting `--prefix ssm --prefix ec2 --all-global --search
    container` will result in four statements, one for SSM, one for EC2, one for
    all global services, and one for "container" search results. These will
    *not* be de-duped.

    If no service options are specified, a policy scaffold with all services
    will be created. Using `--group` here will result in each service getting its own
    policy statement.
    """
    all_services = asai.get_services()
    services = []
    add_to_services: FunctionType = services.append if group else services.extend

    for p in prefix:
        add_to_services([asai.get_service_by_prefix(p, service_list=all_services)])
    if all_global:
        add_to_services(asai.get_global_services(service_list=all_services))
    if all_regional:
        add_to_services(asai.get_regional_services(service_list=all_services))
    for s in search:
        add_to_services(
            [i[1] for i in asai.search_services(s, service_list=all_services)]
        )

    if not services:
        services = [[s] for s in all_services] if group else all_services

    if group:
        statements = [AWSPolicyStatement.from_services(s, wildcard) for s in services]
        click.echo(AWSPolicy(statements).json)
    else:
        click.echo(AWSPolicy.from_services(services, wildcard).json)


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
    _echo_service_prefixes(asai.get_global_services())


@aws_services.command()
def regional():
    """List all services which are tied to specific regions."""
    _echo_service_prefixes(asai.get_regional_services())


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
    for action in service.action_wildcards:
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


def _echo_service_prefixes(services: List[AWSService]):
    svc_ids = sorted(set([s.StringPrefix for s in services]))
    for svc in svc_ids:
        click.echo(svc)


def _get_service_by_prefix(prefix: str) -> AWSService:
    service = asai.get_service_by_prefix(prefix)
    if not service:
        click.echo(f"{prefix} was not found in the service list.", err=True)
        sys.exit(1)
    return service


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover

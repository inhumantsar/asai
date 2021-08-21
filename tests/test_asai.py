#!/usr/bin/env python

"""Tests for `asai` package."""

import pytest

from click.testing import CliRunner
from pathlib import Path
from os.path import join, dirname

from asai import _cli as cli


def _read(fname):
    """Read content of a file and return as a string."""
    return Path(join(dirname(__file__), fname)).read_text()


def test_cli_root():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.cli)
    assert result.exit_code == 0
    help_result = runner.invoke(cli.cli, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output


def test_cli_services_list():
    types = ["all", "global", "no-arn", "regional"]
    expected = {i: _read(i) for i in types}
    runner = CliRunner()
    result = runner.invoke(cli.cli, args=["services"])
    assert result.exit_code == 0
    assert all([i in result.output for i in list(expected.keys())])
    for cmd, services in expected.items():
        result = runner.invoke(cli.cli, args=["services", cmd])
        assert result.exit_code == 0
        assert all([i in result.output for i in services])


def test_cli_services_search():
    runner = CliRunner()
    searches = {
        "auto": [
            "AWS Auto Scaling (autoscaling-plans)",
            "Amazon EC2 Auto Scaling (autoscaling)",
            "Application Auto Scaling (application-autoscaling)",
        ],
        "ec": [
            "Amazon EC2 Auto Scaling (autoscaling)",
            "Amazon EC2 (ec2)",
            "Amazon EC2 Instance Connect (ec2-instance-connect)",
            "Amazon Elastic Container Service (ecs)",
            "Amazon Elastic Container Registry (ecr)",
            "Amazon EC2 Image Builder (imagebuilder)",
        ],
        "container": [
            "Amazon Elastic Container Registry Public (ecr-public)",
            "Amazon Elastic Container Service (ecs)",
            "Amazon Elastic Container Registry (ecr)",
            "Amazon EMR on EKS (EMR Containers) (emr-containers)",
        ],
    }
    for term, results in searches.items():
        result = runner.invoke(cli.cli, args=["services", "search", term])
        assert result.exit_code == 0
        assert all([i in result.output for i in results])


def test_cli_single_service():
    types = ["actions", "actions-wildcard", "arn-format", "arn-regex", "info"]
    services = ["ec2", "s3", "dynamodb"]
    expected = {f"{i}_{j}": _read(f"{i}-{j}") for i in types for j in services}
    runner = CliRunner()
    result = runner.invoke(cli.cli, args=["service"])
    assert result.exit_code == 0
    assert all([i in result.output for i in types])
    for cmd, expected_results in expected.items():
        print(["service", *cmd.split("-")])
        result = runner.invoke(cli.cli, args=["service", *cmd.split("_")])
        assert result.exit_code == 0
        assert all([i in result.output for i in expected_results])

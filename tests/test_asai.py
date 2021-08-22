#!/usr/bin/env python

"""Tests for `asai` package."""
import json
from os.path import dirname, join
from pathlib import Path
from typing import List, Tuple

from click.testing import CliRunner

from asai import _cli as cli


def _read(fname):
    """Read content of a file and return as a string."""
    return Path(join(dirname(__file__), "expected", fname)).read_text()


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
    expected = {i: _read(f"services-{i}") for i in types}
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
    expected = {f"{i}_{j}": _read(f"service-{i}-{j}") for i in types for j in services}
    runner = CliRunner()
    result = runner.invoke(cli.cli, args=["service"])
    assert result.exit_code == 0
    assert all([i in result.output for i in types])
    for cmd, expected_results in expected.items():
        print(["service", *cmd.split("-")])
        result = runner.invoke(cli.cli, args=["service", *cmd.split("_")])
        assert result.exit_code == 0
        assert all([i in result.output for i in expected_results])


def test_cli_policy():
    runner = CliRunner()
    params = [
        "-p",
        "--prefix",
        "--all-global",
        "--all-regional",
        "-s",
        "--search",
        "--wildcard",
        "--group",
    ]
    result = runner.invoke(cli.cli, args=["policy", "--help"])
    assert result.exit_code == 0
    assert all([i in result.output for i in params])
    commands: List[Tuple[str, str]] = [
        ("all", ""),
        ("all-group", "--group"),
        ("prefixes", "-p ec2 -p ecs"),
        ("prefixes-dedupe", "-p sqs -p sqs"),
        ("prefixes-group", "-p ec2 -p ecs --group"),
        ("searches", "-s container -s access"),
        ("searches-group", "-s container -s access --group"),
        ("searches-prefixes-group", "-s container -s access -p ecs -p sqs --group"),
    ]
    expected = {i[0]: json.loads(_read(f"policy-{i[0]}")) for i in commands}
    for (k, cmd) in commands:
        args = ["policy", *cmd.split()]
        print(args)
        result = runner.invoke(cli.cli, args=args)
        output = json.loads(result.output)
        assert expected[k]["Version"] == output["Version"]
        estatements = expected[k]["Statement"]
        for statement in output["Statement"]:
            assert any([statement["Action"] == e["Action"] for e in estatements])
            if "Resource" in statement.keys():
                assert any(
                    [
                        statement["Resource"] == e["Resource"]
                        for e in estatements
                        if "Resource" in e.keys()
                    ]
                )
            if "Condition" in statement.keys():
                econs = [e["Condition"] for e in estatements if "Condition" in e.keys()]
                out_keys = [
                    list(v.keys())[0] for _, v in statement["Condition"].items()
                ]
                assert any(
                    [
                        sorted(out_keys)
                        == sorted([list(v.keys())[0] for _, v in e.items()])
                        for e in econs
                    ]
                )

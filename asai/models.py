"""JSON-friendly models representing AWS resources."""

import json
import random
import re
import string
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Union


def _randomness():
    return "".join(random.sample(string.ascii_letters, 5))


@dataclass(order=True)
class AWSService:
    """Service information as received from policies.js."""

    name: str
    # matching JSON keys for the rest because i'm lazy
    StringPrefix: str
    Actions: List[str]
    HasResource: bool
    ARNFormat: str = field(default="")
    ARNRegex: str = field(default="")
    conditionKeys: List[str] = field(default_factory=lambda: [])

    _CAMEL_REGEX = re.compile(r".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)")

    @property
    def is_regional(self) -> bool:
        """Return true if a region field is present in the service's ARN format."""
        # region field can appear as ${region}, <region>, or region, in either title or lower case
        return "region" in self.ARNFormat.lower()

    @property
    def action_wildcards(self) -> List[str]:
        """Return service actions, wildcarding common prefixes."""
        actions = []
        for action in self.Actions:
            prefix = AWSService._get_action_prefix(action)
            wildcard = f"{prefix}*"
            if wildcard in actions:
                continue

            if AWSService._count_prefix_occurances(prefix, self.Actions) > 1:
                actions.append(wildcard)
            else:
                actions.append(action)
        return sorted(actions)

    def _get_action_prefix(action: str) -> str:
        """Split action by CamelCase, return prefix."""
        matches = re.findall(AWSService._CAMEL_REGEX, action)
        return matches[0]  # .group(0)

    def _count_prefix_occurances(prefix: str, actions: List[str]) -> int:
        """Get the number of times a prefix occurs within a list of strings."""
        return len([i for i, x in enumerate(actions) if x.startswith(prefix)])


@dataclass()
class AWSPolicyStatement:
    """Representation of an IAM policy statement."""

    Sid: str
    Action: List[str]
    Resource: Union[List[str], str]
    Condition: Dict[str, Dict[str, str]]

    def from_services(services: List[AWSService], wildcard=False):
        """Create object using service information, optionally wildcarding actions."""
        sid = f"Sid-{_randomness()}" if len(services) > 1 else services[0].name
        actions, resources = [], []
        conditions_list = []
        for s in services:
            for a in s.action_wildcards if wildcard else s.Actions:
                actions.append(f"{s.StringPrefix}:{a}")
            if s.HasResource:
                resources.append(s.ARNFormat)
            for i in s.conditionKeys:
                if i not in conditions_list:
                    conditions_list.append(i)

        return AWSPolicyStatement(
            Sid=sid,
            Action=sorted(set(actions)),
            Resource=sorted(set(resources)),
            Condition={
                f"SomeCondition-{_randomness()}": {i: "...some value..."}
                for i in sorted(set(conditions_list))
            },
        )

    @property
    def json(self) -> str:
        """Prettified JSON representation of the policy statement."""
        return json.dumps(self.dict, indent=4, sort_keys=False)

    @property
    def dict(self) -> Dict[str, Dict[str, Any]]:
        """Return dictionary with falsey values excluded."""
        statement_dict = {"Sid": self.Sid, "Effect": "Allow", "Action": self.Action}
        if self.Resource:
            statement_dict["Resource"] = self.Resource
        if self.Condition:
            statement_dict["Condition"] = self.Condition
        return statement_dict


@dataclass()
class AWSPolicy:
    """IAM policy document scaffold."""

    Statement: List[AWSPolicyStatement]
    Version: str = "2012-10-17"

    def from_services(services: List[AWSService], wildcard=False):
        """Create object using service information, optionally wildcarding actions."""
        statements = [AWSPolicyStatement.from_services(services, wildcard)]
        return AWSPolicy(Statement=statements)

    @property
    def json(self) -> str:
        """Prettified JSON representation of the policy."""
        d = {
            "Version": self.Version,
            "Statement": [s.dict for s in self.Statement],
        }
        return json.dumps(d, indent=4, sort_keys=False)

    @property
    def dict(self) -> Dict[str, Dict[str, Any]]:
        """Create IAM policy statement scaffold."""
        return asdict(self)

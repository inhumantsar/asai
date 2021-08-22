# AWS Service Authorization Information (ASAI) v0.2.0

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

### Generate Policy Scaffolds

The `policy` command will help you generate policy scaffolds you can tailor to fit your needs.

Policy scaffolds are valid JSON, but *not* valid IAM policies. They demonstrate all of the possible options a service's IAM policy could employ. You must tailor the resulting scaffolds
to create valid IAM policies.

#### Sample Output

The fields below have been truncated for readability. For a complete example which includes
all possible services, see [`tests/expected/policy-all`](tests/expected/policy-all).

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Amazon Comprehend",
            "Effect": "Allow",
            "Action": [
                "comprehend:BatchDetectDominantLanguage",
                "comprehend:BatchDetectEntities",
                ...
            ],
            "Resource": [
                "arn:${Partition}:comprehend:${Region}:${AccountId}:${ResourceType}/${ResourceName}"
            ],
            "Condition": {
                "SomeCondition-IYzBf": {
                    "aws:RequestTag/${TagKey}": "...some value..."
                },
                "SomeCondition-UYQWo": {
                    "comprehend:ModelKmsKey": "...some value..."
                },
                ...
            }
        },
        {
            "Sid": "Amazon Elastic File System",
            "Effect": "Allow",
            "Action": [
                "elasticfilesystem:Backup",
                "elasticfilesystem:ClientMount",
                ...
            ],
            "Resource": [
                "arn:${Partition}:elasticfilesystem:${Region}:${Account}:${ResourceType}/${ResourcePath}"
            ],
            "Condition": {...}
        },
        ...
    ]
}
```

#### Command details

    asai policy [OPTIONS]

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
  
      Options:
        -p, --prefix TEXT  Specific service prefix. Can be used multiple times.
        --all-global       Include all global services in policy scaffold.
        --all-regional     Include all global services in policy scaffold.
        -s, --search TEXT  Include all search results. Can be used multiple times.
        --wildcard         Wildcard the actions list of all specified services.
        --group            Group services by parameter.
        --help             Show this message and exit.


### Service Information

The `service` and `services` commands will display prefix names and other information
about particular services.

| Command    | Subcommand         | Description |
|------------|--------------------|---|
| `services` | `all`              |List all service prefixes.|
|            | `global`           |List all services which aren't tied to specific regions.|
|            | `no-arn`           |List all services which don't have an ARN format.|
|            | `regional`         |List all services which are tied to specific regions.|
|            | `search`           |Search for a service by name or prefix.|
| `service`  | `actions`          |List a service's actions.|
|            | `actions-wildcard` |List a service's actions, wildcarding common prefixes.|
|            | `arn-format`       |Display a service's ARN format description.|
|            | `arn-regex`        |Display a service's ARN Regex string.|
|            | `info`             |Print all available service information.|

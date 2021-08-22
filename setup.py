"""ASAI can find the available actions, conditions, and other useful IAM information for AWS services."""

from os.path import dirname, join
from pathlib import Path

from setuptools import find_packages, setup

GITHUB_URL = "https://github.com/inhumantsar/asai"
VERSION = "0.2.0"


def read(fname):
    """Read content of a file and return as a string."""
    return Path(join(dirname(__file__), fname)).read_text()


def get_requirements():
    """Return requirements with loose version restrictions."""
    return read("requirements.txt").replace("==", ">=").split("\n")


setup(
    name="asai",
    version=VERSION,
    license="BSD License",
    url=GITHUB_URL,
    download_url=f"{GITHUB_URL}/archive/refs/tags/v{VERSION}.zip",
    project_urls={"Repository": GITHUB_URL, "Bug Reports": f"{GITHUB_URL}/issues"},
    author="Shaun Martin",
    author_email="inhumantsar@protonmail.com",
    description="ASAI can find the available actions, conditions, and other useful IAM information for AWS services.",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    install_requires=get_requirements(),
    test_suite="tests",
    keywords=["aws", "iam", "amazon web services"],
    setup_requires=["pytest-runner"],
    tests_require=["tox==3.24.0", "pytest==6.2.4", "pytest-xdist==2.3.0"],
    python_requires=">=3.6.0",
    entry_points={
        "console_scripts": [
            "asai=asai._cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Utilities",
    ],
)

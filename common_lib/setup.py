from pathlib import Path

from setuptools import find_packages, setup


def parse_requirements(file_name: str):
    file_path = Path(__file__).parent.absolute() / file_name

    with open(file_path, "r") as fp:
        return list(fp.readlines())


setup(
    name="common_lib",
    version="0.0.1",
    description="Common library for shared utilities.",
    packages=find_packages(),
    install_requires=parse_requirements("requirements.in"),
)

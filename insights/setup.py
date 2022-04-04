from pathlib import Path

from setuptools import find_packages, setup


def parse_requirements(file_name: str):
    file_path = Path(__file__).parent.absolute() / file_name

    with open(file_path, "r") as fp:
        return list(fp.readlines())


setup(
    name="insights",
    version="0.0.1",
    description="When you haven't got an ETL system =)",
    packages=find_packages(),
    install_requires=parse_requirements("requirements.in"),
)

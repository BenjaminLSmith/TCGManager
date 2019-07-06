"""Build package and setup plugins for TCTManager."""
from setuptools import setup, find_packages

setup(
    setup_requires=['pbr', 'pytest-runner'],
    tests_require=["pytest"],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    pbr=True,
)

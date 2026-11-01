from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in bharat_business/__init__.py
from bharat_business import __version__ as version

setup(
    name="bharat_business",
    version=version,
    description="Indian Small Business Operating Platform built on Frappe + ERPNext",
    author="Bharat Business",
    author_email="hello@bharatbusiness.in",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)

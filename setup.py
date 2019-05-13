from setuptools import setup, find_packages

setup(
    name='wagtail-tableblock',
    version='0.0.1',
    description='A robust TableBlock implementation for Wagtail CMS.',
    url='https://github.com/caltechads/wagtail-tableblock',
    author='Caltech IMSS ADS',
    author_email='imss-ads-staff@caltech.edu',
    license='GPL-3.0',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Programming Language :: Python",
        "Programming Language :: Python 3.6",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)

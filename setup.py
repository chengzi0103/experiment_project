#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as requirements_file:
    all_pkgs = requirements_file.readlines()
requirements = [pkg.replace('\n', '') for pkg in all_pkgs]

test_requirements = []

setup(
    author="experiment_project",
    author_email='cheng.chen@.net',
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
    ],
    description="inboc python project basic template",
    entry_points={
        'console_scripts': [
            'experiment_project=experiment_project.main:run_tool',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='experiment_project',
    name='experiment_project',
    packages=find_packages(include=['experiment_project', 'experiment_project.*']),
    test_suite='tests',
    tests_require=test_requirements,
    version='0.1.1.dev0',
    zip_safe=False,
    dependency_links=[]

)

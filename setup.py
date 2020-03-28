#! /usr/bin/env python
# encoding: utf-8

from setuptools import setup, find_packages


def main():

    install_requires = [
        'twilio',
        'Flask >= 0.12',
        'numpy',
        'scikit-learn'
    ]
    packages = [p for p in find_packages() if "test" not in p]

    setup(
        name='codevscovid19',
        version='0.0.0',
        description='Something for CodeVsCovid19',
        author='Eric Bezzam',
        author_email="ebezzam@gmail.com",
        license=None,
        install_requires=install_requires,
        packages=packages,
        include_package_data=True,
        zip_safe=False,
    )


if __name__ == '__main__':
    main()

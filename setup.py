#!/usr/bin/env python3

setup(
    name='Lambda Queue Consumer',
    version='0.0.1',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=reqs,
    test_suite='lambda_queue_consumer.test'
)

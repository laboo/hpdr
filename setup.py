from setuptools import find_packages, setup

setup(
    name='hpdr',
    packages=find_packages(),
    version='0.14',
    description='Hive date ranges simplified.',
    author='Mark Libucha',
    author_email='mlibucha@gmail.com',
    url='http://hpdrdoc.blogspot.com/',
    license='Apache 2.0',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='test',
    zip_safe=False,
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython'
    ),
    install_requires=[
        "attrs>=16.1.0, <17.0.0",
        "enum34>=1.1.6, <2.0.0",
        "funcparserlib>=0.3.6, <1.0.0",
        "future>=0.15.2, <1.0.0",
        "pendulum>=0.5.5, <1.0.0",
        "pytest>=3.0.2, <4.0.0",
        "python-dateutil>=2.5.3, <3.0.0",
        "pytz>=2016.6.1, <2017.0.0",
        "six>=1.10.0, <2.0.0",
        "tabulate>=0.7.5, <2.0.0"
    ]
)

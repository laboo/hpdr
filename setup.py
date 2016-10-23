from setuptools import find_packages, setup

setup(
    name='hpdr',
    packages=find_packages(),
    version='0.1',
    description='Hive partition date range',
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
        'Programming Language :: Python :: Implementation :: CPython'
    )
)

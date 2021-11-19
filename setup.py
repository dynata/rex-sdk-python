import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


setuptools.setup(
    name="dynata_rex",
    version="0.0.1",
    author="Grant Ward",
    author_email="grant.ward@dynata.com",
    description=("Package for building and interacting with the "
                 "Dynata Respondent Exchange (REX)"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dynata/rex-sdk-python",
    packages=setuptools.find_packages(exclude=('tests', )),
    platforms=['Any'],
    install_requires=requirements,
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    keywords='smor dynata python',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
)

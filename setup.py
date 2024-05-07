from setuptools import setup

setup(
    name="pinkrst",
    version="0.0.1a",
    author="BSL5",
    description="Opinionated ReStructured Text (.rst) Formatter",
    entry_points={
        "console_scripts": ["pink=pinkrst.pinkrst:main"],
    },
    install_requires=["argparse","rich"],
    python_requires=">3.5",
)

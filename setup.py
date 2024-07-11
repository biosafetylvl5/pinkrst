from setuptools import setup, find_packages

setup(
    name="pinkrst",
    version="0.0.1a",
    author="BSL5",
    description="Opinionated ReStructured Text (.rst) Formatter",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": ["pink=pinkrst.pinkrst:main"],
    },
    install_requires=["argparse", "rich"],
    python_requires=">3.5",
)

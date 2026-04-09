from setuptools import setup, find_packages  # type: ignore

setup(
    name="manifesto-nt",
    version="1.0.1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "manifesto=manifesto.cli:main",
        ],
    },
    author="Fedja Arnautovic",
    description="Automate your releases.",
    python_requires=">=3.8",
)

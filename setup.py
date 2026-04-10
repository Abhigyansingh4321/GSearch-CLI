from pathlib import Path

from setuptools import find_packages, setup


ROOT = Path(__file__).parent


setup(
    name="gsearch-cli",
    version="0.2.0",
    author="Abhigyan Singh",
    author_email="your.email@example.com",
    description="A terminal-first web search CLI with Rich output and scriptable modes.",
    long_description=(ROOT / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/abhigyansingh4321/G-Search-CLI",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.8",
        "ddgs>=9.13.0",
        "python-dotenv>=1.0.1",
        "requests>=2.33.1",
        "rich>=13.7.0",
    ],
    entry_points={
        "console_scripts": [
            "gsearch=src.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)

"""
Setup script for Unified Agent System
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("unified/requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="unified-agents",
    version="0.1.0",
    author="AI Agent Development Team",
    description="Unified D3P-SuperClaude Agent System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/agents",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "unified-agents=unified.cli:cli",
            "ua=unified.cli:cli",  # Short alias
        ],
    },
    include_package_data=True,
    package_data={
        "unified": [
            "config/*.yml",
            "config/*.yaml",
        ],
        "": [
            "design_agents/*.yaml",
            "dev_agents/*.yaml",
            "d3p/*.yaml",
            "d3p/phases/*.md",
        ],
    },
)
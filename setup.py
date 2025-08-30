#!/usr/bin/env python3
"""
SaaS Factory - Setup Script
Modern, Clean Architecture for AI-Powered SaaS Applications
"""

from setuptools import setup, find_packages
import os

# Read requirements from requirements.txt
def read_requirements():
    with open('requirements.txt') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read README for long description
def read_readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name="saas-factory",
    version="2.0.0",
    description="Modern, Clean Architecture for AI-Powered SaaS Applications",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="SaaS Factory Team",
    author_email="team@saas-factory.com",
    url="https://github.com/your-org/saas-factory",
    packages=find_packages(include=['agents.*', 'shared.*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.12.0",
            "isort>=5.13.0",
            "flake8>=6.1.0",
            "mypy>=1.8.0",
            "pre-commit>=3.6.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.5.0",
        ],
        "monitoring": [
            "sentry-sdk[fastapi]>=1.40.0",
            "opentelemetry-api>=1.21.0",
            "opentelemetry-sdk>=1.21.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "saas-factory=agents.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="saas, ai, agents, fastapi, react, supabase, typescript",
    project_urls={
        "Bug Reports": "https://github.com/your-org/saas-factory/issues",
        "Source": "https://github.com/your-org/saas-factory",
        "Documentation": "https://github.com/your-org/saas-factory#readme",
    },
)

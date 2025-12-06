"""
Setup script for NASA RDEF Reader package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nasa-rdef-reader",
    version="1.0.0",
    author="NASA RDEF Tools",
    author_email="support@example.com",
    description="A tool for reading legacy NASA RDEF telemetry files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nasa/rdef-reader",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies for basic functionality
        # Users can optionally install additional packages for enhanced features
    ],
    extras_require={
        "gui": [],  # GUI functionality uses only standard library
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
        ],
    },
    entry_points={
        "console_scripts": [
            "rdef-viewer=nasa_rdef_reader.gui:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

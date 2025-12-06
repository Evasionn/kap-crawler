"""Setup configuration for kap-crawler package."""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kap-crawler",
    version="0.1.0",
    author="Evasionn",
    description="Crawl announcements from Kamuyu Aydınlatma Platformu (KAP)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Evasionn/kap-crawler",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "marshmallow>=3.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "black>=23.0.0",
            "pylint>=3.0.0",
        ],
    },
)

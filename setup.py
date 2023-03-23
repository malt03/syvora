from setuptools import setup, find_packages

setup(
    name="syvora",
    version="0.1.0",
    description="A compiler/interpreter for the Syvora programming language",
    author="Koji Murata",
    author_email="k@malt03.com",
    url="https://github.com/malt03/syvora",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "syvora=syvora.main:main",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
)

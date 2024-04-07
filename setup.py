from setuptools import setup, find_packages

setup(
    name="gif-steganography",
    version="0.0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "gif-steganography=gif_steganography.cli:main",
        ],
    },
)

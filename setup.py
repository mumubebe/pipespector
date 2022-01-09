import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pipespector",
    version="0.1",
    author="mumubebe",
    description="debugging and tracing pipes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mumubebe/pipespector/",
    project_urls={
        "Bug Tracker": "https://github.com/mumubebe/pipespector/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    setup_requires=["wheel"],
    entry_points={
        "console_scripts": [
            "pipespector=pipespector.shell:main",
        ],
    },
)

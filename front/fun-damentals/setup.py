import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fun-damentals",
    version="0.0.1",
    author="Adilson Angelo",
    author_email="adilson.angelo.jr@gmail.com   ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AdilsonAngelo/TrabalhoGraduacao",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pworm",
    version="0.0.1",
    author="emuggie",
    author_email="emuggie@gmail.com",
    description="Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/emuggie/serverlease-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD 3-Clause License",
        "Operating System :: OS Independent",
    ],
    entry_point = {
        'console_scripts' : ['run=pworm.server:run']
    },
    python_requires='>=3.5',
)
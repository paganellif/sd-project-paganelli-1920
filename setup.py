import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='sd-project-paganelli-1920',
    version='0.0.1',
    packages=setuptools.find_packages(),
    url='https://gitlab.com/paganelli.f/sd-project-paganelli-1920',
    author='Filippo Paganelli',
    author_email='filippo1paganelli@gmail.com',
    description='Forest Fire Detection using Multi-Agent Systems and Wireless Sensor Networks',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='<3.8',
    setup_requires=['wheel']
)

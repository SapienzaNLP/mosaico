from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.readlines()

setup(
    name="mosaico",
    version="0.1.0",
    description="MOSAICo library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/poccio/mosaico",
    license="cc-by-nc-sa-4.0",
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=requirements,
    python_requires=">=3.10.0",
    author="Luigi Procopio",
    author_email="luigi.procopio@litus.ai",
    zip_safe=False,
)

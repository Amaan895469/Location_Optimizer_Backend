from setuptools import setup, find_packages

setup(
    name="operations_research",
    version="0.1.0",
    packages=find_packages("src"),
    install_requires=[
        "pulp",
        "numpy",
        "pandas",
        "flask",  
    ],
    author="Amaan Alauddin",
    author_email="amaaniqbal1@gmail.com",
    description="Operations Research optimization package",
    keywords="operations-research, optimization, p-median",
    python_requires=">=3.6",
)
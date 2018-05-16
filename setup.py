from setuptools import setup, find_packages


requires = [
    'requests',
    'numpy',
    'matplotlib',
    'pandas',
    'networkx',
]

setup(name='py-sbfsem',
      version=0,
      description='A Python package for Viking connectomics',
      author="Sara Patterson",
      author_email="sarap44@uw.edu",
      packages=find_packages(),
      install_requires=requires, )

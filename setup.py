from setuptools import setup, find_packages

import magichue


setup(
    name='python-magichue',
    version=magichue.__version__,
    url='https://github.com/namacha/python-magichue',
    author=magichue.__author__,
    author_email='mac.ayu15@gmail.com',
    long_description_content_type='text/markdown',
    description='A library to interface with Magichue(or Magichome)',
    long_description=open('README.md').read(),
    license=magichue.__license__,
    
    packages=find_packages(),
)

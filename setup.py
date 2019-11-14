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
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Home Automation',
    ],
    packages=find_packages(),
)

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.rst').read_text(encoding='utf-8')

setup(
    name='sber-payments',
    version='0.3.0',
    author='Anton Popov',
    author_email='anton@jokerinteractive.ru',
    description='SBERBank Payments Python Client Library',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/jokerinteractive/sber-payments/',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Office/Business',
        'Topic :: Office/Business :: Financial',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.6',
    project_urls={
        'Bug Reports': 'https://github.com/jokerinteractive/sber-payments/issues',
        'Funding': 'https://yoomoney.ru/to/41001137693525',
        'Say Thanks!': 'https://saythanks.io/to/ademaro%40ya.ru',
        'Source': 'https://github.com/jokerinteractive/sber-payments/',
    },
    install_requires=['requests'], 
)
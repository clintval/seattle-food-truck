import io

from setuptools import find_packages, setup

with io.open('README.md', encoding='utf-8') as f:
    long_description = f.read()

VERSION = '0.3.0'
PACKAGE = 'seattle-food-truck'
AUTHOR = 'clintval'
ARTIFACT = f'https://github.com/{AUTHOR}/{PACKAGE}/archive/v{VERSION}.tar.gz'

DESCRIPTION = """Python client for the glorious food trucks in Seattle"""

setup(
    name=PACKAGE.replace('-', '_'),
    packages=find_packages(),
    version=VERSION,
    description=(DESCRIPTION),
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email='valentine.clint@gmail.com',
    download_url=ARTIFACT,
    url=f'https://github.com/{AUTHOR}/{PACKAGE}',
    py_modules=[PACKAGE],
    install_requires=[
        'click',
        'geopy',
        'lazy-property',
        'python-dateutil',
        'requests',
        'requests_futures',
        'terminaltables'
    ],
    scripts=[
        'scripts/sft',
    ],
    license='MIT',
    zip_safe=True,
    keywords='seattle food truck',
    project_urls={
        'Seattle Food Truck': 'https://seattlefoodtruck.com/'
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)

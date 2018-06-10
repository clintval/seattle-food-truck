from setuptools import setup, find_packages

setup(
    name='seattle_food_truck',
    version='0.1.2',
    author='clintval',
    author_email='valentine.clint@gmail.com',
    url='https://github.com/clintval/seattle-food-truck',
    download_url='https://github.com/clintval/seattle-food-truck/releases/tag/0.1.1',
    license='MIT',
    keywords=['seattle', 'food', 'truck'],
    install_requires=[
        'click',
        'lazy-property',
        'python-dateutil',
        'requests',
        'requests_futures',
        'terminaltables'
    ],
    scripts=['scripts/sft'],
    packages=find_packages())

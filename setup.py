from setuptools import setup, find_packages

setup(
    name='seattle_food_truck',
    version='0.1.0',
    author='clintval',
    author_email='valentine.clint@gmail.com',
    url='https://github.com/clintval/seattle-food-truck',
    download_url='https://github.com/clintval/seattle-food-truck/releases/tag/0.1.0',
    license='MIT',
    keywords=['seattle', 'food', 'truck'],
    install_requires=[
        'click',
        'python-dateutil',
        'requests'
        'terminaltables'],
    scripts=['scripts/sft'],
    packages=find_packages())

print("""
-------------------------------------------
 seattle_food_truck installation complete!
-------------------------------------------
""")

from setuptools import setup, find_packages

setup(
    name='seattle_food_truck',
    version='0.1',
    author='clintval',
    author_email='valentine.clint@gmail.com',
    url='https://github.com/clintval/seattle-food-truck',
    license='MIT',
    install_requires=[
        'python-dateutil',
        'requests'],
    scripts=[],  # CLI coming!
    packages=find_packages())

print("""
-------------------------------------------
 seattle_food_truck installation complete!
-------------------------------------------
""")

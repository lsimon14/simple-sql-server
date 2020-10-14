import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='simple-sql-server',
    version='0.0.2',
    author='Luke Simon',
    description='Python package to perform basic SQL Server functions',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/lsimon14/simple-sql-server',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3',
    install_requires=[
        'bcpy',
        'pyodbc'
    ]
)

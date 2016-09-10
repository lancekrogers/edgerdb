from setuptools import setup

setup(name='edgerdb',
      version='0.1',
      description='A package for installing a database of edger database filings.',
      url='https://github.com/lancekrogers/edgerdb',
      author='Lance Rogers',
      author_email='lancekrogers@gmail.com',
      license='MIT',
      packages=['edgerdb'],
      install_requires=[
          'psycopg2',
      ],
      zip_safe=False)

from setuptools import setup

setup(name='edgerdb',
      version='1.1.2.2',
      description='A package for installing a database of edgar database filings.',
      url='https://github.com/lancekrogers/edgerdb',
      author='Lance Rogers',
      author_email='lancekrogers@gmail.com',
      license='MIT',
      packages=['edgerdb', 'edgerdb.settings'],
      #package_data={'': ['*.log']},
      include_package_data=True,
      install_requires=[
          'psycopg2',
      ],
      zip_safe=False)

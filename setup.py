from setuptools import setup
import idbase

install_requires = ['Django', 'pytz', 'django_compressor']

setup(name='idbase',
      version=idbase.__version__,
      description='Identity.UW base look and feel',
      install_requires=install_requires,
      )

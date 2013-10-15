from setuptools import setup

setup(
    name='Flask-Stats',
    version='0.0.1',
    url='https://github.com/gabrielpjordao/flask-stats',
    license='BSD',
    author='Gabriel Jordao, Rodrigo Ribeiro',
    description='Extension for gathering stats from flask applications',
    py_modules=['flask_stats'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=['Flask', 'statsd'],
    tests_require=['mock'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

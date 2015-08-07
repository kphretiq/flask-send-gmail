"""
Flask-Send-Gmail
-------------

Send plaintext, html emails (using Jinja Templates) and attachments using
your gmail account.
"""
from setuptools import setup

setup(
    name='Flask-Send-Gmail',
    version='1.0',
    url='https://github.com/kphretiq/flask-send-gmail',
    license='BSD',
    author='Doug Shawhan',
    author_email='kphretiq@gmail.com',
    description='Send email with gmail.',
    long_description=__doc__,
    py_modules=['flask_send_gmail'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

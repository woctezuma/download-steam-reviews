from distutils.core import setup

# noinspection PyUnresolvedReferences
import setuptools

setup(
    name='steamreviews',
    packages=['steamreviews'],
    install_requires=[
        'requests',
    ],
    version='0.5.0',
    description='An API to download Steam reviews',
    long_description='Steam Reviews: an API to download Steam reviews, written in Python 3.',
    long_description_content_type='text/x-rst',
    author='Wok',
    author_email='wok@tuta.io',
    url='https://github.com/woctezuma/download-steam-reviews',
    download_url='https://github.com/woctezuma/download-steam-reviews/archive/0.5.0.tar.gz',
    keywords=['steam', 'review', 'reviews', 'download', 'api'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Games/Entertainment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)

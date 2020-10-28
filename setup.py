import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='steamreviews',
    version='0.9.2',
    author='Wok',
    author_email='wok@tuta.io',
    description='An API to download Steam reviews',
    keywords=['steam', 'review', 'reviews', 'download', 'api'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/woctezuma/download-steam-reviews',
    download_url='https://github.com/woctezuma/download-steam-reviews/archive/0.9.2.tar.gz',
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Games/Entertainment',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
)

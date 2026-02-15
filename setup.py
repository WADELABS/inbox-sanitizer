from setuptools import setup, find_packages

setup(
    name="inbox-sanitizer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'google-api-python-client>=2.0.0',
        'google-auth-httplib2>=0.1.0',
        'google-auth-oauthlib>=0.4.0',
        'schedule>=1.0.0',
        'pyyaml>=5.4.0',
    ],
    entry_points={
        'console_scripts': [
            'inbox-sanitizer=src.cli:main',
        ],
    },
    author="WADELABS",
    description="Automatically clean up your Gmail inbox",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/WADELABS/inbox-sanitizer",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

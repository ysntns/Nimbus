"""
Setup configuration for Nimbus backup solution.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ''

# Read requirements
requirements_file = Path(__file__).parent / 'requirements.txt'
requirements = []
if requirements_file.exists():
    with open(requirements_file, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='nimbus-backup',
    version='2.0.0',
    author='Yasin TANIŞ',
    author_email='ysn.tnss@gmail.com',
    description='Enterprise-grade backup and cloud synchronization solution',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ysntns/nimbus',
    project_urls={
        'Bug Reports': 'https://github.com/ysntns/nimbus/issues',
        'Source': 'https://github.com/ysntns/nimbus',
        'Documentation': 'https://github.com/ysntns/nimbus#readme',
    },
    packages=find_packages(exclude=['tests', 'tests.*', 'docs', 'scripts']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Archiving :: Backup',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
    ],
    keywords='backup, cloud-sync, incremental-backup, encryption, multi-cloud',
    python_requires='>=3.8',
    install_requires=[
        'click>=8.1.0',
        'rich>=13.0.0',
        'loguru>=0.7.0',
        'pyyaml>=6.0',
        'psutil>=5.9.0',
        'requests>=2.31.0',
    ],
    extras_require={
        'gui': [
            'PyQt6>=6.5.0',
            'PyQt6-WebEngine>=6.5.0',
        ],
        'cloud': [
            'google-api-python-client>=2.100.0',
            'dropbox>=11.36.0',
            'boto3>=1.28.0',
        ],
        'crypto': [
            'cryptography>=41.0.0',
        ],
        'scheduler': [
            'apscheduler>=3.10.0',
        ],
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'pytest-mock>=3.11.0',
            'black>=23.7.0',
            'isort>=5.12.0',
            'flake8>=6.1.0',
            'mypy>=1.5.0',
        ],
        'all': [
            'PyQt6>=6.5.0',
            'PyQt6-WebEngine>=6.5.0',
            'google-api-python-client>=2.100.0',
            'dropbox>=11.36.0',
            'boto3>=1.28.0',
            'cryptography>=41.0.0',
            'apscheduler>=3.10.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'nimbus=app.cli.main:cli',
        ],
    },
    include_package_data=True,
    package_data={
        'app': ['py.typed'],
    },
    zip_safe=False,
)

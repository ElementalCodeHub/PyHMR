from setuptools import setup,find_packages

setup(
    name='HMR',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'Click',
        'watchdog'
    ],
    entry_points={
        'console_scripts': [
            'hmr = main:start_hmr'
        ]
    }
)

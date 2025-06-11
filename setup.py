from setuptools import find_packages, setup

package_name = 'docker_manager'

setup(
    name=package_name,
    description='Utility for launching Docker containers from a GUI',
    version='0.1.0',
    maintainer='Michael Ripperger',
    maintainer_email='michael.ripperger@swri.org',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        f'{package_name}': ['*.ui', ]
    },
    license_files=[
        'LICENSE',
    ],
    install_requires=[
        'PyQt5',
        'docker',
    ],
    zip_safe=True,
    scripts=[
        'scripts/docker_manager',
    ],
)


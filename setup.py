"""Setup package."""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ssh-websocket",
    version="0.0.3",
    author="Thomas Nicollet",
    author_email="thomas.nicollet@epitech.eu",
    description="A Stable implementation of a SSH server over websocket",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nwmqpa/SSHWebSocket",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ),
    entry_points={'console_scripts': [
        'dns_server = ssh_websocket.dns_server:main',
        'ssh_server = ssh_websocket.ssh_server:main',
        'ssh_client = ssh_websocket.ssh_client:main',
    ]},
    install_requires=['twisted', 'autobahn', 'websocket-client', 'websockets']
)
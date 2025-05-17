from setuptools import setup, find_packages

setup(
    name="automata_app",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "networkx",
        "matplotlib",
    ],
    entry_points={
        'console_scripts': [
            'automata-app=gui.main:main',
        ],
    },
    author="Student",
    description="A Python application for finite automata manipulation and visualization",
    keywords="automata, finite state machine, DFA, NFA, tkinter",
    python_requires=">=3.6",
) 
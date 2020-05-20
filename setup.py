from setuptools import setup

setup(
        name="acload",
        version="0.1",
        py_modules=["acload"],
        install_requires=[
            "Click",
            ],
        entry_points="""
            [console_scripts]
            acload=acload:cli
        """,
        )


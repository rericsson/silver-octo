from setuptools import setup

setup(
        name="acload",
        version="0.1",
        py_modules=[
            "ac_api",
            "acload",
            "mapping"
            ],
        install_requires=[
            "Click",
            "dataclasses-json",
            "python-dotenv",
            "openpyxl",
            "requests",
            "requests-oauthlib",
            ],
        entry_points="""
            [console_scripts]
            acload=acload:cli
        """,
        )


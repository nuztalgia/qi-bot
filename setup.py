from setuptools import setup

setup(
    url="https://github.com/nuztalgia/qibot",
    project_urls={
        "Issue Tracker": "https://github.com/nuztalgia/qibot/issues",
        "Source Code": "https://github.com/nuztalgia/qibot",
    },
    install_requires=[
        "aiohttp ==3.8.3",
        "botstrap >=0.2.7",
        "humanize ==4.4.0",
        "json5 ==0.9.10",
        "pillow ==10.3.0",
        "py-cord ==2.2.2",
    ],
)

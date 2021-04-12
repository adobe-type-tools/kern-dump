from setuptools import setup


with open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()


setup(
    name="kern-dump",
    use_scm_version=True,
    description="Various scripts for analyzing, reading and writing kerning information.",
    long_description=long_description,
    author="Frank Grießhammer",
    author_email="afdko@adobe.com",
    url="https://github.com/adobe-type-tools/kern-dump",
    license="MIT License",
    platforms=["Any"],
    setup_requires=["setuptools_scm"],
    python_requires=">=3.6",
    py_modules=[
        "getKerningPairsFromOTF",
        "getKerningPairsFromUFO",
        "getKerningPairsFromFEA",
    ],
    entry_points={
        'console_scripts': [
            'dumpkerning=dumpkerning:main',
            'dumpKernFeatureFromOTF=dumpKernFeatureFromOTF:main',
            'convertKernedOTFtoKernedUFO=convertKernedOTFtoKernedUFO:main',
        ],
    },
    install_requires=["afdko"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Text Processing :: Fonts",
    ]
)

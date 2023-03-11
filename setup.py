import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
	long_description = fh.read()

setuptools.setup(
		author="Matheus Vilano",
		author_email="mattvilano+pip@gmail.com",
		classifiers=[
			"Development Status :: 5 - Production/Stable",
			"Intended Audience :: Developers",
			"License :: OSI Approved :: MIT License",
			"Operating System :: OS Independent",
			"Programming Language :: Python :: 3",
		],
		description="A simple framework for event-driven programming.",
		install_requires=[],
		keywords="observer listener event design pattern callback",
		license="MIT",
		long_description=long_description,
		long_description_content_type="events",
		name="simplevent",
		packages=setuptools.find_packages(where="src"),
		package_dir={"": "src"},
		project_urls={
			"Author Website": "https://www.matheusvilano.com/",
			"Git Repository": "https://github.com/matheusvilano/simplevent",
		},
		python_requires=">=3.6",
		url="package URL",
		version="1.0.0",
)

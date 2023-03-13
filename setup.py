import setuptools
from pathlib import Path

long_description = (Path(__file__).parent/"README.md").read_text()

setuptools.setup(
		author="Matheus Vilano",
		classifiers=[
			"Development Status :: 5 - Production/Stable",
			"Intended Audience :: Developers",
			"License :: OSI Approved :: MIT License",
			"Operating System :: OS Independent",
			"Programming Language :: Python :: 3",
		],
		description="A simple framework for event-driven programming, based on the Observer design pattern.",
		install_requires=[],
		keywords="event observer listener subscription subscriber subject design pattern callback",
		license="MIT",
		long_description=long_description,
		long_description_content_type="text/markdown",  # GitHub-flavored Markdown (GFM)
		name="simplevent",
		packages=setuptools.find_packages("src"),
		package_dir={"": "src"},
		project_urls={
			"Author Website": "https://www.matheusvilano.com/",
			"Git Repository": "https://github.com/matheusvilano/simplevent",
		},
		python_requires=">=3.6",
		url="https://github.com/matheusvilano/simplevent.git",
		version="1.0.1",
)

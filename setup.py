from setuptools import setup

with open("README.md", "r") as f:
	readme = f.read()

setup(
	name='sparqly',
	version='0.1.1',
	description='SPARQL semantic translator and ORM for Python.',
	long_description=readme,
	long_description_content_type='text/markdown',
	author='Dustpancake',
	author_email='fergusb.temp@gmail.com',
	url='https://github.com/Dustpancake/sparqly',
	packages=[
		'sparqly'
	],
	classifiers=[
		"Programming Language :: Python :: 3.7",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
	],
	python_requires=">=3.7",
	zip_safe=False
)

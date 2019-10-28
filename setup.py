from setuptools import setup, find_packages

LONG_DESCRIPTION = open("README.md").read()

setup(name="aws-lambda-decorators",
      version="0.44",
      description="A set of python decorators to simplify aws python lambda development",
      long_description=LONG_DESCRIPTION,
      long_description_content_type="text/markdown",
      url="https://github.com/gridsmartercities/aws-lambda-decorators",
      author="Grid Smarter Cities",
      author_email="open-source@gridsmartercities.com",
      license="MIT",
      classifiers=["Intended Audience :: Developers",
                   "Development Status :: 4 - Beta",
                   "Programming Language :: Python :: 3",
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent",
                   "Natural Language :: English"
                   ],
      keywords="aws lambda decorator",
      packages=find_packages(exclude="tests"),
      install_requires=[
          "boto3",
          "PyJWT",
          "schema"
      ],
      zip_safe=False
      )

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="coffee-business-chatbot",
    version="1.3.0",
    author="Coffee Business AI Team",
    author_email="info@coffeeai.com",
    description="AI-powered chatbot for coffee business consultation and sales qualification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/coffee-business-chatbot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Communications :: Chat",
        "Topic :: Office/Business",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "httpx>=0.24.0",
            "websockets>=12.0",
        ],
        "docs": [
            "mkdocs>=1.4.0",
            "mkdocs-material>=9.0.0",
            "mkdocstrings>=0.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "coffee-chatbot=web_knowledge_chatbot:main",
            "coffee-chatbot-cli=knowledge_based_chatbot:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json", "*.html", "*.css", "*.js"],
        "knowledge": ["*.mdx"],
        "static": ["*"],
    },
    keywords="ai chatbot coffee business langchain openai fastapi websocket",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/coffee-business-chatbot/issues",
        "Source": "https://github.com/yourusername/coffee-business-chatbot",
        "Documentation": "https://github.com/yourusername/coffee-business-chatbot#readme",
    },
)
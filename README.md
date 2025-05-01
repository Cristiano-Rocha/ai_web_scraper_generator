# AI Web Scraper Generator

An intelligent web scraping tool that uses AI agents to generate and execute web scraping scripts automatically.

## Overview

This project is an AI-powered web scraping solution that automatically generates and executes web scraping scripts. It uses multiple AI agents working together to plan, validate, and implement web scraping tasks, making it easier to extract data from websites without manual coding.

## Features

- **AI-Powered Scraping**: Uses multiple AI agents to plan and execute web scraping tasks
- **Browser Automation**: Integrates with browser automation tools for dynamic content
- **Automatic Code Generation**: Generates Python scraping scripts automatically
- **Flexible Configuration**: Supports various scraping scenarios and requirements
- **HAR File Generation**: Captures browser interactions for analysis

## Project Structure

```
.
├── agents/              # AI agent implementations
├── config/             # Configuration files
├── llm/               # Language model related code
├── prompts/           # AI prompt templates
├── tools/             # Utility tools and functions
├── agents.py          # Main agent orchestration
├── example.py         # Example scraping implementation
├── browser_requests.md # Browser request documentation
├── browser_requests.json # Browser request configurations
├── pyproject.toml     # Project dependencies and metadata
└── uv.lock            # Dependency lock file
```

## Requirements

- Python 3.12 or higher
- Dependencies:
  - aiohttp >= 3.11.18
  - autogen-core >= 0.5.5
  - autogen-ext[azure] >= 0.5.5
  - browser-use >= 0.1.41

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd ai-web-scraper-generator
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

## Usage

The project uses multiple AI agents to handle different aspects of web scraping:

1. **WebPilot Agent**: Initial interface for web interaction, handles browser navigation
2. **Scraping Planner Agent**: Plans the extraction strategy
3. **Code Implementer Agent**: Generates the actual scraping code
4. **Plan Validator Agent**: Validates the scraping plan
5. **Executor Validator Agent**: Validates the execution

### Basic Usage

```python
from agents import main

# Run the scraping system
asyncio.run(main())
```

### Example Implementation

See `example.py` for a basic example of how to implement a web scraper:

```python
import requests
from bs4 import BeautifulSoup

# Configure headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# URL to scrape
url = 'https://example.com/'

# Scrape the site
data = scrape_example_site(url)
```

## Configuration

The project can be configured through various files:

- `browser_requests.json`: Browser request configurations
- `config/`: Directory containing additional configuration files


## License

MIT

## Support

For support, please [add your support contact information] 
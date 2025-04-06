# MCP Webhook AI Agent 🤖

A FastMCP-based server that provides webhook AI agent functionality and RAG (Retrieval-Augmented Generation) capabilities for managing document retrieval and querying.

## Features

- 🔗 Document source management
- 🔍 RAG-based querying
- 📡 Webhook POST endpoint for query processing
- 🚀 Built with FastMCP for seamless integration

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd <your-repo-directory>
```

2. Create and activate a virtual environment:

For Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```

For macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
# Or install individually:
pip install fastmcp requests pydantic
```

To deactivate the virtual environment when you're done:
```bash
deactivate
```

## Usage

### Starting the Server

Run the server in development mode:
```bash
fastmcp dev mcp_rag.py
```

Or install it for use with Claude:
```bash
fastmcp install mcp_rag.py
```

### Available Tools

#### 1. Document Source Management

```python
# Register a new document source
set_document_source({
    "url": "https://your-docs.com/api",
    "description": "API documentation"
})

# List all registered sources
list_document_sources()
```

#### 2. RAG Querying

```python
# Query all document sources
query_rag("How do I implement authentication?")

# Query specific sources
query_rag("How do I implement authentication?", source_ids=["1", "2"])
```

#### 3. Webhook POST Endpoint

Send POST requests with query payloads:

```python
# Process a query through the default endpoint
process_post_query({
    "query": "Your message here"
})

# Use a custom endpoint
process_post_query(
    payload={"query": "Your message here"},
    url="https://your-custom-endpoint.com"
)
```

Example POST request body:
```json
{
    "query": "Your message here"
}
```

### API Reference

#### DocumentSource Model
```python
class DocumentSource:
    url: str          # URL of the document source
    description: str  # Optional description
```

#### QueryPayload Model
```python
class QueryPayload:
    query: str  # The query message to process
```

#### Tool Functions

1. `set_document_source(source: DocumentSource) -> str`
   - Registers a new document source
   - Returns: Confirmation message with source ID

2. `list_document_sources() -> Dict[str, str]`
   - Lists all registered document sources
   - Returns: Dictionary of source IDs and URLs

3. `query_rag(query: str, source_ids: Optional[List[str]] = None) -> str`
   - Queries specified document sources
   - Returns: Retrieved and processed results

4. `process_post_query(payload: QueryPayload, url: str = "https://api.example.com/process") -> str`
   - Processes a POST request with a query payload
   - Returns: Server response or error message

## Development

### Project Structure

```
mcp-webhook-ai-agent/
├── mcp_rag.py          # Main server implementation
├── README.md           # Documentation
├── requirements.txt    # Project dependencies
└── mcp.json           # Cursor AI MCP configuration
```

### Cursor AI MCP Configuration

1. Create an `mcp.json` file in your project root:
```json
{
    "name": "mcp-webhook-ai-agent",
    "version": "1.0.0",
    "description": "Webhook AI agent with RAG capabilities",
    "main": "mcp_rag.py",
    "tools": [
        {
            "name": "set_document_source",
            "description": "Register a new document source URL for RAG operations"
        },
        {
            "name": "list_document_sources",
            "description": "List all registered document sources"
        },
        {
            "name": "query_rag",
            "description": "Query the specified document sources using RAG"
        },
        {
            "name": "process_post_query",
            "description": "Process a POST request with a query payload"
        }
    ],
    "dependencies": {
        "fastmcp": ">=0.4.0",
        "requests": ">=2.31.0",
        "pydantic": ">=2.0.0"
    }
}
```

2. Configure Cursor AI:
   - Open Cursor AI settings
   - Navigate to the MCP section
   - Add the path to your `mcp.json` file
   - Restart Cursor AI to apply changes

3. Verify Configuration:
```bash
# Check if MCP is properly configured
fastmcp check mcp.json

# List available tools
fastmcp list
```

### Adding New Features

1. Define new models in `mcp_rag.py`
2. Add new tools using the `@mcp.tool()` decorator
3. Update documentation as needed

## License

[Your chosen license]

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## Testing

### Setup Test Environment

1. Install test dependencies:
```bash
pip install pytest pytest-mock
```

2. Run tests:
```bash
# Run all tests
pytest -v

# Run specific test file
pytest -v test_mcp_rag.py

# Run with coverage report
pytest --cov=mcp_rag test_mcp_rag.py
```

### Available Tests

1. Document Source Management:
   - `test_set_document_source`: Tests adding valid document sources
   - `test_set_invalid_document_source`: Tests handling invalid URLs
   - `test_list_document_sources`: Tests listing registered sources

2. RAG Querying:
   - `test_query_rag`: Tests querying with mocked responses
   - `test_query_rag_no_sources`: Tests behavior with no sources
   - `test_query_rag_invalid_source_ids`: Tests handling invalid source IDs

3. POST Request Processing:
   - `test_process_post_query`: Tests POST request handling with mocked responses

### Manual Testing

You can also test the server manually using the FastMCP development server:

1. Start the server:
```bash
fastmcp dev mcp_rag.py
```

2. Example test commands:
```python
# Add a test source
set_document_source({
    "url": "https://test-docs.com/api",
    "description": "Test docs"
})

# List sources
list_document_sources()

# Try a query
query_rag("test query")

# Test POST endpoint
process_post_query({
    "query": "test message"
})
``` 
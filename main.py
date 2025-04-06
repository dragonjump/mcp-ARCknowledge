from fastmcp import FastMCP
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import requests
from urllib.parse import urlparse
import json

# Initialize FastMCP server
mcp = FastMCP(
    "MCP Master Webhook Agents",
    description="Your custom webhook knowledge base tool-use or RAG (Retrieval-Augmented Generation) server for managing document retrieval and querying",
    dependencies=["requests", "pydantic"]
) 

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


# Store for document sources
document_sources: Dict[str, str] = {}

class DocumentSource(BaseModel):
    """Model for document source configuration"""
    url: str = Field(..., description="URL of the document source")
    description: Optional[str] = Field(None, description="Optional description of the source")

class QueryPayload(BaseModel):
    """Model for query payload"""
    query: str = Field(..., description="The query message to process")

@mcp.tool()
def set_document_source(source: Dict[str, str]) -> str:
    """
    Register a new document source URL for RAG operations and save to JSON file
    
    Args:
        source: Dictionary containing url and optional description
    
    Returns:
        str: Confirmation message
    """
    if 'url' not in source:
        return "Error: URL is required"
    
    try:
        # Load existing sources from file
        try:
            with open('document_sources.json', 'r') as f:
                file_sources = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            file_sources = {}
        
        # Generate new source ID
        source_id = str(len(file_sources) + 1)
        
        # Add to memory dictionary
        document_sources[source_id] = source['url']
        
        # Add to file sources
        file_sources[source_id] = {
            "url": source['url'],
            "description": source.get('description', '')
        }
        
        # Save back to file
        with open('document_sources.json', 'w') as f:
            json.dump(file_sources, f, indent=4)
        
        return f"Document source registered with ID: {source_id}"
    except Exception as e:
        return f"Error saving to file: {str(e)}"

@mcp.tool()
def list_document_sources() -> Dict[str, str]:
    """
    List all registered document sources
    
    Returns:
        Dict[str, str]: Dictionary of source IDs and their URLs
    """
    return document_sources

@mcp.tool()
def query_rag(query: str, source_ids: Optional[List[str]] = None) -> str:
    """
    Query the specified document sources using RAG
    
    Args:
        query: The search query
        source_ids: Optional list of source IDs to query (if None, queries all sources)
    
    Returns:
        str: Retrieved and processed results
    """
    if not document_sources:
        return "Error: No document sources registered"
    
    sources_to_query = document_sources
    if source_ids:
        sources_to_query = {id: document_sources[id] 
                           for id in source_ids 
                           if id in document_sources}
        if not sources_to_query:
            return "Error: No valid source IDs provided"
    
    results = []
    for source_id, url in sources_to_query.items():
        try:
            # Send POST request with chatInput payload
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            payload = {"chatInput": query}
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                results.append(f"Source {source_id}: {response.text}")
            else:
                results.append(f"Source {source_id}: Failed to retrieve content. Status code: {response.status_code}")
        except Exception as e:
            results.append(f"Source {source_id}: Error - {str(e)}")
    
    return "\n".join(results)

@mcp.prompt()
def rag_query_prompt(query: str) -> str:
    """Create a prompt template for RAG queries"""
    return f"""Please help me find information about the following query:
Query: {query}

Available document sources:
{list_document_sources()}

How would you like to proceed with the search?"""

@mcp.tool()
def process_post_query(payload: QueryPayload, url: str = "https://api.example.com/process") -> str:
    """
    Process a POST request with a query payload
    
    Args:
        payload: QueryPayload object containing the query message
        url: Optional URL to send the POST request to (defaults to example URL)
    
    Returns:
        str: Response from the server
    """
    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        data = {"query": payload.query}
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            return f"Successfully processed query. Response: {response.text}"
        else:
            return f"Error processing query. Status code: {response.status_code}, Response: {response.text}"
    except Exception as e:
        return f"Error making POST request: {str(e)}"

@mcp.tool()
def load_document_sources_from_file(file_path: str = "document_sources.json") -> str:
    """
    Load document sources from a JSON file
    
    Args:
        file_path: Path to the JSON file containing document sources (default: document_sources.json)
    
    Returns:
        str: Confirmation message
    """
    try:
        with open(file_path, 'r') as f:
            sources = json.load(f)
            
        if not isinstance(sources, dict):
            return "Error: JSON file must contain a dictionary of sources"
            
        # Add each source to the document_sources dictionary
        for source_id, source_data in sources.items():
            if isinstance(source_data, str):
                # If the source is just a URL string
                document_sources[source_id] = source_data
            elif isinstance(source_data, dict) and 'url' in source_data:
                # If the source is a dictionary with url
                document_sources[source_id] = source_data['url']
            else:
                return f"Error: Invalid source format for ID {source_id}"
                
        return f"Successfully loaded {len(sources)} document sources from {file_path}"
    except FileNotFoundError:
        return f"Error: File {file_path} not found"
    except json.JSONDecodeError:
        return f"Error: Invalid JSON format in {file_path}"
    except Exception as e:
        return f"Error loading document sources: {str(e)}"

if __name__ == "__main__":
    mcp.run() 

  
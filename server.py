from fastmcp import FastMCP
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import requests
from urllib.parse import urlparse
import json

# Initialize FastMCP server
mcp = FastMCP(
    "mcp-webhook-knowledge-agent",
    description="Your custom webhook knowledge base tool-use or RAG (Retrieval-Augmented Generation) server for managing document retrieval and querying",
    dependencies=["requests", "pydantic"]
)

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
def set_document_source(source: DocumentSource) -> str:
    """
    Register a new document source URL for RAG operations
    
    Args:
        source: DocumentSource object containing the URL and optional description
    
    Returns:
        str: Confirmation message
    """
    parsed_url = urlparse(source.url)
    if not parsed_url.scheme or not parsed_url.netloc:
        return "Error: Invalid URL format"
    
    source_id = str(len(document_sources) + 1)
    document_sources[source_id] = source.url
    return f"Document source registered with ID: {source_id}"

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
    
    # Placeholder for actual RAG implementation
    # In a real implementation, you would:
    # 1. Retrieve documents from sources
    # 2. Process and embed the query
    # 3. Perform similarity search
    # 4. Return relevant context
    
    results = []
    for source_id, url in sources_to_query.items():
        try:
            # This is a simplified example - replace with actual RAG logic
            response = requests.get(url)
            if response.status_code == 200:
                results.append(f"Source {source_id}: Retrieved {len(response.text)} characters")
            else:
                results.append(f"Source {source_id}: Failed to retrieve content")
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

if __name__ == "__main__":
    mcp.run() 
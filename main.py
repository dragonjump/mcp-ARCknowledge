from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import requests
import json
import os
import time
from urllib.parse import urlparse
from fastmcp import FastMCP, Image 

# Initialize FastMCP server
mcp = FastMCP(
    "ArcKnowledge",
    description="ArcKnowledge - Bridge MCP to your custom knowledge base api webhooks. Supports text and image queries.",
    dependencies=["requests", "pydantic"],
    tool_prefix="mcp_arcknowledge", log_level="ERROR")  

# Store for knowledge document sources
knowledge_document_sources: Dict[str, Dict[str, str]] = {}

class QueryRequest(BaseModel):
    """Model for query request with image support"""
    query: str = Field(..., description="The query message to process")
    image: Optional[str] = Field(None, description="Optional base64 encoded image data")

class KnowledgeDocumentSource(BaseModel):
    """Model for knowledge document source configuration"""
    url: str = Field(..., description="URL of the knowledge document source")
    description: Optional[str] = Field(None, description="Optional description of the source")
    apikey: Optional[str] = Field(None, description="Optional apikey of the source")

def load_initial_knowledge_sources(knowledge_document_path: Optional[str] = None) -> None:
    """Load initial knowledge document sources from file"""
    KNOWLEDGE_DOCUMENT_PATH = knowledge_document_path or os.getenv('KNOWLEDGE_DOCUMENT_PATH', 'knowledge_document_sources.json')

    try:
        with open(KNOWLEDGE_DOCUMENT_PATH, 'r') as f:
            sources = json.load(f)
        for source_id, source_data in sources.items():
            if isinstance(source_data, dict) and 'url' in source_data:
                knowledge_document_sources[source_id] = source_data
        print(f"Loaded knowledge sources: {len(knowledge_document_sources)} sources")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"No initial knowledge document sources found at {KNOWLEDGE_DOCUMENT_PATH}: {str(e)}")

@mcp.tool()
def update_knowledge_document_source(knowledge_document_path: str) -> str:
    """
    Update the knowledge document source URL with custom config JSON file
    
    Args:
        knowledge_document_path: Path to the JSON config file
    
    Returns:
        str: Confirmation message
    """
    if not isinstance(knowledge_document_path, str) or not knowledge_document_path.strip():
        return "Error: knowledge_document_path is required and must be a non-empty string"
    
    try:
        load_initial_knowledge_sources(knowledge_document_path.strip())
        return f"Successfully updated knowledge document source to: {knowledge_document_path}"
    except Exception as e:
        return f"Error updating source config: {str(e)}"

@mcp.tool()
def list_knowledge_document_sources() -> Dict[str, Dict[str, str]]:
    """
    List all registered knowledge document sources
    
    Returns:
        Dict[str, Dict[str, str]]: Dictionary of source IDs mapping to their properties
    """
    if not knowledge_document_sources:
        load_initial_knowledge_sources()
    return knowledge_document_sources

 
@mcp.tool()
def load_image(path: str) -> Image:
    """Load an image from disk"""
    # FastMCP handles reading and format detection
    return Image(path=path)
@mcp.tool()
def query_knowledge_base(query: str, source_ids: List[str] = [], image:  str  = '') -> str:
    """
    Query the specified knowledge document sources using knowledge base
    
    Args:
        query: The search query or question user ask
        source_ids: list of source IDs to query (if None, queries all sources)
        image: base64 encoded image string to include in the query
    
    Returns:
        str: Retrieved and processed results
    """
    if not knowledge_document_sources:
        return "Error: No knowledge document sources registered"
    
    results = []
    sources_to_query = knowledge_document_sources
    if source_ids:
        sources_to_query = {id: knowledge_document_sources[id] 
                           for id in source_ids 
                           if id in knowledge_document_sources}
        if not sources_to_query:
            sources_to_query = knowledge_document_sources
            results.append("Warning: No valid source IDs provided, querying all sources")
    
    for source_id, source_info in sources_to_query.items():
        try:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            
            if source_info.get("apikey"):
                headers["x-api-key"] = source_info["apikey"]
                
            # Construct payload with query and optional image
            payload = QueryRequest(query=query, image=image).dict(exclude_none=True)
                
            response = requests.post(source_info["url"], json=payload, headers=headers)
            
            if response.status_code == 200:
                try:
                    # Try to parse and format JSON response
                    resp_data = response.json()
                    results.append(f"Source {source_id}: {json.dumps(resp_data, indent=2)}")
                except json.JSONDecodeError:
                    # Fallback to raw text if not JSON
                    results.append(f"Source {source_id}: {response.text}")
            else:
                results.append(f"Source {source_id}: Failed to retrieve content. Status code: {response.status_code}")
        except Exception as e:
            results.append(f"Source {source_id}: Error - {str(e)}")
    
    return "\n".join(results)

@mcp.tool()
def add_new_knowledge_document_source(url: str, description: str = '', apikey: str= '') -> str:
    """
    Add a new knowledge document source URL and append to existing sources
    
    Args:
        url: URL of the knowledge document source
        description: description of the source 
        apikey: apikey of the source
    Returns:
        str: Confirmation message
    """
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return "Error: Invalid URL format"
            
        source = KnowledgeDocumentSource(
            url=url,
            description=description,
            apikey=apikey
        )
        
        uniqueid = str(int(time.time()))
        knowledge_document_sources[uniqueid] = source.dict(exclude_none=True)
        return f"Knowledge document source added with ID: {uniqueid}"
    except Exception as e:
        return f"Error adding new source: {str(e)}"

if __name__ == "__main__":
    # Load initial sources
    load_initial_knowledge_sources()
    # Start FastMCP server
    mcp.run() 

  
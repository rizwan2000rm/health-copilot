"""
Knowledge Base module for the AI Fitness Coach.

This module handles document processing, vector store management,
and knowledge retrieval functionality.
"""

import os
from typing import Optional, List
from langchain_core.vectorstores import VectorStoreRetriever
from document_processor import DocumentProcessor


class KnowledgeBase:
    """Handles knowledge base operations including document processing and retrieval."""
    
    def __init__(self):
        """Initialize the knowledge base."""
        self.doc_processor = DocumentProcessor()
        self.retriever: Optional[VectorStoreRetriever] = None
    
    def setup_knowledge_base(self, context_dir: str) -> bool:
        """
        Set up the knowledge base from context directory.
        
        Args:
            context_dir: Path to the directory containing fitness documents
            
        Returns:
            True if knowledge base was set up successfully, False otherwise
        """
        print(f"📁 Context directory: {context_dir}")
        
        # Check if context directory exists and has files
        if not os.path.exists(context_dir):
            print(f"❌ Context directory not found: {context_dir}")
            return False
    
        files = os.listdir(context_dir)
        print(f"📄 Found {len(files)} files in context directory: {files}")

        vectorstore = self.doc_processor.setup_knowledge_base(context_dir)
        
        if vectorstore is None:
            print("❌ Failed to set up knowledge base. Running without context.")
            return False
        
        # Get retriever for document search - reduced k for faster retrieval
        self.retriever = self.doc_processor.get_retriever(vectorstore, k=2)
        
        try:
            chunk_count = vectorstore._collection.count()
            print(f"✅ Knowledge base ready with {chunk_count} chunks")
            
            # If we have 0 chunks, try to force refresh
            if chunk_count == 0:
                print("🔄 Detected empty knowledge base, forcing refresh...")
                self.doc_processor.clear_existing_vectorstore()
                vectorstore = self.doc_processor.setup_knowledge_base(context_dir, force_refresh=True)
                if vectorstore:
                    self.retriever = self.doc_processor.get_retriever(vectorstore, k=2)
                    chunk_count = vectorstore._collection.count()
                    print(f"✅ Refreshed knowledge base ready with {chunk_count} chunks")
        except Exception as e:
            print(f"⚠️ Could not get chunk count: {e}")
            print("✅ Knowledge base loaded (chunk count unavailable)")
        
        return True
    
    def get_retriever(self) -> Optional[VectorStoreRetriever]:
        """
        Get the current retriever.
        
        Returns:
            The vector store retriever if available, None otherwise
        """
        return self.retriever
    
    def has_knowledge_base(self) -> bool:
        """
        Check if knowledge base is available.
        
        Returns:
            True if knowledge base is set up, False otherwise
        """
        return self.retriever is not None
    
    def format_docs_with_sources(self, docs) -> tuple[str, List[str]]:
        """
        Format documents and extract source file information.
        
        Args:
            docs: List of documents to format
            
        Returns:
            Tuple of (formatted_docs_string, list_of_source_files)
        """
        referenced_files = []
        formatted_docs = []
        
        for doc in docs:
            if 'source' in doc.metadata:
                source_file = doc.metadata['source']
                if source_file not in referenced_files:
                    referenced_files.append(source_file)
            formatted_docs.append(doc.page_content)
        
        return "\n\n".join(formatted_docs), referenced_files
    
    def format_docs(self, docs) -> str:
        """
        Format documents for use in prompts.
        
        Args:
            docs: List of documents to format
            
        Returns:
            Formatted documents as a single string
        """
        return "\n\n".join(doc.page_content for doc in docs)

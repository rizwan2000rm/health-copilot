"""
AI Fitness Coach module.

This module contains the core AI coaching logic, including model initialization,
prompt templates, and response generation with document retrieval.
"""

import os
from typing import Optional, Dict, Any
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.vectorstores import VectorStoreRetriever
from document_processor import DocumentProcessor
from cache import ResponseCache


class FitnessCoach:
    """AI Fitness Coach that provides workout advice and guidance."""
    
    def __init__(self, model_name: str = "llama3.2:3b", cache_file: str = "response_cache.json"):
        """
        Initialize the AI Fitness Coach.
        
        Args:
            model_name: Name of the Ollama model to use
            cache_file: Path to the cache file for response caching
        """
        self.model_name = model_name
        self.model = OllamaLLM(model=model_name)
        self.cache = ResponseCache(cache_file)
        self.doc_processor = DocumentProcessor()
        self.retriever: Optional[VectorStoreRetriever] = None
        self.chain = None
        
        # Initialize the prompt template
        self._setup_prompt_template()
    
    def _setup_prompt_template(self) -> None:
        """Set up the prompt template for the AI coach."""
        self.template = """You are a minimalist fitness coach. Focus on evidence-based, time-efficient workouts (45-60 min, 2-3x/week).

PRINCIPLES: Compound movements, progressive overload, safety-first, sustainability.

RESEARCH CONTEXT: {context}

USER REQUEST: {input}

Provide a concise, practical workout solution with form cues and modifications. Use research context when relevant."""
        
        self.prompt = ChatPromptTemplate.from_template(self.template)
    
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
        
        # Set up the processing chain
        self._setup_chain()
        return True
    
    def _setup_chain(self) -> None:
        """Set up the processing chain based on whether retrieval is available."""
        if self.retriever:
            # Chain with retrieval
            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)
            
            self.chain = (
                {"context": self.retriever | format_docs, "input": RunnablePassthrough()}
                | self.prompt
                | self.model
                | StrOutputParser()
            )
        else:
            # Chain without retrieval
            self.chain = self.prompt | self.model | StrOutputParser()
    
    def get_response(self, user_input: str) -> str:
        """
        Get a response from the AI coach for the given input.
        
        Args:
            user_input: The user's question or request
            
        Returns:
            The AI coach's response
        """
        # Check cache first for faster response
        cached_response = self.cache.get(user_input)
        if cached_response:
            return cached_response
        
        # Get response from the model
        if self.retriever:
            response = self.chain.invoke(user_input)
        else:
            response = self.chain.invoke({"input": user_input})
        
        # Cache the response for future use
        self.cache.set(user_input, response)
        
        return response
    
    def get_cached_response(self, user_input: str) -> Optional[str]:
        """
        Get a cached response if available.
        
        Args:
            user_input: The user's question or request
            
        Returns:
            Cached response if available, None otherwise
        """
        return self.cache.get(user_input)
    
    def clear_cache(self) -> None:
        """Clear the response cache."""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary containing cache statistics
        """
        return {
            "cache_size": self.cache.size(),
            "cache_file": self.cache.cache_file,
            "model_name": self.model_name,
            "has_retriever": self.retriever is not None
        }

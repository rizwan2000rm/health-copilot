from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from document_processor import DocumentProcessor
import os
import threading
import time
import hashlib
import json

class ResponseCache:
    """Simple in-memory cache for responses"""
    def __init__(self, cache_file="response_cache.json"):
        self.cache_file = cache_file
        self.cache = self.load_cache()
    
    def load_cache(self):
        """Load cache from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)
        except Exception:
            pass
    
    def get_cache_key(self, query):
        """Generate cache key for query"""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()
    
    def get(self, query):
        """Get cached response"""
        key = self.get_cache_key(query)
        return self.cache.get(key)
    
    def set(self, query, response):
        """Cache response"""
        key = self.get_cache_key(query)
        self.cache[key] = response
        self.save_cache()

def show_loading():
    """Show a simple loading animation"""
    loading_chars = "|/-\\"
    i = 0
    while not hasattr(show_loading, 'stop'):
        print(f"\r🤖 AI Coach: Thinking {loading_chars[i % len(loading_chars)]}", end="", flush=True)
        time.sleep(0.1)
        i += 1

def main():
    # Initialize the Ollama model - using faster llama3.2:3b instead of gpt-oss
    model = OllamaLLM(model="llama3.2:3b")
    
    # Initialize response cache for faster repeated queries
    cache = ResponseCache()
    
    # Initialize document processor
    doc_processor = DocumentProcessor()
    
    # Set up knowledge base from context directory
    context_dir = os.path.join(os.path.dirname(__file__), "context")
    print(f"📁 Context directory: {context_dir}")
    
    # Check if context directory exists and has files
    if not os.path.exists(context_dir):
        print(f"❌ Context directory not found: {context_dir}")
        retriever = None
    else:
        files = os.listdir(context_dir)
        print(f"📄 Found {len(files)} files in context directory: {files}")
        
        vectorstore = doc_processor.setup_knowledge_base(context_dir)
        
        if vectorstore is None:
            print("❌ Failed to set up knowledge base. Running without context.")
            retriever = None
        else:
            # Get retriever for document search - reduced k for faster retrieval
            retriever = doc_processor.get_retriever(vectorstore, k=2)
            try:
                chunk_count = vectorstore._collection.count()
                print(f"✅ Knowledge base ready with {chunk_count} chunks")
                
                # If we have 0 chunks, try to force refresh
                if chunk_count == 0:
                    print("🔄 Detected empty knowledge base, forcing refresh...")
                    doc_processor.clear_existing_vectorstore()
                    vectorstore = doc_processor.setup_knowledge_base(context_dir, force_refresh=True)
                    if vectorstore:
                        retriever = doc_processor.get_retriever(vectorstore, k=2)
                        chunk_count = vectorstore._collection.count()
                        print(f"✅ Refreshed knowledge base ready with {chunk_count} chunks")
            except Exception as e:
                print(f"⚠️ Could not get chunk count: {e}")
                print("✅ Knowledge base loaded (chunk count unavailable)")
    
    # Create optimized prompt template for faster processing
    template = """You are a minimalist fitness coach. Focus on evidence-based, time-efficient workouts (45-60 min, 2-3x/week).

PRINCIPLES: Compound movements, progressive overload, safety-first, sustainability.

RESEARCH CONTEXT: {context}

USER REQUEST: {input}

Provide a concise, practical workout solution with form cues and modifications. Use research context when relevant."""

    prompt = ChatPromptTemplate.from_template(template)
    
    # Create the chain
    if retriever:
        # Chain with retrieval
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        chain = (
            {"context": retriever | format_docs, "input": RunnablePassthrough()}
            | prompt
            | model
            | StrOutputParser()
        )
    else:
        # Chain without retrieval
        chain = prompt | model | StrOutputParser()
    
    print("🏋️ Welcome to your AI Fitness Coach!")
    print("Ask me about workouts, exercises, or fitness advice. Type 'quit' to exit.\n")
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Check for exit command
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Thanks for using the AI Fitness Coach! Stay strong! 💪")
                break
            
            # Skip empty inputs
            if not user_input:
                continue
            
            # Check cache first for faster response
            cached_response = cache.get(user_input)
            if cached_response:
                print(f"⚡ AI Coach: {cached_response}")
                print("\n" + "="*50 + "\n")
                continue
            
            # Start loading animation
            loading_thread = threading.Thread(target=show_loading)
            loading_thread.daemon = True
            loading_thread.start()
            
            try:
                # Get response from the model
                if retriever:
                    response = chain.invoke(user_input)
                else:
                    response = chain.invoke({"input": user_input})
                
                # Cache the response for future use
                cache.set(user_input, response)
            finally:
                # Stop loading animation
                show_loading.stop = True
                loading_thread.join()
                print("\r🤖 AI Coach: ", end="", flush=True)
            
            # Print the response
            print(response)
            print("\n" + "="*50 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nThanks for using the AI Fitness Coach! Stay strong! 💪")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'quit' to exit.\n")

if __name__ == "__main__":
    main()
import os
import chromadb
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from typing import List

class DocumentProcessor:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize the document processor with ChromaDB."""
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Try to initialize embeddings with fallback
        try:
            self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
            print("✅ Using nomic-embed-text for embeddings")
        except Exception as e:
            print(f"❌ Failed to load nomic-embed-text: {e}")
            print("🔄 Falling back to alternative embedding model...")
            try:
                self.embeddings = OllamaEmbeddings(model="llama3.2:3b")
                print("✅ Using llama3.2:3b for embeddings")
            except Exception as e2:
                print(f"❌ Failed to load llama3.2:3b: {e2}")
                raise Exception("No suitable embedding model available. Please install an embedding model.")
        
        # Optimized text splitter for faster processing
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Smaller chunks for faster embedding
            chunk_overlap=200,  # Reduced overlap
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
    def load_documents_from_directory(self, directory_path: str) -> List[Document]:
        """Load all documents from a directory."""
        documents = []
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            if filename.endswith('.txt'):
                try:
                    loader = TextLoader(file_path, encoding='utf-8')
                    docs = loader.load()
                    # Add metadata to identify the source
                    for doc in docs:
                        doc.metadata['source'] = filename
                        doc.metadata['type'] = 'text'
                    documents.extend(docs)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
                    
            elif filename.endswith('.pdf'):
                try:
                    loader = PyPDFLoader(file_path)
                    docs = loader.load()
                    # Add metadata to identify the source
                    for doc in docs:
                        doc.metadata['source'] = filename
                        doc.metadata['type'] = 'pdf'
                    documents.extend(docs)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        return documents
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks."""
        print(f"📄 Chunking {len(documents)} documents...")
        chunked_docs = self.text_splitter.split_documents(documents)
        print(f"✂️ Created {len(chunked_docs)} chunks from {len(documents)} documents")
        
        # Show some statistics
        chunk_sizes = [len(chunk.page_content) for chunk in chunked_docs]
        if chunk_sizes:
            print(f"📊 Chunk size stats: min={min(chunk_sizes)}, max={max(chunk_sizes)}, avg={sum(chunk_sizes)//len(chunk_sizes)}")
        
        return chunked_docs
    
    def create_vectorstore(self, documents: List[Document], collection_name: str = "fitness_knowledge"):
        """Create a ChromaDB vectorstore from documents."""
        # Split documents into chunks
        chunked_docs = self.chunk_documents(documents)
        
        # Create ChromaDB vectorstore
        vectorstore = Chroma.from_documents(
            documents=chunked_docs,
            embedding=self.embeddings,
            collection_name=collection_name,
            persist_directory=self.persist_directory
        )
        
        return vectorstore
    
    def load_existing_vectorstore(self, collection_name: str = "fitness_knowledge"):
        """Load an existing ChromaDB vectorstore."""
        try:
            vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )
            return vectorstore
        except Exception as e:
            print(f"Error loading existing vectorstore: {e}")
            return None
    
    def get_retriever(self, vectorstore, k: int = 4):
        """Get a retriever from the vectorstore."""
        return vectorstore.as_retriever(search_kwargs={"k": k})
    
    def setup_knowledge_base(self, context_directory: str, force_refresh: bool = False):
        """Set up the complete knowledge base from context directory."""
        print("📚 Setting up fitness knowledge base...")
        
        # Check if vectorstore already exists (unless force refresh is requested)
        if not force_refresh:
            existing_vectorstore = self.load_existing_vectorstore()
            
            if existing_vectorstore is not None:
                try:
                    chunk_count = existing_vectorstore._collection.count()
                    if chunk_count > 0:
                        print(f"✅ Found existing knowledge base with {chunk_count} chunks, loading...")
                        return existing_vectorstore
                    else:
                        print("⚠️ Existing knowledge base is empty, recreating...")
                except Exception as e:
                    print(f"⚠️ Error checking existing vectorstore: {e}, recreating...")
        
        # Load documents from context directory
        print("📖 Loading documents from context directory...")
        documents = self.load_documents_from_directory(context_directory)
        
        if not documents:
            print("❌ No documents found in context directory")
            return None
        
        print(f"📄 Loaded {len(documents)} documents")
        
        # Create vectorstore
        print("🔧 Creating vectorstore...")
        vectorstore = self.create_vectorstore(documents)
        
        print("✅ Knowledge base setup complete!")
        return vectorstore
    
    def clear_existing_vectorstore(self, collection_name: str = "fitness_knowledge"):
        """Clear the existing vectorstore to force recreation."""
        try:
            # Delete the collection if it exists
            self.client.delete_collection(collection_name)
            print(f"🗑️ Cleared existing collection: {collection_name}")
        except Exception as e:
            print(f"ℹ️ No existing collection to clear: {e}")

import os
import time
import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter

os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'

class VectorEngine:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        model_path = os.path.join(base_dir, "data", "models", "bge-base-zh-v1.5")

        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_path, 
            model_kwargs={'device': 'cpu'}  , 
            encode_kwargs={'normalize_embeddings': True} 
        )

        persist_path = os.path.join(os.path.dirname(__file__), "../../data/chroma_db")
        self.chroma_client = chromadb.PersistentClient(path=persist_path)

        # 创建或获取集合
        self.collection_name = "policy_knowledge_base"
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"} # 使用余弦相似度
        )

    def _get_loader(self, file_path: str):
        ext = file_path.split(".")[-1].lower()
        if ext == "pdf":
            return PyPDFLoader(file_path)
        elif ext in ["docx", "doc"]:
            return Docx2txtLoader(file_path)
        elif ext in ["txt", "md"]:
            try:
                loader = TextLoader(file_path, encoding='utf-8')
                loader.load()
                return TextLoader(file_path, encoding='utf-8')
            except:
                return TextLoader(file_path, encoding='gbk')
        else:
            raise ValueError(f"不支持的文件格式: {ext}")

    def add_docs(self, texts, metadata, ids):
        embeddings = self.embeddings.embed_documents(texts)
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadata,
            ids=ids
        )

    def file_to_vector(self, file_path: str, chunk_size: int, chunk_overlap: int, strategy: str, doc_id: int, filename: str):
        start_time = time.time()
        
        loader = self._get_loader(file_path)
        raw_docs = loader.load()

        if strategy == "fixed":
            text_splitter = CharacterTextSplitter(
                separator="\n",
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
        else:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=["\n\n", "\n", "，", "。", "！", "？", " "]
            )
        chunks = text_splitter.split_documents(raw_docs)

        texts = [c.page_content for c in chunks]

        metadatas = [
            {"source": filename, "doc_id": doc_id, "page": c.metadata.get("page", 0)}
            for c in chunks
        ]
        ids = [f"doc_{doc_id}_chunk_{i}" for i in range(len(chunks))]

        if texts:
            self.add_docs(texts, metadatas, ids)

        end_time = time.time()
        print(f"文件 {filename} 转换为向量耗时: {end_time - start_time} 秒")
            
        return len(chunks)
    
    def search_knowledge(self, query: str, top_k: int = 3):
        query_vector = self.embeddings.embed_query(query)

        results = self.collection.query(
            query_embeddings=query_vector,
            n_results=top_k
        )

        retrieved_docs = []
        if results["documents"] and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                retrieved_docs.append({
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i]
                })
        return retrieved_docs
    
    def preview_doc_chunks(self, doc_id: int, limit: int = 10):
        results = self.collection.get(
            where={"doc_id": doc_id},
            limit=limit,
            include=["documents", "metadatas"]
        )
        return results
    
    def delete_vector_data(self, doc_id: int):
        """根据 ID 精确删除向量库中的所有分片"""
        # ChromaDB 支持 where 过滤删除
        self.collection.delete(where={"doc_id": doc_id})

engine = VectorEngine()
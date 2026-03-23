export default function ProjectCard() {
    return (
      <div className="glass p-6">
  
        <h2 className="text-xl font-bold mb-2">
          EnterpriseRAG AI
        </h2>
  
        <p className="text-gray-400 mb-4">
          Multi-tenant RAG platform processing 100K+ documents with low latency.
        </p>
  
        <div className="flex gap-2 flex-wrap">
          <span>FastAPI</span>
          <span>Redis</span>
          <span>FAISS</span>
          <span>RAG</span>
        </div>
  
      </div>
    );
  }
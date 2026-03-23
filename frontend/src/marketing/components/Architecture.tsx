export default function Architecture() {
    return (
      <div className="p-10 text-center">
  
        <h2 className="text-2xl font-bold mb-6">
          Distributed AI Architecture
        </h2>
  
        <div className="flex gap-4 justify-center flex-wrap">
          <div className="glass">Client</div>
          <div className="glass">API</div>
          <div className="glass">Redis</div>
          <div className="glass">Vector DB</div>
          <div className="glass">LLM</div>
        </div>
  
      </div>
    );
  }
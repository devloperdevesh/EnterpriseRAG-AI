export default function Loader() {
    return <div>Loading...</div>;
  }

  {loading ? <Loader /> : <Content />}
  export default function Loader() {
    return (
      <div className="animate-pulse p-4">
        <div className="h-4 bg-gray-700 rounded w-1/2 mb-2"></div>
        <div className="h-4 bg-gray-700 rounded w-1/3"></div>
      </div>
    );
  }
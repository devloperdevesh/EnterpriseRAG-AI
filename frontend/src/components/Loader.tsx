export default function Loader() {
    return <div>Loading...</div>;
  }

  {loading ? <Loader /> : <Content />}
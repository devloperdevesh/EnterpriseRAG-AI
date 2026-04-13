import { Link } from "react-router-dom";

export default function Navbar() {
  const isLoggedIn = !!localStorage.getItem("token");

  const logout = () => {
    localStorage.removeItem("token");
    window.location.href = "/login";
  };

  return (
    <div className="flex justify-between items-center px-8 py-4 bg-white shadow-md">

      {/* Logo + Name */}
      <div className="flex items-center gap-2">
        <img 
          src="/favicon.png" 
          alt="logo" 
          className="w-8 h-8"
        />
        <h1 className="font-bold text-xl">
          EnterpriseRAG
        </h1>
      </div>

      {/* Center Links */}
      <div className="flex gap-6 text-gray-700">
        <Link to="/">Home</Link>
        <Link to="/features">Features</Link>
        <Link to="/pricing">Pricing</Link>
        <Link to="/docs">Docs</Link>
      </div>

      {/* Right Side Auth */}
      <div className="flex gap-4 items-center">

        {!isLoggedIn ? (
          <>
            <Link to="/login" className="text-gray-600">
              Login
            </Link>

            <Link 
              to="/signup" 
              className="bg-blue-500 text-white px-4 py-2 rounded"
            >
              Sign Up
            </Link>
          </>
        ) : (
          <button 
            onClick={logout}
            className="bg-red-500 text-white px-4 py-2 rounded"
          >
            Logout
          </button>
        )}

      </div>

    </div>
  );
}
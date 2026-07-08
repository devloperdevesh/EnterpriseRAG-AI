import React from 'react';

export default function Topbar() {
  return (
    <div className="flex justify-between px-3.75 py-5 border-b border-white/10">
      <input className="w-200 ml-4 pl-4 bg-transparent rounded-lg border border-white/10 focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Search..." />
      <button className="w-35 bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded">New</button>
    </div>
  );
}
export default function Input({ placeholder, type = "text", onChange }: any) {
    return (
      <input
        type={type}
        placeholder={placeholder}
        onChange={onChange}
        className="
          w-full px-4 py-3 rounded-xl
          bg-[#121212] border border-[#1F2933]
          text-[rgba(224,224,224,0.87)]
          placeholder:text-[rgba(176,176,176,0.6)]
          focus:outline-none focus:ring-2 focus:ring-purple-600
        "
      />
    );
  }
  
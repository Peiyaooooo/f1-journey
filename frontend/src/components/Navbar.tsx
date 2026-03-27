// frontend/src/components/Navbar.tsx
import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="flex items-center justify-between px-6 py-3 border-b border-gray-800 bg-gray-950">
      <div className="flex items-center gap-8">
        <Link href="/" className="text-lg font-bold text-red-500">
          F1 Journey
        </Link>
        <Link href="/explore" className="text-sm text-gray-400 hover:text-white">Explore</Link>
        <Link href="/quiz" className="text-sm text-gray-400 hover:text-white">Quiz</Link>
        <Link href="/compare" className="text-sm text-gray-400 hover:text-white">Compare</Link>
      </div>
      <div className="flex items-center gap-3">
        <input
          type="text"
          placeholder="Search tracks..."
          className="bg-gray-800 text-sm text-gray-300 px-3 py-1.5 rounded-md w-48 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-600"
          readOnly
        />
      </div>
    </nav>
  );
}

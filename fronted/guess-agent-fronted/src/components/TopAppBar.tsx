import { Menu } from "lucide-react";

export default function TopAppBar() {
  return (
    <header className="fixed top-0 w-full z-50 bg-surface/80 backdrop-blur-xl bg-gradient-to-b from-surface to-transparent">
      <div className="flex justify-center items-center px-6 py-4 w-full max-w-screen-xl mx-auto">
        <h1 className="text-xl font-black text-primary tracking-[0.2em] font-headline">
          Guess Agent
        </h1>
        {/* <button className="hover:opacity-80 transition-opacity active:scale-95 duration-200">
          <Menu className="w-6 h-6 text-primary" />
        </button>
        <h1 className="text-xl font-black text-primary tracking-[0.2em] font-headline">HUNCH</h1> */}
      </div>
    </header>
  );
}

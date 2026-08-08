import { NavLink } from "react-router-dom";

const linkClass = ({ isActive }: { isActive: boolean }) =>
  `px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
    isActive ? "bg-white/10 text-white" : "text-[#b2b6ca] hover:text-white"
  }`;

export default function Nav() {
  return (
    <div className="fixed top-0 left-0 right-0 z-50 px-4 sm:px-6 pt-4">
      <nav className="max-w-5xl mx-auto glass rounded-2xl px-4 py-3 flex items-center justify-between">
        <span className="font-semibold tracking-tight">Janmat Pulse</span>
        <div className="flex items-center gap-1">
          <NavLink to="/" end className={linkClass}>
            Dashboard
          </NavLink>
          <NavLink to="/manifestos" className={linkClass}>
            Manifesto Chat
          </NavLink>
        </div>
        <a
          href="https://github.com/dev21382/public-opinion-aggregator"
          target="_blank"
          rel="noreferrer"
          className="hidden sm:block text-xs font-mono uppercase tracking-wider text-[#9397ab] hover:text-white"
        >
          Source
        </a>
      </nav>
    </div>
  );
}

import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  MessageSquare,
  FileText,
  BarChart3,
  CreditCard,
  Settings,
  Activity,
  Database,
} from "lucide-react";

export default function Sidebar() {
  const navItems = [
    {
      section: "OVERVIEW",
      items: [
        {
          path: "/dashboard",
          label: "Dashboard",
          icon: <LayoutDashboard size={18} />,
        },
      ],
    },
    {
      section: "AI WORKFLOWS",
      items: [
        {
          path: "/chat",
          label: "Chat",
          icon: <MessageSquare size={18} />,
        },
        {
          path: "/documents",
          label: "Documents",
          icon: <FileText size={18} />,
        },
      ],
    },
    {
      section: "OBSERVABILITY",
      items: [
        {
          path: "/analytics",
          label: "Analytics",
          icon: <BarChart3 size={18} />,
        },
      ],
    },
    {
      section: "ADMIN",
      items: [
        {
          path: "/billing",
          label: "Billing",
          icon: <CreditCard size={18} />,
        },
        {
          path: "/settings",
          label: "Settings",
          icon: <Settings size={18} />,
        },
      ],
    },
  ];

  return (
    <aside className="w-72 min-h-screen border-r border-white/10 bg-zinc-950 text-white flex flex-col">
      
      {/* Logo */}
      <div className="p-6 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-400 to-blue-600 shadow-lg shadow-cyan-500/20">
            <Database size={20} />
          </div>

          <div>
            <h1 className="text-lg font-bold tracking-wide">
              EnterpriseRAG
            </h1>
            <p className="text-xs text-zinc-400">
              AI Infrastructure Console
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 p-4">
        {navItems.map((group) => (
          <div key={group.section} className="mb-8">
            <p className="mb-3 px-3 text-xs font-semibold tracking-widest text-zinc-500">
              {group.section}
            </p>

            <div className="space-y-1">
              {group.items.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `
                    group flex items-center gap-3 rounded-xl px-4 py-3
                    transition-all duration-200
                    ${
                      isActive
                        ? "bg-cyan-500/10 text-cyan-300 border-l-4 border-cyan-400 shadow-lg shadow-cyan-500/10"
                        : "text-zinc-400 hover:bg-white/5 hover:text-white"
                    }
                    `
                  }
                >
                  {item.icon}
                  <span>{item.label}</span>
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="border-t border-white/10 p-4">
        <div className="rounded-xl bg-white/5 p-4">
          <div className="flex items-center gap-2 mb-2">
            <Activity size={16} className="text-emerald-400" />
            <span className="text-sm font-medium text-emerald-400">
              Connected
            </span>
          </div>

          <p className="text-xs text-zinc-400">
            Workspace
          </p>

          <p className="text-sm font-medium">
            enterprise-demo
          </p>
        </div>
      </div>
    </aside>
  );
}
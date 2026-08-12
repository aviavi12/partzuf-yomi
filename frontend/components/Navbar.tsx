"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/", label: "דשבורד", icon: "📊" },
  { href: "/synthesis", label: "סיכום יומי", icon: "📋" },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <nav
      className="border-b px-4 py-3"
      style={{ background: "var(--card)", borderColor: "var(--border)" }}
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-xl">🧬</span>
          <span className="font-bold text-lg">פרצוף יומי</span>
        </Link>
        <div className="flex items-center gap-1">
          {NAV_ITEMS.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
                style={{
                  background: active ? "var(--accent)" : "transparent",
                  color: active ? "var(--accent-foreground)" : "var(--muted-foreground)",
                }}
              >
                {item.icon} {item.label}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}

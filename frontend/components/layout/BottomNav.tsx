"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  MessageCircle,
  Headphones,
  Mic,
  RotateCcw,
} from "lucide-react";

/** モバイル用ナビゲーションリンク定義 */
const navLinks = [
  { href: "/", label: "Home", icon: LayoutDashboard },
  { href: "/talk", label: "Talk", icon: MessageCircle },
  { href: "/listening", label: "Listen", icon: Headphones },
  { href: "/speaking", label: "Speak", icon: Mic },
  { href: "/review", label: "Review", icon: RotateCcw },
];

/**
 * モバイルボトムナビゲーションバー
 * md未満の画面で表示
 */
export default function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-[var(--color-bg-secondary)] border-t border-[var(--color-border)] safe-area-bottom">
      <div className="flex items-center justify-around h-16">
        {navLinks.map((link) => {
          const isActive = pathname === link.href;
          const Icon = link.icon;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`flex flex-col items-center justify-center gap-1 px-3 py-2 transition-colors ${
                isActive
                  ? "text-primary"
                  : "text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]"
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="text-[10px] font-medium">{link.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}

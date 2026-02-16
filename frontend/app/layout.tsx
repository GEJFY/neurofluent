import type { Metadata, Viewport } from "next";
import "./globals.css";
import ToastContainer from "@/components/ui/Toast";

/**
 * FluentEdge AI - ルートレイアウト
 * ダークモードデフォルト、Google Fonts読み込み
 */
export const metadata: Metadata = {
  title: "FluentEdge AI - 英語トレーニング",
  description:
    "AIを活用したパーソナライズド英語トレーニングアプリ。Free Talk、Flash Translation、Spaced Repetitionで英語力を高めよう。",
  manifest: "/manifest.json",
  icons: {
    icon: "/favicon.ico",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  themeColor: "#0F172A",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja" className="dark">
      <body className="font-body antialiased bg-[var(--color-bg-primary)] text-[var(--color-text-primary)]">
        {children}
        <ToastContainer />
      </body>
    </html>
  );
}

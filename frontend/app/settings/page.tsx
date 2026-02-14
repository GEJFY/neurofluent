"use client";

import { useState } from "react";
import {
  User,
  BookOpen,
  Palette,
  Volume2,
  Shield,
  Info,
  ChevronRight,
  Save,
  Moon,
  Sun,
  AlertTriangle,
  ExternalLink,
} from "lucide-react";
import AppShell from "@/components/layout/AppShell";

/**
 * 設定ページ
 * プロフィール / 学習 / テーマ / 音声 / アカウント / About
 */

type SettingsSection =
  | "profile"
  | "learning"
  | "theme"
  | "audio"
  | "account"
  | "about";

interface SectionItem {
  id: SettingsSection;
  label: string;
  labelJa: string;
  icon: React.ElementType;
}

const SECTIONS: SectionItem[] = [
  { id: "profile", label: "Profile", labelJa: "プロフィール", icon: User },
  { id: "learning", label: "Learning", labelJa: "学習設定", icon: BookOpen },
  { id: "theme", label: "Theme", labelJa: "テーマ", icon: Palette },
  { id: "audio", label: "Audio", labelJa: "音声設定", icon: Volume2 },
  { id: "account", label: "Account", labelJa: "アカウント", icon: Shield },
  { id: "about", label: "About", labelJa: "アプリについて", icon: Info },
];

const TARGET_LEVELS = ["B1", "B2", "C1", "C2"];
const DAILY_GOALS = [5, 10, 15, 30, 60];
const VOICE_OPTIONS = [
  { id: "alloy", name: "Alloy", description: "ニュートラルなトーン" },
  { id: "echo", name: "Echo", description: "落ち着いた男性声" },
  { id: "nova", name: "Nova", description: "明るい女性声" },
  { id: "shimmer", name: "Shimmer", description: "柔らかい女性声" },
];
const PLAYBACK_SPEEDS = [0.75, 1.0, 1.25, 1.5, 2.0];

export default function SettingsPage() {
  const [activeSection, setActiveSection] =
    useState<SettingsSection>("profile");
  const [isSaving, setIsSaving] = useState(false);
  const [showSaved, setShowSaved] = useState(false);

  // プロフィール
  const [name, setName] = useState("User");
  const [email] = useState("user@example.com");
  const [targetLevel, setTargetLevel] = useState("B2");
  const [nativeLanguage, setNativeLanguage] = useState("Japanese");

  // 学習設定
  const [dailyGoal, setDailyGoal] = useState(15);
  const [notifyReminder, setNotifyReminder] = useState(true);
  const [notifyWeekly, setNotifyWeekly] = useState(true);
  const [notifyAchievements, setNotifyAchievements] = useState(true);

  // テーマ
  const [theme, setTheme] = useState<"dark" | "light">("dark");

  // 音声
  const [selectedVoice, setSelectedVoice] = useState("alloy");
  const [playbackSpeed, setPlaybackSpeed] = useState(1.0);

  // アカウント
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // 保存
  const handleSave = async () => {
    setIsSaving(true);
    // デモ：1秒後に保存完了
    setTimeout(() => {
      setIsSaving(false);
      setShowSaved(true);
      setTimeout(() => setShowSaved(false), 2000);
    }, 1000);
  };

  return (
    <AppShell>
      <div className="space-y-6">
        {/* ヘッダー */}
        <div className="space-y-1">
          <h1 className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
            Settings
          </h1>
          <p className="text-sm text-[var(--color-text-muted)]">
            アプリの設定をカスタマイズ
          </p>
        </div>

        <div className="flex flex-col md:flex-row gap-4">
          {/* セクションナビ */}
          <div className="md:w-56 shrink-0">
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-2 space-y-1">
              {SECTIONS.map((section) => {
                const Icon = section.icon;
                return (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-colors ${
                      activeSection === section.id
                        ? "bg-primary/10 text-primary font-medium"
                        : "text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-primary)]/50"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="flex-1 text-left">{section.label}</span>
                    <ChevronRight className="w-3.5 h-3.5 opacity-40" />
                  </button>
                );
              })}
            </div>
          </div>

          {/* コンテンツエリア */}
          <div className="flex-1 min-w-0">
            {/* Profile セクション */}
            {activeSection === "profile" && (
              <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-5">
                <p className="text-sm font-semibold text-[var(--color-text-primary)]">
                  Profile Settings
                </p>

                {/* 名前 */}
                <div className="space-y-1.5">
                  <label className="text-xs text-[var(--color-text-muted)]">
                    Name
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl bg-[var(--color-bg-input)] border border-[var(--color-border)] text-[var(--color-text-primary)] text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
                  />
                </div>

                {/* メール（読み取り専用） */}
                <div className="space-y-1.5">
                  <label className="text-xs text-[var(--color-text-muted)]">
                    Email
                  </label>
                  <input
                    type="email"
                    value={email}
                    readOnly
                    className="w-full px-4 py-2.5 rounded-xl bg-[var(--color-bg-input)] border border-[var(--color-border)] text-[var(--color-text-muted)] text-sm cursor-not-allowed"
                  />
                </div>

                {/* ターゲットレベル */}
                <div className="space-y-1.5">
                  <label className="text-xs text-[var(--color-text-muted)]">
                    Target Level
                  </label>
                  <div className="flex gap-2">
                    {TARGET_LEVELS.map((level) => (
                      <button
                        key={level}
                        onClick={() => setTargetLevel(level)}
                        className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors border ${
                          targetLevel === level
                            ? "bg-primary/10 border-primary text-primary"
                            : "bg-[var(--color-bg-input)] border-[var(--color-border)] text-[var(--color-text-secondary)] hover:border-primary/30"
                        }`}
                      >
                        {level}
                      </button>
                    ))}
                  </div>
                </div>

                {/* 母国語 */}
                <div className="space-y-1.5">
                  <label className="text-xs text-[var(--color-text-muted)]">
                    Native Language
                  </label>
                  <select
                    value={nativeLanguage}
                    onChange={(e) => setNativeLanguage(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl bg-[var(--color-bg-input)] border border-[var(--color-border)] text-[var(--color-text-primary)] text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
                  >
                    <option value="Japanese">Japanese (日本語)</option>
                    <option value="Chinese">Chinese (中文)</option>
                    <option value="Korean">Korean (한국어)</option>
                    <option value="Spanish">Spanish (Español)</option>
                    <option value="Portuguese">Portuguese (Português)</option>
                  </select>
                </div>

                <button
                  onClick={handleSave}
                  disabled={isSaving}
                  className="px-6 py-2.5 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 disabled:opacity-50 transition-colors flex items-center gap-2"
                >
                  <Save className="w-4 h-4" />
                  {isSaving ? "Saving..." : "Save Changes"}
                </button>

                {showSaved && (
                  <p className="text-xs text-green-400">
                    Settings saved successfully
                  </p>
                )}
              </div>
            )}

            {/* Learning セクション */}
            {activeSection === "learning" && (
              <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-5">
                <p className="text-sm font-semibold text-[var(--color-text-primary)]">
                  Learning Preferences
                </p>

                {/* 日次目標 */}
                <div className="space-y-1.5">
                  <label className="text-xs text-[var(--color-text-muted)]">
                    Daily Goal (minutes)
                  </label>
                  <div className="flex gap-2 flex-wrap">
                    {DAILY_GOALS.map((goal) => (
                      <button
                        key={goal}
                        onClick={() => setDailyGoal(goal)}
                        className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors border ${
                          dailyGoal === goal
                            ? "bg-primary/10 border-primary text-primary"
                            : "bg-[var(--color-bg-input)] border-[var(--color-border)] text-[var(--color-text-secondary)] hover:border-primary/30"
                        }`}
                      >
                        {goal} min
                      </button>
                    ))}
                  </div>
                  <p className="text-[11px] text-[var(--color-text-muted)]">
                    1日の学習目標時間を設定します
                  </p>
                </div>

                {/* 通知設定 */}
                <div className="space-y-3">
                  <label className="text-xs text-[var(--color-text-muted)]">
                    Notifications
                  </label>
                  {[
                    {
                      key: "reminder",
                      label: "Daily Reminder",
                      desc: "毎日の学習リマインダー",
                      checked: notifyReminder,
                      onChange: setNotifyReminder,
                    },
                    {
                      key: "weekly",
                      label: "Weekly Report",
                      desc: "週次レポート通知",
                      checked: notifyWeekly,
                      onChange: setNotifyWeekly,
                    },
                    {
                      key: "achievements",
                      label: "Achievements",
                      desc: "達成バッジ通知",
                      checked: notifyAchievements,
                      onChange: setNotifyAchievements,
                    },
                  ].map((item) => (
                    <div
                      key={item.key}
                      className="flex items-center justify-between p-3 rounded-xl bg-[var(--color-bg-primary)]/50"
                    >
                      <div>
                        <p className="text-sm text-[var(--color-text-primary)]">
                          {item.label}
                        </p>
                        <p className="text-[11px] text-[var(--color-text-muted)]">
                          {item.desc}
                        </p>
                      </div>
                      <button
                        onClick={() => item.onChange(!item.checked)}
                        className={`w-11 h-6 rounded-full transition-colors relative ${
                          item.checked
                            ? "bg-primary"
                            : "bg-[var(--color-bg-input)]"
                        }`}
                      >
                        <div
                          className={`w-5 h-5 rounded-full bg-white absolute top-0.5 transition-transform ${
                            item.checked
                              ? "translate-x-[22px]"
                              : "translate-x-0.5"
                          }`}
                        />
                      </button>
                    </div>
                  ))}
                </div>

                <button
                  onClick={handleSave}
                  disabled={isSaving}
                  className="px-6 py-2.5 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 disabled:opacity-50 transition-colors flex items-center gap-2"
                >
                  <Save className="w-4 h-4" />
                  {isSaving ? "Saving..." : "Save Changes"}
                </button>
              </div>
            )}

            {/* Theme セクション */}
            {activeSection === "theme" && (
              <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-5">
                <p className="text-sm font-semibold text-[var(--color-text-primary)]">
                  Theme Settings
                </p>

                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={() => setTheme("dark")}
                    className={`p-4 rounded-xl border transition-colors text-center ${
                      theme === "dark"
                        ? "border-primary bg-primary/5"
                        : "border-[var(--color-border)] hover:border-primary/30"
                    }`}
                  >
                    <Moon
                      className={`w-8 h-8 mx-auto mb-2 ${
                        theme === "dark"
                          ? "text-primary"
                          : "text-[var(--color-text-muted)]"
                      }`}
                    />
                    <p className="text-sm font-medium text-[var(--color-text-primary)]">
                      Dark
                    </p>
                    <p className="text-[11px] text-[var(--color-text-muted)]">
                      ダークモード
                    </p>
                  </button>
                  <button
                    onClick={() => setTheme("light")}
                    className={`p-4 rounded-xl border transition-colors text-center ${
                      theme === "light"
                        ? "border-primary bg-primary/5"
                        : "border-[var(--color-border)] hover:border-primary/30"
                    }`}
                  >
                    <Sun
                      className={`w-8 h-8 mx-auto mb-2 ${
                        theme === "light"
                          ? "text-primary"
                          : "text-[var(--color-text-muted)]"
                      }`}
                    />
                    <p className="text-sm font-medium text-[var(--color-text-primary)]">
                      Light
                    </p>
                    <p className="text-[11px] text-[var(--color-text-muted)]">
                      ライトモード
                    </p>
                  </button>
                </div>
              </div>
            )}

            {/* Audio セクション */}
            {activeSection === "audio" && (
              <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-5">
                <p className="text-sm font-semibold text-[var(--color-text-primary)]">
                  Audio Settings
                </p>

                {/* 音声選択 */}
                <div className="space-y-1.5">
                  <label className="text-xs text-[var(--color-text-muted)]">
                    TTS Voice
                  </label>
                  <div className="space-y-2">
                    {VOICE_OPTIONS.map((voice) => (
                      <button
                        key={voice.id}
                        onClick={() => setSelectedVoice(voice.id)}
                        className={`w-full flex items-center gap-3 p-3 rounded-xl border text-left transition-colors ${
                          selectedVoice === voice.id
                            ? "border-primary bg-primary/5"
                            : "border-[var(--color-border)] hover:border-primary/30"
                        }`}
                      >
                        <div
                          className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                            selectedVoice === voice.id
                              ? "border-primary"
                              : "border-[var(--color-text-muted)]"
                          }`}
                        >
                          {selectedVoice === voice.id && (
                            <div className="w-2 h-2 rounded-full bg-primary" />
                          )}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-[var(--color-text-primary)]">
                            {voice.name}
                          </p>
                          <p className="text-[11px] text-[var(--color-text-muted)]">
                            {voice.description}
                          </p>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* 再生速度 */}
                <div className="space-y-1.5">
                  <label className="text-xs text-[var(--color-text-muted)]">
                    Default Playback Speed
                  </label>
                  <div className="flex gap-2 flex-wrap">
                    {PLAYBACK_SPEEDS.map((speed) => (
                      <button
                        key={speed}
                        onClick={() => setPlaybackSpeed(speed)}
                        className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors border ${
                          playbackSpeed === speed
                            ? "bg-primary/10 border-primary text-primary"
                            : "bg-[var(--color-bg-input)] border-[var(--color-border)] text-[var(--color-text-secondary)] hover:border-primary/30"
                        }`}
                      >
                        {speed}x
                      </button>
                    ))}
                  </div>
                </div>

                <button
                  onClick={handleSave}
                  disabled={isSaving}
                  className="px-6 py-2.5 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 disabled:opacity-50 transition-colors flex items-center gap-2"
                >
                  <Save className="w-4 h-4" />
                  {isSaving ? "Saving..." : "Save Changes"}
                </button>
              </div>
            )}

            {/* Account セクション */}
            {activeSection === "account" && (
              <div className="space-y-4">
                {/* パスワード変更 */}
                <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-4">
                  <p className="text-sm font-semibold text-[var(--color-text-primary)]">
                    Change Password
                  </p>
                  <div className="space-y-3">
                    <div className="space-y-1.5">
                      <label className="text-xs text-[var(--color-text-muted)]">
                        Current Password
                      </label>
                      <input
                        type="password"
                        placeholder="Enter current password"
                        className="w-full px-4 py-2.5 rounded-xl bg-[var(--color-bg-input)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-xs text-[var(--color-text-muted)]">
                        New Password
                      </label>
                      <input
                        type="password"
                        placeholder="Enter new password"
                        className="w-full px-4 py-2.5 rounded-xl bg-[var(--color-bg-input)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-xs text-[var(--color-text-muted)]">
                        Confirm New Password
                      </label>
                      <input
                        type="password"
                        placeholder="Confirm new password"
                        className="w-full px-4 py-2.5 rounded-xl bg-[var(--color-bg-input)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
                      />
                    </div>
                    <button className="px-6 py-2.5 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 transition-colors">
                      Update Password
                    </button>
                  </div>
                </div>

                {/* Danger Zone */}
                <div className="bg-[var(--color-bg-card)] border border-red-500/20 rounded-2xl p-5 space-y-4">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-red-400" />
                    <p className="text-sm font-semibold text-red-400">
                      Danger Zone
                    </p>
                  </div>
                  <p className="text-xs text-[var(--color-text-secondary)]">
                    アカウントを削除すると、すべてのデータが完全に削除されます。この操作は取り消せません。
                  </p>
                  {!showDeleteConfirm ? (
                    <button
                      onClick={() => setShowDeleteConfirm(true)}
                      className="px-6 py-2.5 rounded-xl border border-red-500/30 text-red-400 text-sm font-semibold hover:bg-red-500/10 transition-colors"
                    >
                      Delete Account
                    </button>
                  ) : (
                    <div className="p-4 rounded-xl bg-red-500/5 border border-red-500/20 space-y-3">
                      <p className="text-xs text-red-400 font-semibold">
                        Are you sure? This action cannot be undone.
                      </p>
                      <div className="flex gap-2">
                        <button className="px-4 py-2 rounded-xl bg-red-500 text-white text-xs font-semibold hover:bg-red-600 transition-colors">
                          Yes, Delete My Account
                        </button>
                        <button
                          onClick={() => setShowDeleteConfirm(false)}
                          className="px-4 py-2 rounded-xl bg-[var(--color-bg-input)] border border-[var(--color-border)] text-[var(--color-text-secondary)] text-xs font-medium hover:border-primary/30 transition-colors"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* About セクション */}
            {activeSection === "about" && (
              <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-5">
                <p className="text-sm font-semibold text-[var(--color-text-primary)]">
                  About FluentEdge AI
                </p>

                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 rounded-xl bg-[var(--color-bg-primary)]/50">
                    <span className="text-sm text-[var(--color-text-secondary)]">
                      Version
                    </span>
                    <span className="text-sm font-mono text-[var(--color-text-primary)]">
                      1.0.0-beta
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-xl bg-[var(--color-bg-primary)]/50">
                    <span className="text-sm text-[var(--color-text-secondary)]">
                      Build
                    </span>
                    <span className="text-sm font-mono text-[var(--color-text-primary)]">
                      2026.02.14
                    </span>
                  </div>
                </div>

                <div className="space-y-2">
                  {[
                    { label: "Privacy Policy", href: "#" },
                    { label: "Terms of Service", href: "#" },
                    { label: "License Information", href: "#" },
                  ].map((link) => (
                    <a
                      key={link.label}
                      href={link.href}
                      className="flex items-center justify-between p-3 rounded-xl bg-[var(--color-bg-primary)]/50 hover:bg-[var(--color-bg-primary)] transition-colors group"
                    >
                      <span className="text-sm text-[var(--color-text-secondary)]">
                        {link.label}
                      </span>
                      <ExternalLink className="w-3.5 h-3.5 text-[var(--color-text-muted)] group-hover:text-primary transition-colors" />
                    </a>
                  ))}
                </div>

                <div className="text-center pt-4 border-t border-[var(--color-border)]">
                  <p className="text-xs text-[var(--color-text-muted)]">
                    FluentEdge AI - Powered by Advanced Language Models
                  </p>
                  <p className="text-[10px] text-[var(--color-text-muted)] mt-1">
                    &copy; 2026 FluentEdge AI. All rights reserved.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}

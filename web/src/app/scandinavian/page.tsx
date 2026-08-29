"use client";

import { useState } from "react";
import { LayoutDashboard, FileText, Settings, CreditCard, Activity, ArrowUpRight, CheckCircle2 } from "lucide-react";

type ThemeType = "quiet" | "editorial" | "utilitarian";

export default function ScandinavianPrototype() {
  const [theme, setTheme] = useState<ThemeType>("quiet");

  // Scandinavian Harness Modes
  // Overriding any globals with specific arbitrary values per the skill's instructions.
  const themes = {
    quiet: {
      name: "Quiet",
      desc: "Default minimal. Pure neutrals, standard sans-serif, restrained borders.",
      bg: "bg-[#FFFFFF] dark:bg-[#0A0A0A]",
      textPrimary: "text-black dark:text-white",
      textSecondary: "text-black/64 dark:text-white/56",
      textTertiary: "text-black/44 dark:text-white/36",
      border: "border-black/10 dark:border-white/10",
      surface: "bg-[#FFFFFF] dark:bg-[#0A0A0A]",
      fillHover: "hover:bg-black/5 dark:hover:bg-white/9",
      accent: "bg-black text-white dark:bg-white dark:text-black",
      font: "font-sans",
      spacing: "gap-8",
      card: "border border-black/10 dark:border-white/10 rounded-lg p-6",
      divider: "border-b border-black/10 dark:border-white/10",
    },
    editorial: {
      name: "Editorial",
      desc: "Publication style. Heavy structural rules, serif typography, high contrast.",
      bg: "bg-[#FFFFFF] dark:bg-[#0A0A0A]",
      textPrimary: "text-black dark:text-white",
      textSecondary: "text-black/75 dark:text-white/70",
      textTertiary: "text-black/50 dark:text-white/50",
      border: "border-black dark:border-white", // Stronger borders
      surface: "bg-[#F9F9F9] dark:bg-[#111111]",
      fillHover: "hover:bg-black/5 dark:hover:bg-white/10",
      accent: "bg-black text-white dark:bg-white dark:text-black",
      font: "font-serif",
      spacing: "gap-12",
      card: "border-t-2 border-black dark:border-white pt-4", // Thick top rules instead of boxes
      divider: "border-b border-black/20 dark:border-white/20",
    },
    utilitarian: {
      name: "Utilitarian",
      desc: "Dense operational interface. Monospaced elements, one functional color.",
      bg: "bg-[#F5F5F5] dark:bg-[#121212]",
      textPrimary: "text-black dark:text-white",
      textSecondary: "text-black/70 dark:text-white/60",
      textTertiary: "text-black/50 dark:text-white/40",
      border: "border-black/20 dark:border-white/20",
      surface: "bg-white dark:bg-[#1A1A1A]",
      fillHover: "hover:bg-black/10 dark:hover:bg-white/15",
      accent: "bg-blue-600 text-white dark:bg-blue-500 dark:text-white", // Single functional color
      font: "font-mono",
      spacing: "gap-4",
      card: "border border-black/20 dark:border-white/20 p-4 rounded-sm",
      divider: "border-b border-black/20 dark:border-white/20 border-dashed",
    }
  };

  const t = themes[theme];

  return (
    <div className={`min-h-screen w-full transition-colors duration-200 ${t.bg} ${t.textPrimary} ${t.font} !font-normal`}>
      {/* Switcher Header */}
      <div className={`fixed top-0 left-0 right-0 z-50 px-6 py-4 flex items-center justify-between ${t.surface} ${t.divider}`}>
        <div className="flex items-center gap-4">
          <span className="text-sm font-semibold tracking-wide uppercase">Prototype Modes</span>
          <div className="flex gap-2 bg-black/5 dark:bg-white/5 p-1 rounded-md">
            {(Object.keys(themes) as ThemeType[]).map((key) => (
              <button
                key={key}
                onClick={() => setTheme(key)}
                className={`px-4 py-1.5 text-xs font-medium transition-colors rounded ${
                  theme === key ? t.accent : `bg-transparent ${t.textSecondary} ${t.fillHover}`
                }`}
              >
                {themes[key].name}
              </button>
            ))}
          </div>
        </div>
        <div className="text-xs uppercase tracking-widest font-bold">Scandinavian Design Harness</div>
      </div>

      {/* Main Content Layout */}
      <div className="flex pt-[74px] min-h-screen">
        {/* Sidebar */}
        <div className={`w-[260px] h-[calc(100vh-74px)] sticky top-[74px] hidden lg:flex flex-col py-8 px-6 ${t.border} border-r`}>
          <div className={`text-xs uppercase tracking-widest font-semibold mb-6 ${t.textTertiary}`}>Menu</div>
          <div className="flex flex-col gap-2">
            {[
              { label: "Dashboard", icon: LayoutDashboard, active: true },
              { label: "Finance", icon: CreditCard, active: false },
              { label: "Activity Logs", icon: Activity, active: false },
              { label: "Settings", icon: Settings, active: false }
            ].map((item, idx) => (
              <button key={idx} className={`flex items-center gap-3 px-3 py-2.5 text-sm w-full text-left rounded-sm ${item.active ? `${t.bg} font-medium ${t.border} border shadow-sm` : `border border-transparent ${t.textSecondary} ${t.fillHover}`}`}>
                <item.icon className="w-4 h-4 opacity-80" />
                {item.label}
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 p-8 lg:p-16 max-w-5xl mx-auto">
          <header className="mb-16">
            <h1 className="text-4xl lg:text-5xl font-light tracking-tight mb-4">Overview</h1>
            <p className={`text-lg ${t.textSecondary} max-w-2xl`}>
              {t.desc}
            </p>
          </header>

          {/* Stats */}
          <section className="mb-16">
            <div className={`text-xs uppercase tracking-widest font-semibold mb-6 ${t.textTertiary}`}>Metrics</div>
            <div className={`grid grid-cols-1 md:grid-cols-3 ${t.spacing}`}>
              {[
                { label: "Total Balance", value: "Rp 12,500,000", trend: "+2.4%" },
                { label: "Monthly Expenses", value: "Rp 3,200,000", trend: "-5.1%" },
                { label: "Active Subscriptions", value: "4", trend: "0%" }
              ].map((stat, idx) => (
                <div key={idx} className={`${t.surface} ${t.card} flex flex-col`}>
                  <span className={`text-sm mb-4 ${t.textSecondary}`}>{stat.label}</span>
                  <span className="text-3xl font-light mb-2">{stat.value}</span>
                  <span className={`text-sm flex items-center gap-1 ${stat.trend.startsWith('+') ? 'text-black dark:text-white' : t.textSecondary}`}>
                    <ArrowUpRight className="w-3 h-3" /> {stat.trend} from last month
                  </span>
                </div>
              ))}
            </div>
          </section>

          {/* Table / List */}
          <section>
            <div className={`text-xs uppercase tracking-widest font-semibold mb-6 ${t.textTertiary}`}>Recent Transactions</div>
            <div className="w-full">
              {[
                { name: "Supermarket Shopping", date: "Today, 10:00 AM", amount: "-Rp 450,000", status: "Completed" },
                { name: "Internet Bill", date: "Yesterday, 14:30 PM", amount: "-Rp 350,000", status: "Completed" },
                { name: "Salary Deposit", date: "Oct 25, 08:00 AM", amount: "+Rp 15,000,000", status: "Completed" }
              ].map((item, idx) => (
                <div key={idx} className={`flex items-center justify-between py-4 ${t.divider}`}>
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 flex items-center justify-center rounded-full ${t.bg} ${t.border} border`}>
                      <CheckCircle2 className={`w-4 h-4 ${t.textSecondary}`} />
                    </div>
                    <div>
                      <div className="font-medium text-sm">{item.name}</div>
                      <div className={`text-xs mt-1 ${t.textTertiary}`}>{item.date}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-medium text-sm">{item.amount}</div>
                    <div className={`text-xs mt-1 ${t.textTertiary}`}>{item.status}</div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

"use client";

import { LucideIcon } from 'lucide-react';

interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: 'up' | 'down' | 'neutral';
  color?: string; // Kept for compatibility but ignored for styling
  gradientBorder?: boolean;
}

export default function StatsCard({ title, value, subtitle, icon: Icon, trend, color, gradientBorder }: StatsCardProps) {
  // Color prop is ignored in Utilitarian mode to enforce monochrome/single functional color.
  return (
    <div className="bg-[var(--card)] p-5 border border-[var(--border)] rounded-sm flex flex-col">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-xs opacity-50 font-medium uppercase tracking-wider">{title}</p>
          <p className="text-4xl font-light mt-2 leading-tight">{value}</p>
          {subtitle && (
            <p className={`text-xs mt-2 ${
              trend === 'up' ? 'text-black dark:text-white' : 
              trend === 'down' ? 'opacity-80' : 'opacity-50'
            }`}>
              {subtitle}
            </p>
          )}
        </div>
        <div className={`w-11 h-11 border border-[var(--border)] rounded-sm flex items-center justify-center`}>
          <Icon className="w-5 h-5 opacity-70" />
        </div>
      </div>
    </div>
  );
}

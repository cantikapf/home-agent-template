interface BadgeProps {
  children: React.ReactNode;
  variant?: 'success' | 'warning' | 'error' | 'info' | 'default';
  size?: 'sm' | 'md';
}

const variants = {
  success: 'border-[var(--border)] text-black dark:text-white',
  warning: 'border-[var(--border)] text-black dark:text-white border-dashed',
  error: 'bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/50',
  info: 'border-[var(--border)] text-blue-600 dark:text-blue-400',
  default: 'border-[var(--border)] opacity-60 text-black dark:text-white',
};

export default function Badge({ children, variant = 'default', size = 'sm' }: BadgeProps) {
  return (
    <span className={`
      inline-flex items-center rounded-sm border font-medium uppercase tracking-wider
      ${variants[variant]}
      ${size === 'sm' ? 'px-2 py-0.5 text-[10px]' : 'px-2.5 py-1 text-[11px]'}
    `}>
      {children}
    </span>
  );
}

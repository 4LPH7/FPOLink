import * as React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "destructive" | "outline" | "success" | "warning";
}

export function Badge({
  className,
  variant = "default",
  ...props
}: BadgeProps) {
  const base =
    "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 select-none";

  const variants: Record<string, string> = {
    default:
      "border-transparent bg-primary text-primary-foreground shadow-xs hover:bg-primary/80",
    secondary:
      "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
    destructive:
      "border-transparent bg-destructive text-destructive-foreground shadow-xs hover:bg-destructive/80",
    outline: "text-foreground",
    success:
      "border-emerald-200 bg-emerald-50 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-300 dark:border-emerald-800",
    warning:
      "border-amber-200 bg-amber-50 text-amber-800 dark:bg-amber-950/50 dark:text-amber-300 dark:border-amber-800",
  };

  return <div className={cn(base, variants[variant], className)} {...props} />;
}

import * as React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?:
    | "default"
    | "destructive"
    | "outline"
    | "secondary"
    | "ghost"
    | "link"
    | "success";
  size?: "default" | "sm" | "lg" | "icon";
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    const base =
      "inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium transition-[background-color,color,border-color,box-shadow,transform] duration-200 ease-out active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 disabled:active:scale-100 select-none";

    const variants: Record<string, string> = {
      default: "bg-primary text-primary-foreground hover:bg-primary/90 shadow-xs",
      destructive:
        "bg-destructive text-destructive-foreground hover:bg-destructive/90 shadow-xs",
      outline:
        "border border-input bg-background hover:bg-accent hover:text-accent-foreground shadow-xs",
      secondary:
        "bg-secondary text-secondary-foreground hover:bg-secondary/80",
      ghost: "hover:bg-accent hover:text-accent-foreground",
      link: "text-primary underline-offset-4 hover:underline",
      success:
        "bg-emerald-600 text-white hover:bg-emerald-700 shadow-xs shadow-emerald-600/20",
    };

    const sizes: Record<string, string> = {
      default: "h-11 px-4 py-2",
      sm: "h-11 rounded-lg px-3 text-xs",
      lg: "h-12 rounded-xl px-8 text-base",
      icon: "size-11",
    };

    return (
      <button
        ref={ref}
        className={cn(base, variants[variant], sizes[size], className)}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

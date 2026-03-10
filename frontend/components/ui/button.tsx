import { ButtonHTMLAttributes, forwardRef } from "react";

import { cn } from "@/lib/utils";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost" | "danger";
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center rounded-full border px-4 py-2 text-sm font-medium transition",
          "disabled:cursor-not-allowed disabled:opacity-50",
          variant === "primary" &&
            "border-transparent bg-accent text-white hover:bg-[#0a5961]",
          variant === "secondary" &&
            "border-line bg-white/70 text-ink hover:bg-white",
          variant === "ghost" &&
            "border-transparent bg-transparent text-ink hover:bg-black/5",
          variant === "danger" &&
            "border-transparent bg-ember text-white hover:bg-[#963c1b]",
          className
        )}
        {...props}
      />
    );
  }
);

Button.displayName = "Button";

import { Gamepad2, History, BookOpen } from "lucide-react";
import { cn } from "@/src/lib/utils";

interface BottomNavBarProps {
  active: "home" | "history" | "rules";
  onNavigate: (page: "home" | "history" | "rules") => void;
}

export default function BottomNavBar({
  active,
  onNavigate,
}: BottomNavBarProps) {
  const items = [
    { id: "home", label: "首页", icon: Gamepad2 },
    { id: "history", label: "历史", icon: History },
    { id: "rules", label: "规则", icon: BookOpen },
  ] as const;

  return (
    <nav className="fixed bottom-0 left-0 w-full flex justify-around items-center px-4 pb-8 pt-4 bg-white/80 backdrop-blur-xl border-t border-primary/5 shadow-[0_-12px_40px_rgba(0,0,0,0.04)] rounded-t-[2.5rem] z-50">
      {items.map((item) => {
        const isActive = active === item.id;
        const Icon = item.icon;

        return (
          <button
            key={item.id}
            onClick={() => onNavigate(item.id)}
            className={cn(
              "flex flex-col items-center justify-center px-6 py-2 rounded-2xl transition-all duration-300 active:scale-95",
              isActive
                ? "bg-primary-container text-primary translate-y-[-4px]"
                : "text-on-surface-variant hover:text-primary",
            )}
          >
            <Icon className={cn("w-6 h-6")} />
            {/* <Icon className={cn("w-6 h-6", isActive && "fill-current")} /> */}
            <span className="text-[10px] font-bold uppercase tracking-widest mt-1.5">
              {item.label}
            </span>
          </button>
        );
      })}
    </nav>
  );
}

import { Lightbulb } from 'lucide-react';
import { cn } from '@/src/lib/utils';

interface HunchCardProps {
  content: string;
  title?: string;
  className?: string;
}

export default function HunchCard({ content, title = "助手直觉", className }: HunchCardProps) {
  return (
    <div className={cn("glass-card p-6 rounded-2xl my-4 relative overflow-hidden", className)}>
      <div className="flex items-center gap-3 mb-3 relative z-10">
        <Lightbulb className="w-4 h-4 text-tertiary fill-current" />
        <span className="font-headline font-bold text-on-surface uppercase tracking-widest text-[10px]">{title}</span>
      </div>
      <p className="text-on-surface font-headline text-lg leading-tight italic relative z-10">
        “{content}”
      </p>
      <div className="absolute -right-8 -bottom-8 w-24 h-24 bg-tertiary/5 rounded-full blur-2xl" />
    </div>
  );
}

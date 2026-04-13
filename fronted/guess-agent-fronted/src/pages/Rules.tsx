import { MessageCircle, Lightbulb, CheckCircle2, ArrowRight, Sparkles } from 'lucide-react';
import { motion } from 'motion/react';

interface RulesProps {
  onBack: () => void;
}

export default function Rules({ onBack }: RulesProps) {
  const phases = [
    { icon: MessageCircle, title: '提问', desc: '用巧妙的问题询问 AI。尝试在不直接点破的情况下缩小概念范围。', color: 'bg-primary-container text-primary' },
    { icon: Lightbulb, title: '推测', desc: '当你确信时输入你的“直觉”。每一次错误的猜测都会增加挑战难度。', color: 'bg-secondary-container text-secondary' },
    { icon: CheckCircle2, title: '确认', desc: '向导将揭示真相。根据你的速度和精准度进行评分。', color: 'bg-tertiary-container text-tertiary' },
  ];

  const rules = [
    { num: '01', title: '提问限制', desc: '每局你只有 10 个提问名额。请谨慎使用，向导的回答非常精简。' },
    { num: '02', title: '禁止专有名词', desc: '问题必须是概念性的。禁止询问具体姓名或特定地点。' },
    { num: '03', title: '最终推测', desc: '在游戏结束和谜题揭晓前，你只有 3 次猜测机会。' },
  ];

  return (
    <div className="space-y-12 pb-12">
      <section className="space-y-6 pt-8">
        <div className="inline-flex items-center px-4 py-1.5 rounded-full bg-primary/5 text-primary font-bold text-[10px] tracking-[0.2em] uppercase">
          操作指南
        </div>
        <h2 className="text-4xl md:text-5xl font-headline font-extrabold text-on-surface leading-tight">
          掌握猜词的 <span className="text-primary italic">艺术</span>。
        </h2>
        <p className="text-lg text-on-surface-variant max-w-md leading-relaxed font-medium">
          空灵向导正在等候。学会穿梭于语言迷宫，赢取属于你的胜利。
        </p>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {phases.map((p, i) => (
          <motion.div 
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="bg-surface-container-low p-8 rounded-[2rem] space-y-6 flex flex-col items-start hover:bg-white transition-all shadow-sm group"
          >
            <div className={`w-14 h-14 rounded-2xl ${p.color} flex items-center justify-center group-hover:scale-110 transition-transform`}>
              <p.icon className="w-7 h-7" />
            </div>
            <h3 className="text-xl font-headline font-bold text-on-surface">{p.title}</h3>
            <p className="text-on-surface-variant text-sm leading-relaxed font-medium">{p.desc}</p>
          </motion.div>
        ))}
      </section>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-12 items-start">
        <div className="space-y-10">
          <h4 className="font-headline font-bold text-xl flex items-center gap-3">
            <BookIcon className="w-6 h-6 text-primary" />
            游戏规则
          </h4>
          <ul className="space-y-8">
            {rules.map((r, i) => (
              <li key={i} className="flex gap-6">
                <span className="text-primary/10 font-headline font-black text-4xl leading-none">{r.num}</span>
                <div className="space-y-1">
                  <h5 className="font-bold text-on-surface text-lg">{r.title}</h5>
                  <p className="text-sm text-on-surface-variant leading-relaxed font-medium">{r.desc}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <div className="glass-card p-10 rounded-[2.5rem] space-y-8 relative overflow-hidden">
          <div className="absolute -top-10 -right-10 w-40 h-40 bg-tertiary/5 rounded-full blur-3xl" />
          <div className="flex items-center gap-3 text-tertiary relative z-10">
            <Sparkles className="w-5 h-5" />
            <span className="font-headline font-bold tracking-widest text-[10px] uppercase">向导的提示</span>
          </div>
          <p className="text-2xl font-headline font-bold text-on-surface leading-tight relative z-10">
            “我是微风的无声伙伴，却能承载王国秘密的重量。”
          </p>
          <div className="pt-8 relative z-10">
            <p className="text-[9px] font-bold uppercase tracking-[0.2em] text-on-surface-variant/50 mb-4">新手专业贴士</p>
            <div className="bg-surface-container-highest/30 p-6 rounded-2xl backdrop-blur-sm">
              <p className="text-sm italic font-medium leading-relaxed">
                “注意向导如何强调‘无声’和‘微风’。思考一下无形的力量或媒介。”
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-primary text-white p-10 md:p-16 rounded-[3rem] relative overflow-hidden">
        <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <h4 className="text-4xl font-headline font-extrabold leading-tight">来自架构师的建议</h4>
            <p className="opacity-80 text-lg leading-relaxed font-medium">
              AI 使用语义网络。尝试询问“用途”、“材质”或“来源”，以快速缩小可能性范围。
            </p>
            <button 
              onClick={onBack}
              className="bg-white text-primary px-10 py-5 rounded-2xl font-bold transition-all active:scale-95 flex items-center gap-3 group shadow-xl shadow-black/10"
            >
              回到游戏
              <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
          <div className="hidden md:block">
            <img 
              alt="AI Insight" 
              className="rounded-3xl shadow-2xl rotate-3 scale-110" 
              src="https://picsum.photos/seed/ai-insight/600/400" 
              referrerPolicy="no-referrer"
            />
          </div>
        </div>
        <div className="absolute -bottom-20 -left-20 w-80 h-80 bg-black/10 rounded-full blur-[100px]" />
      </section>
    </div>
  );
}

function BookIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
    </svg>
  );
}

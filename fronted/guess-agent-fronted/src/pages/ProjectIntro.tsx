import {
  ArrowRight,
  BrainCircuit,
  Database,
  Layers3,
  LockKeyhole,
  ShieldCheck,
  Sparkles,
  Workflow,
  Zap,
} from "lucide-react";
import { motion } from "motion/react";
import coffeeImage from "../assets/image.png";

interface ProjectIntroProps {
  onBack: () => void;
}

const capabilityCards = [
  {
    span: "md:col-span-8",
    icon: BrainCircuit,
    title: "主模型",
    model: "DeepSeek-V3",
    desc: "作为核心大脑，DeepSeek-V3 负责复杂语义理解、策略生成与上下文推演，确保每一轮博弈都保持高挑战性与强逻辑性。",
    tags: ["核心模型", "游戏推进"],
    tone: "bg-primary-container text-primary",
  },
  {
    span: "md:col-span-4",
    icon: Zap,
    title: "辅助模型",
    model: "Qwen2.5",
    desc: "负责高并发下的快速响应与基础对话解析，作为系统的敏捷感知层。",
    tags: ["辅助模型", "系统词生成"],
    tone: "bg-tertiary-container text-tertiary",
  },
] as const;

const highlights = [
  {
    icon: ShieldCheck,
    title: "安全边界机制",
    desc: "LLM 不直接参与最终胜负判定。所有核心逻辑由后端闭环处理，Agent 仅作为引导者，避免模型幻觉破坏规则。",
  },
  {
    icon: LockKeyhole,
    title: "加密词库存储",
    desc: "所有游戏词条均经过加密处理，确保从出题到揭晓的全过程都具备清晰的安全边界与技术严谨性。",
  },
] as const;

const valuePills = ["逻辑可验证", "数据全加密", "多模型协作"] as const;

const summaryItems = [
  {
    icon: Layers3,
    title: "多模型协作",
    desc: "DeepSeek-V3 + Qwen2.5 协同工作",
  },
  {
    icon: ShieldCheck,
    title: "逻辑可验证",
    desc: "胜负判定由后端服务闭环完成",
  },
  {
    icon: LockKeyhole,
    title: "数据全加密",
    desc: "词库与状态在链路中保持安全隔离",
  },
  {
    icon: Workflow,
    title: "上下文管理",
    desc: "MemoryPolicy 负责过滤冗余历史",
  },
] as const;

export default function ProjectIntro({ onBack }: ProjectIntroProps) {
  return (
    <div className="space-y-12 pb-12 pt-8">
      <section className="relative overflow-hidden space-y-6 mb-4">
        <div className="absolute -top-20 -right-16 w-56 h-56 rounded-full  blur-3xl" />
        <div className="absolute -bottom-16 -left-16 w-64 h-64 rounded-full blur-3xl" />

        <motion.h2
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.08 }}
          className="font-headline text-4xl md:text-5xl font-extrabold tracking-tight text-on-surface leading-tight max-w-3xl"
        >
          Guess Game{" "}
          <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
            猜词项目
          </span>
        </motion.h2>

        <motion.p
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.16 }}
          className="text-lg text-on-surface-variant max-w-3xl leading-relaxed mb-2"
        >
          Guess Game
          是一款融合了大语言模型（LLM）、回合制逻辑猜词游戏系统。通过多模型协作，实现系统与用户的猜词游戏，你将和系统各自设定一个秘密词语，通过轮流提问的方式，抢先猜出对方设置的词语即可获胜
        </motion.p>

        <motion.h4>项目地址：https://github.com/janfeise/guess-agent</motion.h4>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {capabilityCards.map((card, index) => {
          const Icon = card.icon;

          return (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.08 * index }}
              className={`${card.span} p-8 rounded-[1.5rem] bg-surface-container-low flex flex-col justify-between gap-6 shadow-[0_8px_30px_rgba(0,0,0,0.04)] border border-black/5`}
            >
              <div className="space-y-4">
                <div className="flex items-start gap-4">
                  <div
                    className={`w-12 h-12 rounded-2xl ${card.tone} flex items-center justify-center flex-shrink-0 text-white/90`}
                  >
                    <Icon className="w-6 h-6" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="font-headline text-2xl font-bold text-on-surface leading-tight">
                      {card.title}
                    </h3>
                    {"model" in card && (
                      <p className="mt-1 text-base font-semibold text-on-surface-variant tracking-wide">
                        {card.model}
                      </p>
                    )}
                  </div>
                </div>

                <p className="text-on-surface-variant leading-relaxed">
                  {card.desc}
                </p>
              </div>

              <div className="flex flex-wrap gap-2">
                {card.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-3 py-1 bg-surface-container-lowest rounded-full text-xs font-medium text-on-surface-variant border border-black/5"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </motion.div>
          );
        })}
      </section>

      <section className="space-y-6 pb-18">
        <details>
          <summary>☕ 觉得项目有用？请作者喝杯咖啡</summary>
          <img src={coffeeImage} width="200" alt="请作者喝杯咖啡" />
        </details>
      </section>
    </div>
  );
}

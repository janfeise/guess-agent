import {
  AlertTriangle,
  Brain,
  GitBranch,
  Home,
  RefreshCcw,
  Sparkles,
  Target,
  Timer,
  Trophy,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import styles from "./Result.module.css";
import { GameEndStats, GameOutcome } from "@/src/types/game";

interface ResultProps {
  outcome: GameOutcome;
  stats: GameEndStats;
  onRestart: () => void;
  onHome: () => void;
}

function clampConfidence(value: number) {
  return Math.max(0, Math.min(100, value));
}

function StatCard({
  icon: Icon,
  label,
  value,
}: {
  icon: LucideIcon;
  label: string;
  value: string | number;
}) {
  return (
    <div className={styles.statCard}>
      <Icon className={styles.statCardIcon} />
      <div>
        <div className={styles.statCardLabel}>{label}</div>
        <div className={styles.statCardValue}>{value}</div>
      </div>
    </div>
  );
}

function ResultActions({
  onRestart,
  onHome,
  primaryLabel,
}: {
  onRestart: () => void;
  onHome: () => void;
  primaryLabel: string;
}) {
  return (
    <div className={styles.actions}>
      <button
        type="button"
        onClick={onRestart}
        className={styles.primaryButton}
      >
        <RefreshCcw className={styles.buttonIcon} />
        {primaryLabel}
      </button>
      <button type="button" onClick={onHome} className={styles.secondaryButton}>
        <Home className={styles.buttonIcon} />
        返回首页
      </button>
    </div>
  );
}

function VictoryResult({ stats, onRestart, onHome }: ResultProps) {
  const confidence = clampConfidence(stats.confidence ?? 85);
  const targetWord = stats.revealedWord || "答案已确认";
  const message =
    stats.message || "以太向导对此印象深刻。你的直觉在未知中开辟了一条道路。";

  return (
    <section className={`${styles.resultPage} ${styles.resultPageWin}`}>
      <div className={styles.resultShell}>
        <header className={styles.hero}>
          <div className={styles.badge}>
            <Trophy className={styles.badgeIcon} />
            <span>挑战完成</span>
          </div>
          <h2 className={styles.title}>胜利</h2>
          <p className={styles.subtitle}>{message}</p>
        </header>

        <div className={styles.grid}>
          <article className={styles.mainCard}>
            <span className={styles.cardLabel}>正确答案</span>
            <div className={styles.wordRow}>
              <Target className={styles.cardIcon} />
              <div className={styles.wordValue}>{targetWord}</div>
            </div>
            <div className={styles.cardFoot}>
              <Sparkles className={styles.footIcon} />
              <div className={styles.footDivider} />
            </div>
          </article>

          <div className={styles.statsGrid}>
            <StatCard icon={GitBranch} label="使用轮次" value={stats.rounds} />
            <StatCard icon={Timer} label="总用时" value={stats.time} />
          </div>
        </div>

        <ResultActions
          onRestart={onRestart}
          onHome={onHome}
          primaryLabel="再玩一次"
        />
      </div>
    </section>
  );
}

function FailureResult({ stats, onRestart, onHome }: ResultProps) {
  const confidence = clampConfidence(stats.confidence ?? 98);
  const targetWord = stats.revealedWord || "答案已揭晓";
  const message =
    stats.message ||
    "这一次，答案比你更快一步。换个角度重新出发，下一局会更接近。";

  return (
    <section className={`${styles.resultPage} ${styles.resultPageLose}`}>
      <div className={styles.resultShell}>
        <header className={styles.hero}>
          <div className={styles.badgeLose}>
            <AlertTriangle className={styles.badgeIcon} />
            <span>挑战结束</span>
          </div>
          <h2 className={styles.titleLose}>失败</h2>
          <p className={styles.subtitle}>{message}</p>
        </header>

        <div className={styles.grid}>
          <article className={styles.mainCardLose}>
            <span className={styles.cardLabel}>目标词汇</span>
            <div className={styles.wordRow}>
              <Target className={styles.cardIcon} />
              <div className={styles.wordValueLose}>{targetWord}</div>
            </div>
            <div className={styles.reviewCard}>
              <Sparkles className={styles.reviewIcon} />
              <p className={styles.reviewText}>
                你已经摸到答案的边缘了，只差最后一次判断。
              </p>
            </div>
          </article>

          <div className={styles.statsGrid}>
            <StatCard icon={GitBranch} label="使用轮次" value={stats.rounds} />
            <StatCard icon={Timer} label="总用时" value={stats.time} />

            <article
              className={`${styles.statCard} ${styles.statCardWideLose}`}
            >
              <div className={styles.confidenceHead}>
                <div>
                  <Brain className={styles.confidenceIconLose} />
                  <div className={styles.statCardLabel}>AI 信心指数</div>
                </div>
                <div className={styles.confidenceValueLose}>{confidence}%</div>
              </div>
              <div className={styles.progressTrackLose} aria-hidden="true">
                <div
                  className={styles.progressFillLose}
                  style={{ width: `${confidence}%` }}
                />
              </div>
            </article>
          </div>
        </div>

        <ResultActions
          onRestart={onRestart}
          onHome={onHome}
          primaryLabel="重新挑战"
        />
      </div>
    </section>
  );
}

export default function Result(props: ResultProps) {
  return props.outcome === "win" ? (
    <VictoryResult {...props} />
  ) : (
    <FailureResult {...props} />
  );
}

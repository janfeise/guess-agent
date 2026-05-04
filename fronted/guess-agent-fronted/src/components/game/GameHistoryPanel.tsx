import {
  AlertTriangle,
  Bot,
  CheckCircle2,
  Clock3,
  History as HistoryIcon,
  Sparkles,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { HistoryItem } from "@/src/types/game";
import styles from "./GameHistoryPanel.module.css";

interface GameHistoryPanelProps {
  history: HistoryItem[];
  selectedRoundNo: number | null;
  onSelectRound: (roundNo: number) => void;
}

type PerspectiveFilter = "all" | "user" | "system";
type RoundStatus = "current" | "completed" | "warning" | "confirmed";

interface RoundCardData {
  roundNo: number;
  items: HistoryItem[];
  status: RoundStatus;
  statusDetail?: string;
}

interface SecondaryLine {
  label: string;
  text: string;
  tone: RoundStatus | "neutral";
}

const POSITIVE_MARKERS = [
  "yes",
  "true",
  "correct",
  "confirmed",
  "confirm",
  "是",
  "对",
  "正确",
  "已确认",
  "确认",
  "猜对",
];

const NEGATIVE_MARKERS = [
  "no",
  "false",
  "incorrect",
  "wrong",
  "不是",
  "不对",
  "错误",
  "判定错误",
  "词性不符",
];

function joinClasses(...parts: Array<string | false | null | undefined>) {
  return parts.filter(Boolean).join(" ");
}

function normalizeText(value?: string | null) {
  return (value || "").trim().replace(/\s+/g, "").toLowerCase();
}

function containsMarker(value: string, markers: string[]) {
  return markers.some((marker) => value.includes(normalizeText(marker)));
}

function isCodeLike(value?: string | null) {
  const normalized = normalizeText(value);

  return [
    "pending",
    "wrong_guess",
    "agent_guess_wrong",
    "guess_incorrect",
    "user_asked_question",
    "system_asks_question",
    "system_makes_guess",
    "user_answer_recorded",
  ].includes(normalized);
}

function getStatusLabel(status: RoundStatus) {
  switch (status) {
    case "current":
      return "进行中";
    case "warning":
      return "判定错误";
    case "confirmed":
      return "已确认";
    case "completed":
    default:
      return "已完成";
  }
}

function getStatusIcon(status: RoundStatus) {
  switch (status) {
    case "current":
      return Clock3;
    case "warning":
      return AlertTriangle;
    case "confirmed":
    case "completed":
    default:
      return CheckCircle2;
  }
}

function getActorLabel(actor: HistoryItem["actor"]) {
  return actor === "user" ? "用户" : "系统";
}

function getTurnTypeLabel(turnType: HistoryItem["turn_type"]) {
  switch (turnType) {
    case "question":
      return "提问";
    case "answer":
      return "回答";
    case "ask":
      return "系统发问";
    case "guess":
      return "系统猜测";
    case "judge":
      return "判断";
    case "judge_agent_guess":
      return "系统判定";
    default:
      return turnType;
  }
}

function getFilterLabel(filter: PerspectiveFilter) {
  switch (filter) {
    case "all":
      return "全部";
    case "user":
      return "我方";
    case "system":
      return "系统";
    default:
      return filter;
  }
}

function formatConfidence(confidence?: number) {
  if (confidence == null) return null;

  const value = confidence <= 1 ? confidence * 100 : confidence;
  return `${Math.round(value)}%`;
}

function formatLabelText(value?: string | boolean | null) {
  if (value === true) return "是";
  if (value === false) return "否";
  if (value == null) return "未知";

  switch (value) {
    case "yes":
      return "是";
    case "no":
      return "否";
    case "unknown":
      return "未知";
    default:
      return value;
  }
}

function getPrimaryText(item: HistoryItem) {
  if (item.turn_type === "guess") {
    return item.input_text || item.hint || item.answer_text || "暂无内容";
  }

  if (item.turn_type === "answer") {
    return item.input_text || item.answer_text || item.hint || "暂无内容";
  }

  return item.input_text || item.hint || item.answer_text || "暂无内容";
}

function extractReasonText(...values: Array<string | undefined>) {
  for (const value of values) {
    const raw = (value || "").trim();
    if (!raw) {
      continue;
    }

    if (
      isCodeLike(raw) ||
      /^[a-z_]+=.+$/i.test(raw) ||
      /^[a-z_]+$/i.test(raw)
    ) {
      continue;
    }

    const labeledMatch = raw.match(
      /(?:原因|理由|说明|详情|detail|reason)[:=：]\s*(.+)$/i,
    );

    if (labeledMatch?.[1]) {
      return labeledMatch[1].trim();
    }

    const wrappedMatch = raw.match(/[（(]([^()（）]+)[）)]/);
    if (wrappedMatch?.[1]) {
      return wrappedMatch[1].trim();
    }

    return raw;
  }

  return "";
}

function getOutcomeText(status: RoundStatus, detail?: string) {
  if (!detail) {
    return status === "warning" ? "判定错误" : "已确认";
  }

  if (status === "warning") {
    return detail.includes("错误") ? detail : `判定错误（${detail}）`;
  }

  if (status === "confirmed") {
    return detail.includes("确认") ? detail : `已确认（${detail}）`;
  }

  return detail;
}

function getSecondaryLine(
  item: HistoryItem,
  status: RoundStatus,
): SecondaryLine | null {
  const responseText = extractReasonText(
    item.result,
    item.answer_text,
    item.hint,
  );

  if (item.turn_type === "question" && responseText) {
    return {
      label: "AI 回答",
      text: responseText,
      tone: status,
    };
  }

  if (item.turn_type === "ask" && responseText && !isCodeLike(responseText)) {
    return {
      label: "用户回应",
      text: responseText,
      tone: status,
    };
  }

  if (item.turn_type === "guess") {
    const outcomeText = getOutcomeText(status, responseText);

    if (outcomeText && !isCodeLike(outcomeText)) {
      return {
        label:
          status === "warning"
            ? "判定错误"
            : status === "confirmed"
              ? "已确认"
              : "结果",
        text: outcomeText,
        tone: status,
      };
    }
  }

  if (
    (item.turn_type === "judge" || item.turn_type === "judge_agent_guess") &&
    responseText
  ) {
    return {
      label: "判定结果",
      text: getOutcomeText(status, responseText),
      tone: status,
    };
  }

  if (item.turn_type === "answer" && item.answer_text) {
    return {
      label: "回答状态",
      text: formatLabelText(item.answer_text),
      tone: "neutral",
    };
  }

  return null;
}

function classifyRound(
  items: HistoryItem[],
  isLatestRound: boolean,
): RoundCardData {
  let status: RoundStatus = isLatestRound ? "current" : "completed";
  let statusDetail: string | undefined;

  for (let index = items.length - 1; index >= 0; index -= 1) {
    const item = items[index];
    const normalized = normalizeText(
      [item.result, item.answer_text, item.hint, item.input_text]
        .filter(Boolean)
        .join(" "),
    );

    const positiveSignal =
      item.answer_label === "yes" ||
      containsMarker(normalized, POSITIVE_MARKERS);
    const negativeSignal =
      item.answer_label === "no" ||
      containsMarker(normalized, NEGATIVE_MARKERS);

    if (negativeSignal) {
      status = "warning";
      statusDetail = extractReasonText(
        item.result,
        item.hint,
        item.answer_text,
        item.input_text,
      );
      break;
    }

    if (positiveSignal) {
      status = "confirmed";
      statusDetail = extractReasonText(
        item.result,
        item.hint,
        item.answer_text,
        item.input_text,
      );
      break;
    }
  }

  if (!isLatestRound && status === "current") {
    status = "completed";
  }

  return {
    roundNo: items[0].round_no,
    items,
    status,
    statusDetail,
  };
}

function getRoundCardClass(status: RoundStatus, isSelected: boolean) {
  return joinClasses(
    styles.roundCard,
    status === "current" && styles.roundCardCurrent,
    status === "warning" && styles.roundCardWarning,
    status === "confirmed" && styles.roundCardConfirmed,
    isSelected && styles.roundCardSelected,
  );
}

function getRoundDotClass(status: RoundStatus, isSelected: boolean) {
  return joinClasses(
    styles.timelineDot,
    status === "current" && styles.timelineDotCurrent,
    status === "warning" && styles.timelineDotWarning,
    status === "confirmed" && styles.timelineDotConfirmed,
    isSelected && styles.timelineDotSelected,
  );
}

function getStatusTagClass(status: RoundStatus) {
  return joinClasses(
    styles.statusTag,
    status === "current" && styles.statusTagCurrent,
    status === "completed" && styles.statusTagCompleted,
    status === "warning" && styles.statusTagWarning,
    status === "confirmed" && styles.statusTagConfirmed,
  );
}

function getStatusNoteClass(status: RoundStatus) {
  return joinClasses(
    styles.statusNote,
    status === "current" && styles.statusNoteCurrent,
    status === "warning" && styles.statusNoteWarning,
    status === "confirmed" && styles.statusNoteConfirmed,
  );
}

export default function GameHistoryPanel({
  history,
  selectedRoundNo,
  onSelectRound,
}: GameHistoryPanelProps) {
  const [filter, setFilter] = useState<PerspectiveFilter>("all");

  const sortedHistory = useMemo(() => {
    return [...history].sort((left, right) => right.round_no - left.round_no);
  }, [history]);

  const roundCards = useMemo(() => {
    const roundBuckets = new Map<number, HistoryItem[]>();

    for (const item of sortedHistory) {
      const bucket = roundBuckets.get(item.round_no);

      if (bucket) {
        bucket.push(item);
      } else {
        roundBuckets.set(item.round_no, [item]);
      }
    }

    const latestRoundNo = sortedHistory[0]?.round_no;

    return Array.from(roundBuckets.values()).map((items) =>
      classifyRound(items, items[0].round_no === latestRoundNo),
    );
  }, [sortedHistory]);

  const visibleRounds = useMemo(() => {
    if (filter === "all") {
      return roundCards;
    }

    return roundCards.filter((round) =>
      round.items.some((item) => item.actor === filter),
    );
  }, [filter, roundCards]);

  useEffect(() => {
    if (!visibleRounds.length) return;

    const selectedVisible = visibleRounds.some(
      (item) => item.roundNo === selectedRoundNo,
    );

    if (!selectedVisible) {
      onSelectRound(visibleRounds[0].roundNo);
    }
  }, [onSelectRound, selectedRoundNo, visibleRounds]);

  const selectedRound = useMemo(() => {
    if (visibleRounds.length === 0) return null;

    if (selectedRoundNo != null) {
      return (
        visibleRounds.find((item) => item.roundNo === selectedRoundNo) ||
        visibleRounds[0]
      );
    }

    return visibleRounds[0];
  }, [selectedRoundNo, visibleRounds]);

  const renderTurnBlock = (item: HistoryItem, roundStatus: RoundStatus) => {
    const secondaryLine = getSecondaryLine(item, roundStatus);
    const confidenceLabel = formatConfidence(item.confidence);

    return (
      <section className={styles.turnBlock}>
        <div className={styles.turnBlockHead}>
          <div className={styles.turnTags}>
            <span
              className={joinClasses(
                styles.actorPill,
                item.actor === "user"
                  ? styles.actorPillUser
                  : styles.actorPillSystem,
              )}
            >
              {getActorLabel(item.actor)}
            </span>
            <span className={styles.turnTypePill}>
              {getTurnTypeLabel(item.turn_type)}
            </span>
          </div>

          {confidenceLabel && (
            <span className={styles.confidencePill}>{confidenceLabel}</span>
          )}
        </div>

        <div className={styles.turnMain}>{getPrimaryText(item)}</div>

        {secondaryLine && (
          <div className={styles.turnSecondary}>
            <span
              className={joinClasses(
                styles.turnSecondaryLabel,
                secondaryLine.tone === "warning" &&
                  styles.turnSecondaryLabelWarning,
                secondaryLine.tone === "confirmed" &&
                  styles.turnSecondaryLabelConfirmed,
                secondaryLine.tone === "current" &&
                  styles.turnSecondaryLabelCurrent,
                secondaryLine.tone === "neutral" &&
                  styles.turnSecondaryLabelNeutral,
                secondaryLine.tone === "completed" &&
                  styles.turnSecondaryLabelNeutral,
              )}
            >
              {secondaryLine.label}
            </span>
            <span className={styles.turnSecondaryText}>
              {secondaryLine.text}
            </span>
          </div>
        )}
      </section>
    );
  };

  const renderRoundNote = (round: RoundCardData) => {
    if (round.status === "current") {
      return (
        <div className={getStatusNoteClass(round.status)}>
          当前回合仍在推进中，记录会随着后续输入继续补全。
        </div>
      );
    }

    if (round.status === "warning") {
      return (
        <div className={getStatusNoteClass(round.status)}>
          错误原因：{getOutcomeText(round.status, round.statusDetail)}
        </div>
      );
    }

    if (round.status === "confirmed") {
      return (
        <div className={getStatusNoteClass(round.status)}>
          已确认：{getOutcomeText(round.status, round.statusDetail)}
        </div>
      );
    }

    return null;
  };

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <div className={styles.filterBar}>
          {(["all", "user", "system"] as PerspectiveFilter[]).map((item) => {
            const active = filter === item;

            return (
              <button
                key={item}
                type="button"
                onClick={() => setFilter(item)}
                className={joinClasses(
                  styles.filterButton,
                  active && styles.filterButtonActive,
                )}
              >
                {getFilterLabel(item)}
              </button>
            );
          })}
        </div>
      </div>

      <div className={styles.body}>
        <div className={styles.list}>
          {visibleRounds.length > 0 ? (
            visibleRounds.map((round, index) => {
              const isSelected = round.roundNo === selectedRound?.roundNo;
              const StatusIcon = getStatusIcon(round.status);

              return (
                <div className={styles.roundRow} key={round.roundNo}>
                  <div className={styles.timelineRail}>
                    <div
                      className={getRoundDotClass(round.status, isSelected)}
                    />
                    {index !== visibleRounds.length - 1 && (
                      <div className={styles.timelineLine} />
                    )}
                  </div>

                  <button
                    type="button"
                    onClick={() => onSelectRound(round.roundNo)}
                    className={getRoundCardClass(round.status, isSelected)}
                    aria-pressed={isSelected}
                  >
                    <div className={styles.cardHeader}>
                      <div className={styles.headerTags}>
                        <span className={styles.roundBadge}>
                          回合 {String(round.roundNo).padStart(2, "0")}
                        </span>
                        <span className={getStatusTagClass(round.status)}>
                          <StatusIcon className={styles.statusIcon} />
                          {getStatusLabel(round.status)}
                        </span>
                      </div>

                      <span className={styles.roundMeta}>
                        {round.items.length} 条消息
                      </span>
                    </div>

                    <div className={styles.turnList}>
                      {round.items.map((item, itemIndex) => (
                        <div
                          key={`${round.roundNo}-${itemIndex}-${item.actor}-${item.turn_type}`}
                        >
                          {renderTurnBlock(item, round.status)}
                        </div>
                      ))}
                    </div>

                    {renderRoundNote(round)}
                  </button>
                </div>
              );
            })
          ) : (
            <div className={styles.emptyState}>
              <div>
                <div className={styles.emptyIconWrap}>
                  <Bot className={styles.emptyIcon} />
                </div>
                <p className={styles.emptyTitle}>暂无可展示的回合记录</p>
                <p className={styles.emptyText}>
                  当前筛选条件下没有可见的回合内容。
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

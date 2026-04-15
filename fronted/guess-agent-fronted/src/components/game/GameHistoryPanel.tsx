import { Bot, History as HistoryIcon, Sparkles } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { HistoryItem } from "@/src/types/game";

interface GameHistoryPanelProps {
  history: HistoryItem[];
  selectedRoundNo: number | null;
  onSelectRound: (roundNo: number) => void;
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
    default:
      return turnType;
  }
}

function getSummary(item: HistoryItem) {
  return item.input_text || item.answer_text || item.hint || "暂无内容";
}

function formatConfidence(confidence?: number) {
  if (confidence == null) return "未知";

  const value = confidence <= 1 ? confidence * 100 : confidence;
  return `${Math.round(value)}%`;
}

function formatLabelText(value?: string | boolean | null) {
  if (value === true) return "是";
  if (value === false) return "否";
  if (value == null) return "未知";
  return value;
}

type PerspectiveFilter = "all" | "user" | "system";

function getFilterLabel(filter: PerspectiveFilter) {
  switch (filter) {
    case "all":
      return "全部";
    case "user":
      return "用户视角";
    case "system":
      return "系统视角";
    default:
      return filter;
  }
}

function getBadgeStyle(actor: HistoryItem["actor"]) {
  return actor === "user"
    ? "bg-on-surface/10 text-on-surface"
    : "bg-primary-container/40 text-primary";
}

function getPillStyle(actor: HistoryItem["actor"], kind?: "secondary") {
  if (kind === "secondary") {
    return actor === "user"
      ? "bg-primary/12 text-primary"
      : "bg-secondary/12 text-secondary";
  }

  return actor === "user"
    ? "bg-surface-container-high text-on-surface"
    : "bg-tertiary-container/35 text-tertiary";
}

function buildVisibleSummary(item: HistoryItem) {
  if (item.actor === "user") {
    return item.input_text || item.answer_text || item.hint || "暂无内容";
  }

  return item.answer_text || item.hint || item.input_text || "暂无内容";
}

export default function GameHistoryPanel({
  history,
  selectedRoundNo,
  onSelectRound,
}: GameHistoryPanelProps) {
  const [filter, setFilter] = useState<PerspectiveFilter>("all");

  const sortedHistory = useMemo(
    () => [...history].sort((left, right) => right.round_no - left.round_no),
    [history],
  );

  const visibleHistory = useMemo(() => {
    if (filter === "all") return sortedHistory;

    return sortedHistory.filter((item) =>
      filter === "user" ? item.actor === "user" : item.actor === "system",
    );
  }, [filter, sortedHistory]);

  useEffect(() => {
    if (!visibleHistory.length) return;

    const selectedVisible = visibleHistory.some(
      (item) => item.round_no === selectedRoundNo,
    );

    if (!selectedVisible) {
      onSelectRound(visibleHistory[0].round_no);
    }
  }, [onSelectRound, selectedRoundNo, visibleHistory]);

  const selectedItem = useMemo(() => {
    if (visibleHistory.length === 0) return null;

    if (selectedRoundNo != null) {
      return (
        visibleHistory.find((item) => item.round_no === selectedRoundNo) ||
        visibleHistory[0]
      );
    }

    return visibleHistory[0];
  }, [selectedRoundNo, visibleHistory]);

  const renderEntryBody = (item: HistoryItem, expanded: boolean) => {
    if (item.actor === "user") {
      return (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <span
              className={`inline-flex items-center rounded-full px-3 py-1 text-[10px] font-bold ${getPillStyle(
                item.actor,
              )}`}
            >
              用户
            </span>
            <p className="text-sm leading-relaxed text-on-surface">
              {item.input_text || item.answer_text || item.hint || "暂无内容"}
            </p>
          </div>

          {expanded && (item.answer_text || item.hint) && (
            <div className="flex items-center gap-2">
              <span
                className={`inline-flex items-center rounded-full px-3 py-1 text-[10px] font-bold ${getPillStyle(
                  item.actor,
                  "secondary",
                )}`}
              >
                AI
              </span>
              <p className="text-sm leading-relaxed text-on-surface-variant">
                {item.answer_text || item.hint}
              </p>
            </div>
          )}
        </div>
      );
    }

    return (
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <span
            className={`inline-flex items-center rounded-full px-3 py-1 text-[10px] font-bold ${getPillStyle(
              item.actor,
            )}`}
          >
            系统
          </span>
          <p className="text-sm leading-relaxed text-on-surface">
            {item.input_text || item.hint || "暂无内容"}
          </p>
        </div>

        {expanded && (
          <div className="flex items-center gap-2">
            <span
              className={`inline-flex items-center rounded-full px-3 py-1 text-[10px] font-bold ${getPillStyle(
                item.actor,
                "secondary",
              )}`}
            >
              结果
            </span>
            <p className="text-sm leading-relaxed text-on-surface-variant">
              {item.answer_text ||
                item.hint ||
                formatLabelText(item.answer_label)}
            </p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden">
      <div className="rounded-[2rem] bg-gradient-to-br from-primary/8 to-primary/4 px-5 py-5 ring-1 ring-primary/10">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-primary-container/60 text-primary">
            <HistoryIcon className="h-5 w-5" />
          </div>
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.35em] text-on-surface-variant/60">
              回合历史
            </p>
            <h3 className="mt-1 font-headline text-xl font-extrabold text-on-surface">
              详情查看与切换
            </h3>
          </div>
        </div>
        <p className="mt-3 text-sm leading-relaxed text-on-surface-variant">
          点击任意记录后，右侧内容会切换为对应回合的展开详情。
        </p>
      </div>

      <div className="mt-5 flex-1 min-h-0 overflow-hidden rounded-[2rem] bg-surface-container-low/60 p-4 ring-1 ring-outline/10">
        <div className="flex items-center justify-between gap-3 rounded-[1.5rem] bg-surface-container-low px-1 py-1">
          {(["all", "user", "system"] as PerspectiveFilter[]).map((item) => {
            const active = filter === item;

            return (
              <button
                key={item}
                type="button"
                onClick={() => setFilter(item)}
                className={`flex-1 rounded-[1.25rem] px-4 py-3 text-sm font-bold transition-all duration-200 ${
                  active
                    ? "bg-primary-container text-on-primary-container shadow-[0_8px_18px_rgba(0,108,90,0.12)]"
                    : "text-on-surface-variant hover:text-on-surface"
                }`}
              >
                {getFilterLabel(item)}
              </button>
            );
          })}
        </div>

        <div className="mt-5 flex h-full min-h-0 flex-col overflow-hidden">
          <div className="min-h-0 flex-1 overflow-y-auto pb-6 pr-1">
            {visibleHistory.length > 0 ? (
              <div className="space-y-5">
                {visibleHistory.map((item, index) => {
                  const isSelected = item.round_no === selectedItem?.round_no;
                  const isUser = item.actor === "user";

                  return (
                    <div
                      key={`${item.round_no}-${item.turn_type}-${item.actor}`}
                    >
                      <div className="mb-2 flex items-center justify-between px-1">
                        <span
                          className={`text-sm font-headline font-bold uppercase tracking-tighter ${
                            isSelected ? "text-primary" : "text-slate-400"
                          }`}
                        >
                          回合 {String(item.round_no).padStart(2, "0")}
                        </span>
                        <span className="text-[10px] font-medium text-slate-400">
                          {index === 0 ? "刚刚" : `${index * 4}分钟前`}
                        </span>
                      </div>

                      <button
                        type="button"
                        onClick={() => onSelectRound(item.round_no)}
                        className={`group relative flex w-full items-start gap-4 rounded-[1.5rem] p-4 text-left transition-all duration-200 ${
                          isSelected
                            ? "bg-white shadow-[0_10px_28px_rgba(45,51,53,0.08)] ring-1 ring-outline/10"
                            : "bg-white/70 shadow-[0_6px_18px_rgba(45,51,53,0.04)]"
                        }`}
                      >
                        <div className="relative flex flex-col items-center pt-2">
                          <div
                            className={`h-5 w-5 rounded-full ring-4 ring-surface-container-low transition-all duration-200 ${
                              isSelected
                                ? "bg-primary scale-110"
                                : isUser
                                  ? "bg-primary/70"
                                  : "bg-slate-300"
                            }`}
                          />
                          {index !== visibleHistory.length - 1 && (
                            <div className="mt-1 h-[calc(100%-1rem)] w-0.5 bg-primary/12" />
                          )}
                        </div>

                        <div className="min-w-0 flex-1">
                          <div className="mb-3 flex items-center justify-between gap-3">
                            <span
                              className={`inline-flex items-center rounded-full px-3 py-1 text-[11px] font-bold ${getBadgeStyle(
                                item.actor,
                              )}`}
                            >
                              {getActorLabel(item.actor)}
                            </span>
                            <span className="text-[10px] font-medium text-slate-400">
                              {getTurnTypeLabel(item.turn_type)}
                            </span>
                          </div>

                          <div className="rounded-[1.25rem] bg-surface px-4 py-4">
                            {renderEntryBody(item, isSelected)}
                          </div>
                        </div>
                      </button>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="flex h-full items-center justify-center rounded-[1.5rem] bg-white/70 px-6 py-10 text-center shadow-[0_6px_18px_rgba(45,51,53,0.04)]">
                <div>
                  <Bot className="mx-auto h-10 w-10 text-primary/40" />
                  <p className="mt-3 text-sm font-medium text-on-surface-variant">
                    暂无可展示的回合记录
                  </p>
                </div>
              </div>
            )}
          </div>

          <div className="mt-auto rounded-[1.5rem] bg-primary/6 px-4 py-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-on-primary shadow-[0_8px_18px_rgba(0,108,90,0.16)]">
                <Sparkles className="h-5 w-5" />
              </div>
              <div>
                <p className="text-xs font-bold text-primary">系统洞察</p>
                <p className="text-[11px] leading-relaxed text-primary/70">
                  当前已记录 {sortedHistory.length}{" "}
                  个回合，点击任意卡片可查看展开内容。
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

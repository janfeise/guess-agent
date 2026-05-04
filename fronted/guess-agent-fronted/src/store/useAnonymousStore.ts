/**
 * anonymous store 用于存储匿名用户的唯一标识符，确保用户在不同会话中保持一致的身份。
 *
 * 使用方法：
 * const { anonymousId } = useAnonymousStore();
 * */

import { create } from "zustand";

const ANON_KEY = "__anonymous_id__";

interface AnonymousStore {
  anonymousId: string | null;
  // 可以保留一个手动刷新的方法或初始化方法（如果未来有需求）
  initAnonymousId: () => void;
}

// 提取一个纯函数用于安全地获取或生成 ID
const getOrGenerateId = (): string | null => {
  if (typeof window === "undefined") return null;

  let id = localStorage.getItem(ANON_KEY);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(ANON_KEY, id);
  }
  return id;
};

export const useAnonymousStore = create<AnonymousStore>((set) => ({
  // 直接调用纯函数进行初始化，避免作用域错误
  anonymousId: getOrGenerateId(), // 修复了原本无法找到引用的问题

  initAnonymousId: () => {
    // 保持幂等性，更新 state
    const id = getOrGenerateId();
    if (id) {
      set({ anonymousId: id });
    }
  },
}));

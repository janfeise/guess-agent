import axios, { AxiosInstance } from "axios";
import {
  CreateGameRequest,
  CreateGameResponse,
  GameDetailsResponse,
  UserGameHistoryResponse,
  SubmitTurnRequest,
  SubmitTurnResponse,
  HealthResponse,
  ErrorResponse,
} from "@/src/types/game";

/**
 * API 客户端类 - 封装所有后端接口调用
 */
class GameApiClient {
  private client: AxiosInstance;
  private apiClient: AxiosInstance;
  private baseURL: string;
  private pendingHealthCheck: Promise<HealthResponse> | null = null;
  private pendingCreateGameRequests = new Map<
    string,
    Promise<CreateGameResponse>
  >();

  constructor(baseURL?: string) {
    // 开发环境下使用相对路径以启用 Vite 代理
    // 生产环境下优先使用环境变量，否则默认走同源代理路径
    let apiUrl = baseURL;

    if (!apiUrl) {
      const envUrl = (import.meta as any).env?.VITE_API_BASE_URL;
      if (envUrl) {
        apiUrl = envUrl;
      } else {
        apiUrl = "/api/v1";
      }
    }

    const resolvedApiUrl = apiUrl || "/api/v1";
    const apiRootUrl = resolvedApiUrl.replace(/\/api\/v1\/?$/, "/api");

    this.baseURL = resolvedApiUrl; // 保存当前基础 URL
    this.client = axios.create({
      baseURL: resolvedApiUrl,
      headers: {
        "Content-Type": "application/json",
      },
      timeout: 30000, // 30 秒超时
    });
    this.apiClient = axios.create({
      baseURL: apiRootUrl,
      headers: {
        "Content-Type": "application/json",
      },
      timeout: 30000,
    });

    // 响应拦截器：处理错误
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response) {
          // 服务器返回错误状态码
          const errorData = error.response.data as ErrorResponse;
          console.error(
            `API Error (${error.response.status}):`,
            errorData.detail || "未知错误",
          );
        } else if (error.request) {
          // 请求已发出但没有收到响应
          console.error("API Error: 无法连接到服务器");
        } else {
          // 请求配置出错
          console.error("API Error:", error.message);
        }
        return Promise.reject(error);
      },
    );
  }

  /**
   * 健康检查
   */
  async checkHealth(): Promise<HealthResponse> {
    if (this.pendingHealthCheck) {
      return this.pendingHealthCheck;
    }

    const requestPromise = this.client
      .get<HealthResponse>("/health")
      .then((response) => response.data)
      .finally(() => {
        this.pendingHealthCheck = null;
      });

    this.pendingHealthCheck = requestPromise;
    return requestPromise;
  }

  /**
   * 创建游戏
   */
  async createGame(request: CreateGameRequest): Promise<CreateGameResponse> {
    const requestKey = JSON.stringify({
      user_word: request.user_word,
      difficulty: request.difficulty ?? null,
    });

    const pendingRequest = this.pendingCreateGameRequests.get(requestKey);
    if (pendingRequest) {
      return pendingRequest;
    }

    const requestPromise = this.client
      .post<CreateGameResponse>("/games", request)
      .then((response) => response.data)
      .finally(() => {
        this.pendingCreateGameRequests.delete(requestKey);
      });

    this.pendingCreateGameRequests.set(requestKey, requestPromise);

    return requestPromise;
  }

  /**
   * 提交游戏回合
   */
  async submitTurn(
    gameId: string,
    request: SubmitTurnRequest,
  ): Promise<SubmitTurnResponse> {
    const response = await this.client.post<SubmitTurnResponse>(
      `/games/${gameId}/turns`,
      request,
    );
    return response.data;
  }

  /**
   * 获取游戏详情（如需）
   */
  async getGameDetails(gameId: string, userId: string): Promise<any> {
    const response = await this.apiClient.get<GameDetailsResponse>(
      `/game/${gameId}/details`,
      {
        params: { userId },
      },
    );
    return response.data;
  }

  /**
   * 获取用户所有游戏历史
   */
  async getUserGameHistory(userId: string): Promise<UserGameHistoryResponse> {
    const response = await this.apiClient.get<UserGameHistoryResponse>(
      "/user/games/history",
      {
        params: { userId },
      },
    );
    return response.data;
  }

  /**
   * 修改基础 URL
   */
  setBaseURL(url: string): void {
    this.baseURL = url;
    this.client.defaults.baseURL = url;
  }

  /**
   * 获取当前基础 URL
   */
  getBaseURL(): string {
    return this.baseURL;
  }
}

// 创建单例实例
export const gameApiClient = new GameApiClient();

// 导出客户端类用于测试
export default GameApiClient;

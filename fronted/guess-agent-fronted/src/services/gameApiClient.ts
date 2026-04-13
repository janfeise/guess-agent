import axios, { AxiosInstance } from "axios";
import {
  CreateGameRequest,
  CreateGameResponse,
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
  private baseURL: string;

  constructor(baseURL?: string) {
    // 开发环境下使用相对路径以启用 Vite 代理
    // 生产环境下使用环境变量或完整 URL
    let apiUrl = baseURL;

    if (!apiUrl) {
      const envUrl = (import.meta as any).env?.VITE_API_BASE_URL;
      if (envUrl) {
        apiUrl = envUrl;
      } else if ((import.meta as any).env?.DEV) {
        // 开发环境：使用相对路径，让 Vite 代理处理
        apiUrl = "/api/v1";
      } else {
        // 生产环境：默认基于当前域名
        apiUrl = `${window.location.origin}/api/v1`;
      }
    }

    this.baseURL = apiUrl; // 保存当前基础 URL
    this.client = axios.create({
      baseURL: apiUrl,
      headers: {
        "Content-Type": "application/json",
      },
      timeout: 30000, // 30 秒超时
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
    const response = await this.client.get<HealthResponse>("/health");
    return response.data;
  }

  /**
   * 创建游戏
   */
  async createGame(request: CreateGameRequest): Promise<CreateGameResponse> {
    const response = await this.client.post<CreateGameResponse>(
      "/games",
      request,
    );
    return response.data;
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
  async getGameDetails(gameId: string): Promise<any> {
    const response = await this.client.get(`/games/${gameId}`);
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

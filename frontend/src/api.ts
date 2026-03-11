// frontend/app/api.ts

export interface AdkEvent {
  invocation_id: string;
  author: string;
  actions?: {
    text_delta?: string;
    state_delta?: any;
    tool_call?: any;
    tool_output?: any;
    artifact_delta?: any;
  };
  timestamp: string;
}

export class AdkClient {
  private baseUrl: string;
  private appName: string = "app";
  private userId: string = "user"; // Matched with backend default

  constructor(port: number) {
    // Dynamically use the current hostname (e.g., if running on a remote server/IP)
    const host = typeof window !== "undefined" ? window.location.hostname : "localhost";
    this.baseUrl = `http://${host}:${port}`;
  }

  async runAgent(sessionId: string, message?: string): Promise<AdkEvent[]> {
    const response = await fetch(`${this.baseUrl}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        app_name: this.appName,
        user_id: this.userId,
        session_id: sessionId,
        new_message: message ? { role: "user", parts: [{ text: message }] } : undefined,
        streaming: false,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to run agent: ${response.statusText}`);
    }

    return await response.json();
  }

  async listArtifacts(sessionId: string): Promise<string[]> {
    const response = await fetch(
      `${this.baseUrl}/apps/${this.appName}/users/${this.userId}/sessions/${sessionId}/artifacts`
    );
    if (!response.ok) return [];
    return await response.json();
  }

  async getArtifact(sessionId: string, filename: string): Promise<any> {
    const response = await fetch(
      `${this.baseUrl}/apps/${this.appName}/users/${this.userId}/sessions/${sessionId}/artifacts/${filename}`
    );
    if (!response.ok) return null;
    return await response.json();
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      return response.ok;
    } catch (err) {
      return false;
    }
  }

  async createSession(): Promise<string> {
    const response = await fetch(`${this.baseUrl}/apps/${this.appName}/users/${this.userId}/sessions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    const session = await response.json();
    return session.id;
  }
}

export const strategyClient = new AdkClient(8000);
export const contentClient = new AdkClient(8001);

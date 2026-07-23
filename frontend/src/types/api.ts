export interface HealthResponse {
  status: "ok";
}

export interface ReadinessResponse {
  status: "ready";
  dependencies: {
    database: "ok";
    redis: "ok";
  };
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details: unknown;
  };
}

/**
 * OpenAPI 3.0 spec for Express API (Bolt-compatible).
 * Used by Swagger UI (/docs) and ReDoc (/redoc).
 */

import { config } from "./config.js";

export function getOpenApiSpec(req) {
  let baseUrl = req ? `${req.protocol}://${req.get("host")}` : `http://localhost:${config.port}`;
  // 0.0.0.0 → localhost (brauzer "Try it out" uchun)
  if (baseUrl.includes("0.0.0.0")) {
    baseUrl = baseUrl.replace("0.0.0.0", "localhost");
  }

  return {
    openapi: "3.0.3",
    info: {
      title: "Express API (Bolt-compatible)",
      description:
        "Same endpoints as Django Bolt. Health, Roles, Users, Auth. JWT via POST /auth/login. Use **Authorize** to add Bearer token.",
      version: "0.1.0",
    },
    servers: [{ url: baseUrl, description: "API server" }],
    components: {
      securitySchemes: {
        BearerAuth: {
          type: "http",
          scheme: "bearer",
          bearerFormat: "JWT",
          description:
            "JWT from POST /auth/login. Click Authorize, enter: Bearer <your_access_token>",
        },
      },
      schemas: {
        HealthResponse: {
          type: "object",
          properties: { status: { type: "string", example: "ok" } },
        },
        HealthTestResponse: {
          type: "object",
          properties: {
            status: { type: "string", example: "ok" },
            message: { type: "string", example: "Test health check endpoint" },
          },
        },
        ReadyResponse: {
          type: "object",
          properties: {
            status: { type: "string", enum: ["healthy", "unhealthy"] },
            checks: {
              type: "object",
              properties: { database: { type: "string" } },
            },
          },
        },
        RoleSchema: {
          type: "object",
          properties: {
            code: { type: "string", example: "ADMIN" },
            name: { type: "string", example: "Administrator" },
          },
        },
        UserSchema: {
          type: "object",
          properties: {
            id: { type: "integer", example: 1 },
            username: { type: "string", example: "admin" },
            role: { type: "string", example: "ADMIN" },
          },
        },
        UserListResponse: {
          type: "object",
          properties: {
            results: { type: "array", items: { $ref: "#/components/schemas/UserSchema" } },
            count: { type: "integer" },
            next: { type: "string", nullable: true },
            previous: { type: "string", nullable: true },
          },
        },
        LoginSchema: {
          type: "object",
          required: ["username", "password"],
          properties: {
            username: { type: "string", example: "admin" },
            password: { type: "string", example: "password" },
          },
        },
        TokenSchema: {
          type: "object",
          properties: {
            access_token: { type: "string" },
            expires_in: { type: "integer" },
            token_type: { type: "string", example: "bearer" },
          },
        },
        ErrorDetail: {
          type: "object",
          properties: { detail: { type: "string" } },
        },
      },
    },
    paths: {
      "/health": {
        get: {
          tags: ["Health"],
          summary: "Liveness",
          description: "Simple liveness check.",
          responses: {
            "200": {
              description: "OK",
              content: {
                "application/json": {
                  schema: { $ref: "#/components/schemas/HealthResponse" },
                },
              },
            },
          },
        },
      },
      "/health/test": {
        get: {
          tags: ["Health"],
          summary: "Custom health check",
          description: "Test health check endpoint (Bolt-compatible).",
          responses: {
            "200": {
              description: "OK",
              content: {
                "application/json": {
                  schema: { $ref: "#/components/schemas/HealthTestResponse" },
                },
              },
            },
          },
        },
      },
      "/ready": {
        get: {
          tags: ["Health"],
          summary: "Readiness",
          description: "Readiness check (DB). Returns 503 if unhealthy.",
          responses: {
            "200": {
              description: "Healthy",
              content: {
                "application/json": {
                  schema: { $ref: "#/components/schemas/ReadyResponse" },
                },
              },
            },
            "503": {
              description: "Unhealthy",
              content: {
                "application/json": {
                  schema: { $ref: "#/components/schemas/ReadyResponse" },
                },
              },
            },
          },
        },
      },
      "/roles": {
        get: {
          tags: ["Roles"],
          summary: "List roles",
          description: "List all roles (ADMIN, SHOPKEEPER, CUSTOMER).",
          responses: {
            "200": {
              description: "OK",
              content: {
                "application/json": {
                  schema: {
                    type: "array",
                    items: { $ref: "#/components/schemas/RoleSchema" },
                  },
                },
              },
            },
          },
        },
      },
      "/roles/code/{code}": {
        get: {
          tags: ["Roles"],
          summary: "Get role by code",
          parameters: [
            {
              name: "code",
              in: "path",
              required: true,
              schema: { type: "string", example: "ADMIN" },
            },
          ],
          responses: {
            "200": {
              description: "OK",
              content: {
                "application/json": {
                  schema: { $ref: "#/components/schemas/RoleSchema" },
                },
              },
            },
            "404": {
              description: "Role not found",
              content: {
                "application/json": {
                  schema: { $ref: "#/components/schemas/ErrorDetail" },
                },
              },
            },
          },
        },
      },
      "/users": {
        get: {
          tags: ["Users"],
          summary: "List users",
          description: "Paginated list with search and role filter.",
          parameters: [
            { name: "search", in: "query", schema: { type: "string" } },
            { name: "role", in: "query", schema: { type: "string", enum: ["ADMIN", "SHOPKEEPER", "CUSTOMER"] } },
            { name: "role_code", in: "query", schema: { type: "string" } },
            { name: "page", in: "query", schema: { type: "integer", default: 1 } },
            { name: "page_size", in: "query", schema: { type: "integer", default: 10 } },
          ],
          responses: {
            "200": {
              description: "OK",
              content: {
                "application/json": {
                  schema: { $ref: "#/components/schemas/UserListResponse" },
                },
              },
            },
          },
        },
      },
      "/users/{id}": {
        get: {
          tags: ["Users"],
          summary: "Get user by ID",
          parameters: [
            {
              name: "id",
              in: "path",
              required: true,
              schema: { type: "integer" },
            },
          ],
          responses: {
            "200": {
              description: "OK",
              content: {
                "application/json": {
                  schema: { $ref: "#/components/schemas/UserSchema" },
                },
              },
            },
            "404": {
              description: "User not found",
              content: {
                "application/json": {
                  schema: { $ref: "#/components/schemas/ErrorDetail" },
                },
              },
            },
          },
        },
      },
      "/auth/login": {
        post: {
          tags: ["Auth"],
          summary: "Login (JWT)",
          description: "Obtain JWT access token. No auth required.",
          requestBody: {
            required: true,
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/LoginSchema" },
              },
            },
          },
          responses: {
            "200": {
              description: "OK",
              content: {
                "application/json": {
                  schema: { $ref: "#/components/schemas/TokenSchema" },
                },
              },
            },
            "400": {
              description: "Bad request",
              content: {
                "application/json": {
                  schema: { $ref: "#/components/schemas/ErrorDetail" },
                },
              },
            },
            "401": {
              description: "Invalid credentials",
              content: {
                "application/json": {
                  schema: { $ref: "#/components/schemas/ErrorDetail" },
                },
              },
            },
          },
        },
      },
    },
  };
}

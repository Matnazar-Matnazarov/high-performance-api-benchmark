package docs

import (
	"encoding/json"
	"net/http"
)

// OpenAPI returns the OpenAPI 3.0 spec for the Go API (Bolt-compatible).
// All responses include X-Server-Time and X-Response-Time headers.
func OpenAPI(baseURL string) map[string]any {
	if baseURL == "" {
		baseURL = "http://localhost:8005"
	}
	return map[string]any{
		"openapi": "3.0.3",
		"info": map[string]any{
			"title":       "Go API (Bolt-compatible)",
			"description": "Same endpoints as Django Bolt. Health, Roles, Users, Auth. JWT via POST /auth/login. All responses include **X-Response-Time** header. Use **Authorize** to add Bearer token.",
			"version":     "0.1.0",
		},
		"servers": []map[string]any{
			{"url": baseURL, "description": "API server"},
		},
		"components": map[string]any{
			"securitySchemes": map[string]any{
				"BearerAuth": map[string]any{
					"type":         "http",
					"scheme":       "bearer",
					"bearerFormat": "JWT",
					"description":  "JWT from POST /auth/login. Click Authorize, enter: Bearer <your_access_token>",
				},
			},
			"schemas": map[string]any{
				"HealthResponse": map[string]any{
					"type": "object",
					"properties": map[string]any{"status": map[string]any{"type": "string", "example": "ok"}},
				},
				"HealthTestResponse": map[string]any{
					"type": "object",
					"properties": map[string]any{
						"status":  map[string]any{"type": "string", "example": "ok"},
						"message": map[string]any{"type": "string", "example": "Test health check endpoint"},
					},
				},
				"ReadyResponse": map[string]any{
					"type": "object",
					"properties": map[string]any{
						"status": map[string]any{"type": "string", "enum": []string{"healthy", "unhealthy"}},
						"checks": map[string]any{
							"type": "object",
							"properties": map[string]any{"database": map[string]any{"type": "string"}},
						},
					},
				},
				"RoleSchema": map[string]any{
					"type": "object",
					"properties": map[string]any{
						"code": map[string]any{"type": "string", "example": "ADMIN"},
						"name": map[string]any{"type": "string", "example": "Administrator"},
					},
				},
				"UserSchema": map[string]any{
					"type": "object",
					"properties": map[string]any{
						"id":       map[string]any{"type": "integer", "example": 1},
						"username": map[string]any{"type": "string", "example": "admin"},
						"role":     map[string]any{"type": "string", "example": "ADMIN"},
					},
				},
				"UserListResponse": map[string]any{
					"type": "object",
					"properties": map[string]any{
						"results":  map[string]any{"type": "array", "items": map[string]any{"$ref": "#/components/schemas/UserSchema"}},
						"count":    map[string]any{"type": "integer"},
						"next":     map[string]any{"type": "string", "nullable": true},
						"previous": map[string]any{"type": "string", "nullable": true},
					},
				},
				"LoginSchema": map[string]any{
					"type":     "object",
					"required": []string{"username", "password"},
					"properties": map[string]any{
						"username": map[string]any{"type": "string", "example": "admin"},
						"password": map[string]any{"type": "string", "example": "password"},
					},
				},
				"TokenSchema": map[string]any{
					"type": "object",
					"properties": map[string]any{
						"access_token": map[string]any{"type": "string"},
						"expires_in":   map[string]any{"type": "integer"},
						"token_type":   map[string]any{"type": "string", "example": "bearer"},
					},
				},
				"ErrorDetail": map[string]any{
					"type":       "object",
					"properties": map[string]any{"detail": map[string]any{"type": "string"}},
				},
			},
		},
		"paths": map[string]any{
			"/health": map[string]any{
				"get": map[string]any{
					"tags":        []string{"Health"},
					"summary":     "Liveness",
					"description": "Simple liveness check. Response includes X-Response-Time header.",
					"responses": map[string]any{
						"200": map[string]any{
							"description": "OK",
							"headers": map[string]any{
								"X-Response-Time": map[string]any{"schema": map[string]any{"type": "string"}, "description": "Request processing time (ms)"},
								"X-Server-Time":   map[string]any{"schema": map[string]any{"type": "string"}, "description": "UTC timestamp"},
							},
							"content": map[string]any{
								"application/json": map[string]any{
									"schema": map[string]any{"$ref": "#/components/schemas/HealthResponse"},
								},
							},
						},
					},
				},
			},
			"/health/test": map[string]any{
				"get": map[string]any{
					"tags":        []string{"Health"},
					"summary":     "Custom health check",
					"description": "Test health check endpoint (Bolt-compatible).",
					"responses": map[string]any{
						"200": map[string]any{
							"description": "OK",
							"content": map[string]any{
								"application/json": map[string]any{
									"schema": map[string]any{"$ref": "#/components/schemas/HealthTestResponse"},
								},
							},
						},
					},
				},
			},
			"/ready": map[string]any{
				"get": map[string]any{
					"tags":        []string{"Health"},
					"summary":     "Readiness",
					"description": "Readiness check (DB). Returns 503 if unhealthy.",
					"responses": map[string]any{
						"200": map[string]any{
							"description": "Healthy",
							"content": map[string]any{
								"application/json": map[string]any{
									"schema": map[string]any{"$ref": "#/components/schemas/ReadyResponse"},
								},
							},
						},
						"503": map[string]any{
							"description": "Unhealthy",
							"content": map[string]any{
								"application/json": map[string]any{
									"schema": map[string]any{"$ref": "#/components/schemas/ReadyResponse"},
								},
							},
						},
					},
				},
			},
			"/roles": map[string]any{
				"get": map[string]any{
					"tags":        []string{"Roles"},
					"summary":     "List roles",
					"description": "List all roles (ADMIN, SHOPKEEPER, CUSTOMER).",
					"responses": map[string]any{
						"200": map[string]any{
							"description": "OK",
							"content": map[string]any{
								"application/json": map[string]any{
									"schema": map[string]any{
										"type":  "array",
										"items": map[string]any{"$ref": "#/components/schemas/RoleSchema"},
									},
								},
							},
						},
					},
				},
			},
			"/roles/code/{code}": map[string]any{
				"get": map[string]any{
					"tags": []string{"Roles"},
					"summary": "Get role by code",
					"parameters": []map[string]any{
						{"name": "code", "in": "path", "required": true, "schema": map[string]any{"type": "string", "example": "ADMIN"}},
					},
					"responses": map[string]any{
						"200": map[string]any{
							"description": "OK",
							"content": map[string]any{
								"application/json": map[string]any{
									"schema": map[string]any{"$ref": "#/components/schemas/RoleSchema"},
								},
							},
						},
						"404": map[string]any{
							"description": "Role not found",
							"content": map[string]any{
								"application/json": map[string]any{
									"schema": map[string]any{"$ref": "#/components/schemas/ErrorDetail"},
								},
							},
						},
					},
				},
			},
			"/users": map[string]any{
				"get": map[string]any{
					"tags":        []string{"Users"},
					"summary":     "List users",
					"description": "Paginated list with search and role filter.",
					"parameters": []map[string]any{
						{"name": "search", "in": "query", "schema": map[string]any{"type": "string"}},
						{"name": "role", "in": "query", "schema": map[string]any{"type": "string", "enum": []string{"ADMIN", "SHOPKEEPER", "CUSTOMER"}}},
						{"name": "role_code", "in": "query", "schema": map[string]any{"type": "string"}},
						{"name": "page", "in": "query", "schema": map[string]any{"type": "integer", "default": 1}},
						{"name": "page_size", "in": "query", "schema": map[string]any{"type": "integer", "default": 10}},
					},
					"responses": map[string]any{
						"200": map[string]any{
							"description": "OK",
							"content": map[string]any{
								"application/json": map[string]any{
									"schema": map[string]any{"$ref": "#/components/schemas/UserListResponse"},
								},
							},
						},
					},
				},
				"post": map[string]any{
					"tags":        []string{"Users"},
					"summary":     "Create user",
					"description": "Create user (staff only). Requires JWT.",
					"security":    []map[string]any{{"BearerAuth": []string{}}},
					"requestBody": map[string]any{
						"required": true,
						"content": map[string]any{
							"application/json": map[string]any{
								"schema": map[string]any{
									"type":     "object",
									"required": []string{"username", "password"},
									"properties": map[string]any{
										"username": map[string]any{"type": "string"},
										"password": map[string]any{"type": "string"},
										"email":    map[string]any{"type": "string"},
										"role":     map[string]any{"type": "string", "enum": []string{"ADMIN", "SHOPKEEPER", "CUSTOMER"}},
									},
								},
							},
						},
					},
					"responses": map[string]any{
						"201": map[string]any{
							"description": "Created",
							"content": map[string]any{
								"application/json": map[string]any{
									"schema": map[string]any{"$ref": "#/components/schemas/UserSchema"},
								},
							},
						},
						"400": map[string]any{
							"description": "Bad request",
							"content": map[string]any{
								"application/json": map[string]any{
									"schema": map[string]any{"$ref": "#/components/schemas/ErrorDetail"},
								},
							},
						},
						"401": map[string]any{
							"description": "Unauthorized",
							"content": map[string]any{
								"application/json": map[string]any{
									"schema": map[string]any{"$ref": "#/components/schemas/ErrorDetail"},
								},
							},
						},
					},
				},
			},
			"/users/{user_id}": map[string]any{
				"get": map[string]any{
					"tags": []string{"Users"},
					"summary": "Get user by ID",
					"parameters": []map[string]any{
						{"name": "user_id", "in": "path", "required": true, "schema": map[string]any{"type": "integer"}},
					},
					"responses": map[string]any{
						"200": map[string]any{
							"description": "OK",
							"content": map[string]any{
								"application/json": map[string]any{
									"schema": map[string]any{"$ref": "#/components/schemas/UserSchema"},
								},
							},
						},
						"404": map[string]any{
							"description": "User not found",
							"content": map[string]any{
								"application/json": map[string]any{
									"schema": map[string]any{"$ref": "#/components/schemas/ErrorDetail"},
								},
							},
						},
					},
				},
			},
			"/users/me": map[string]any{
				"get": map[string]any{
					"tags":        []string{"Users"},
					"summary":     "Current user",
					"description": "Get current authenticated user. Requires JWT.",
					"security":    []map[string]any{{"BearerAuth": []string{}}},
					"responses": map[string]any{
						"200": map[string]any{
							"description": "OK",
							"content": map[string]any{
								"application/json": map[string]any{
									"schema": map[string]any{"$ref": "#/components/schemas/UserSchema"},
								},
							},
						},
						"401": map[string]any{
							"description": "Unauthorized",
							"content": map[string]any{
								"application/json": map[string]any{
									"schema": map[string]any{"$ref": "#/components/schemas/ErrorDetail"},
								},
							},
						},
					},
				},
			},
			"/auth/login": map[string]any{
				"post": map[string]any{
					"tags":        []string{"Auth"},
					"summary":     "Login (JWT)",
					"description": "Obtain JWT access token. No auth required.",
					"requestBody": map[string]any{
						"required": true,
						"content": map[string]any{
							"application/json": map[string]any{
								"schema": map[string]any{"$ref": "#/components/schemas/LoginSchema"},
							},
						},
					},
					"responses": map[string]any{
						"200": map[string]any{
							"description": "OK",
							"content": map[string]any{
								"application/json": map[string]any{
									"schema": map[string]any{"$ref": "#/components/schemas/TokenSchema"},
								},
							},
						},
						"400": map[string]any{
							"description": "Bad request",
							"content": map[string]any{
								"application/json": map[string]any{
									"schema": map[string]any{"$ref": "#/components/schemas/ErrorDetail"},
								},
							},
						},
						"401": map[string]any{
							"description": "Invalid credentials",
							"content": map[string]any{
								"application/json": map[string]any{
									"schema": map[string]any{"$ref": "#/components/schemas/ErrorDetail"},
								},
							},
						},
					},
				},
			},
		},
	}
}

// ServeOpenAPI returns a handler that serves the OpenAPI spec as JSON.
// baseURL: e.g. "http://localhost:8005". If empty, uses request Host.
func ServeOpenAPI(defaultBaseURL string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		baseURL := defaultBaseURL
		if baseURL == "" && r.Host != "" {
			scheme := "http"
			if r.TLS != nil {
				scheme = "https"
			}
			baseURL = scheme + "://" + r.Host
		}
		if baseURL == "" {
			baseURL = "http://localhost:8005"
		}
		spec := OpenAPI(baseURL)
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(spec)
	}
}

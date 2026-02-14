package handlers

import (
	"context"
	"encoding/json"
	"net/http"

	"high_performance_api_benchmark/internal/database"
)

// Health returns liveness check.
func Health(w http.ResponseWriter, r *http.Request) {
	writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
}

// HealthTest returns custom health check (Bolt-compatible).
func HealthTest(w http.ResponseWriter, r *http.Request) {
	writeJSON(w, http.StatusOK, map[string]string{
		"status":  "ok",
		"message": "Test health check endpoint",
	})
}

// Ready returns readiness check (DB). Returns 503 if unhealthy.
func Ready(w http.ResponseWriter, r *http.Request) {
	pool := database.Pool()
	if pool == nil {
		writeJSON(w, http.StatusServiceUnavailable, map[string]any{
			"status": "unhealthy",
			"checks": map[string]string{"database": "error"},
		})
		return
	}
	if err := pool.Ping(context.Background()); err != nil {
		writeJSON(w, http.StatusServiceUnavailable, map[string]any{
			"status": "unhealthy",
			"checks": map[string]string{"database": "error"},
		})
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{
		"status": "healthy",
		"checks": map[string]string{"database": "ok"},
	})
}

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}

package middleware

import (
	"fmt"
	"net/http"
	"time"
)

// Timing adds X-Server-Time (UTC) and X-Response-Time (ms) to every response.
// Bolt-compatible observability headers.
func Timing(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		rec := &responseRecorder{ResponseWriter: w, statusCode: http.StatusOK}
		next.ServeHTTP(rec, r)
		durationMs := time.Since(start).Seconds() * 1000
		serverTime := time.Now().UTC().Format("2006-01-02T15:04:05.000Z")
		rec.Header().Set("X-Server-Time", serverTime)
		rec.Header().Set("X-Response-Time", fmt.Sprintf("%.2fms", durationMs))
	})
}

type responseRecorder struct {
	http.ResponseWriter
	statusCode int
}

func (r *responseRecorder) WriteHeader(code int) {
	r.statusCode = code
	r.ResponseWriter.WriteHeader(code)
}

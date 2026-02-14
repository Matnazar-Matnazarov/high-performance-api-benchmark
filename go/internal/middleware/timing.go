package middleware

import (
	"fmt"
	"net/http"
	"sync"
	"time"
)

// Timing adds X-Server-Time (UTC) and X-Response-Time (ms) to every response.
// Bolt-compatible observability headers. Works for all endpoints.
func Timing(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		rec := &responseRecorder{
			ResponseWriter: w,
			statusCode:     http.StatusOK,
			start:          start,
		}
		next.ServeHTTP(rec, r)
	})
}

type responseRecorder struct {
	http.ResponseWriter
	statusCode   int
	start        time.Time
	headerWriter sync.Once
}

func (r *responseRecorder) WriteHeader(code int) {
	r.headerWriter.Do(func() {
		r.statusCode = code
		durationMs := time.Since(r.start).Seconds() * 1000
		serverTime := time.Now().UTC().Format("2006-01-02T15:04:05.000Z")
		r.Header().Set("X-Server-Time", serverTime)
		r.Header().Set("X-Response-Time", fmt.Sprintf("%.2fms", durationMs))
	})
	r.ResponseWriter.WriteHeader(code)
}

func (r *responseRecorder) Write(b []byte) (int, error) {
	// Implicit 200 if handler writes without calling WriteHeader
	r.headerWriter.Do(func() {
		durationMs := time.Since(r.start).Seconds() * 1000
		serverTime := time.Now().UTC().Format("2006-01-02T15:04:05.000Z")
		r.Header().Set("X-Server-Time", serverTime)
		r.Header().Set("X-Response-Time", fmt.Sprintf("%.2fms", durationMs))
		r.ResponseWriter.WriteHeader(r.statusCode)
	})
	return r.ResponseWriter.Write(b)
}

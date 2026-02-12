// Load test for Django Bolt and DRF API endpoints.
//
// Benchmarks multiple endpoints in parallel. Measures req/sec, success/fail,
// and latency percentiles (p50, p95, p99).
//
// Usage:
//
//	./loadtest -api bolt -duration 5s -concurrency 50
//	./loadtest -api drf -duration 5s -concurrency 50
//	./loadtest -api bolt -endpoints /health,/health/test,/ready,/users,/roles
package main

import (
	"flag"
	"fmt"
	"net/http"
	"sort"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

type result struct {
	success    bool
	statusCode int
	latencyMs  float64
}

func percentileIdx(n int, p int) int {
	if n <= 0 {
		return 0
	}
	idx := int(float64(n-1) * float64(p) / 100)
	if idx < 0 {
		return 0
	}
	if idx >= n {
		return n - 1
	}
	return idx
}

func buildURL(base, path string) string {
	base = strings.TrimSuffix(base, "/")
	if !strings.HasPrefix(path, "/") {
		path = "/" + path
	}
	return base + path
}

func worker(client *http.Client, url string, stop <-chan struct{}, total, success, fail *atomic.Int64, latencies *[]float64, latMu *sync.Mutex) {
	for {
		select {
		case <-stop:
			return
		default:
			start := time.Now()
			resp, err := client.Get(url)
			elapsed := time.Since(start).Seconds() * 1000

			total.Add(1)
			if err != nil {
				fail.Add(1)
				continue
			}
			ok := resp.StatusCode >= 200 && resp.StatusCode < 300
			resp.Body.Close()

			if ok {
				success.Add(1)
				latMu.Lock()
				*latencies = append(*latencies, elapsed)
				latMu.Unlock()
			} else {
				fail.Add(1)
			}
		}
	}
}

func main() {
	api := flag.String("api", "bolt", "API type: bolt or drf")
	url := flag.String("url", "", "Base URL (default: bolt=8000, drf=8001)")
	endpoints := flag.String("endpoints", "", "Comma-separated endpoints (default per API)")
	dur := flag.Duration("duration", 5*time.Second, "Test duration")
	concurrency := flag.Int("concurrency", 20, "Concurrent workers")
	flag.Parse()

	baseURL := *url
	if baseURL == "" {
		if *api == "drf" {
			baseURL = "http://localhost:8001"
		} else {
			baseURL = "http://localhost:8000"
		}
	}

	eps := parseEndpoints(*api, *endpoints)

	client := &http.Client{Timeout: 30 * time.Second}

	var total, success, fail atomic.Int64
	latencies := make([]float64, 0, 200_000)
	var latMu sync.Mutex

	stop := make(chan struct{})
	var wg sync.WaitGroup

	for i := 0; i < *concurrency; i++ {
		ep := eps[i%len(eps)]
		fullURL := buildURL(baseURL, ep)
		wg.Add(1)
		go func() {
			defer wg.Done()
			worker(client, fullURL, stop, &total, &success, &fail, &latencies, &latMu)
		}()
	}

	fmt.Printf("Load test: %s @ %s\n", strings.ToUpper(*api), baseURL)
	fmt.Printf("  Endpoints: %s\n", strings.Join(eps, ", "))
	fmt.Printf("  Duration: %s | Concurrency: %d\n", dur.String(), *concurrency)
	fmt.Println("--------------------------------------------------")

	time.Sleep(*dur)
	close(stop)
	wg.Wait()

	t := total.Load()
	s := success.Load()
	f := fail.Load()
	durSec := (*dur).Seconds()
	rps := 0.0
	if durSec > 0 {
		rps = float64(t) / durSec
	}

	successRate := 0.0
	if t > 0 {
		successRate = float64(s) / float64(t) * 100
	}
	failRate := 0.0
	if t > 0 {
		failRate = float64(f) / float64(t) * 100
	}

	fmt.Printf("Total requests:  %d\n", t)
	fmt.Printf("Success (2xx):  %d\n", s)
	fmt.Printf("Fail:           %d\n", f)
	fmt.Printf("Success rate:   %.1f%%\n", successRate)
	fmt.Printf("Fail rate:      %.1f%%\n", failRate)
	fmt.Printf("Requests/sec:   %.1f\n", rps)

	if len(latencies) > 0 {
		sort.Float64s(latencies)
		n := len(latencies)
		p50 := latencies[percentileIdx(n, 50)]
		p95 := latencies[percentileIdx(n, 95)]
		p99 := latencies[percentileIdx(n, 99)]
		fmt.Printf("Latency (ms):   p50=%.1f p95=%.1f p99=%.1f\n", p50, p95, p99)
	}
}

func parseEndpoints(api, raw string) []string {
	if raw != "" {
		parts := strings.Split(raw, ",")
		out := make([]string, 0, len(parts))
		for _, p := range parts {
			p = strings.TrimSpace(p)
			if p != "" {
				out = append(out, p)
			}
		}
		if len(out) > 0 {
			return out
		}
	}

	if api == "drf" {
		return []string{
			"/drf/health/",
			"/drf/health/test/",
			"/drf/ready/",
			"/drf/users/",
			"/drf/roles/",
		}
	}

	return []string{
		"/health",
		"/health/test",
		"/ready",
		"/users",
		"/roles",
	}
}

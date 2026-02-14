package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"

	"high_performance_api_benchmark/internal/config"
	"high_performance_api_benchmark/internal/database"
	"high_performance_api_benchmark/internal/docs"
	"high_performance_api_benchmark/internal/handlers"
	"high_performance_api_benchmark/internal/middleware"

	"github.com/go-chi/chi/v5"
)

func main() {
	cfg := config.Load()
	if err := database.Init(cfg); err != nil {
		log.Fatalf("Database init failed: %v", err)
	}
	defer database.Close()

	r := chi.NewRouter()
	r.Use(middleware.Timing)

	// Swagger UI & OpenAPI (Bolt-compatible, X-Response-Time on all responses)
	r.Get("/swagger-ui/", docs.SwaggerUIHandler())
	r.Get("/swagger-ui", func(w http.ResponseWriter, r *http.Request) {
		http.Redirect(w, r, "/swagger-ui/", http.StatusMovedPermanently)
	})
	r.Get("/api-docs/openapi.json", docs.ServeOpenAPI(""))

	// Health
	r.Get("/health", handlers.Health)
	r.Get("/health/test", handlers.HealthTest)
	r.Get("/ready", handlers.Ready)

	// Auth
	r.Post("/auth/login", handlers.Login)

	// Roles
	r.Get("/roles", handlers.ListRoles)
	r.Get("/roles/code/{code}", handlers.GetRoleByCode)

	// Users - order matters: /users/me before /users/{user_id}
	r.Get("/users", handlers.ListUsers)
	r.Group(func(r chi.Router) {
		r.Use(middleware.JWT)
		r.Get("/users/me", handlers.GetMe)
		r.With(middleware.RequireStaff).Post("/users", handlers.CreateUser)
	})
	r.Get("/users/{user_id}", handlers.GetUser)

	addr := fmt.Sprintf(":%d", cfg.AppPort)
	srv := &http.Server{Addr: addr, Handler: r}

	go func() {
		log.Printf("Go API listening on %s", addr)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Server error: %v", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("Shutting down...")
	if err := srv.Shutdown(context.Background()); err != nil {
		log.Printf("Shutdown error: %v", err)
	}
	log.Println("Bye")
}

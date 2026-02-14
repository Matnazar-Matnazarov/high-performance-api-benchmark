package database

import (
	"context"
	"fmt"

	"high_performance_api_benchmark/internal/config"

	"github.com/jackc/pgx/v5/pgxpool"
)

var pool *pgxpool.Pool

// Init creates the connection pool.
func Init(cfg *config.Config) error {
	connStr := fmt.Sprintf(
		"postgres://%s:%s@%s:%d/%s",
		cfg.DBUser, cfg.DBPassword, cfg.DBHost, cfg.DBPort, cfg.DBName,
	)
	var err error
	pool, err = pgxpool.New(context.Background(), connStr)
	if err != nil {
		return fmt.Errorf("database init: %w", err)
	}
	return pool.Ping(context.Background())
}

// Close closes the connection pool.
func Close() {
	if pool != nil {
		pool.Close()
		pool = nil
	}
}

// Pool returns the connection pool.
func Pool() *pgxpool.Pool {
	return pool
}

package config

import (
	"os"
	"path/filepath"
	"strconv"

	"github.com/joho/godotenv"
)

// Config holds application configuration.
type Config struct {
	DBName     string
	DBUser     string
	DBPassword string
	DBHost     string
	DBPort     int
	AppPort    int
	JWTSecret  string
	JWTExpires int
}

// Load reads configuration from environment.
func Load() *Config {
	// Load .env from project root (when run from go/ dir: ../.env)
	_ = godotenv.Load(filepath.Join("..", ".env"))
	return &Config{
		DBName:     getEnv("DB_NAME", "bolt_test"),
		DBUser:     getEnv("DB_USER", "postgres"),
		DBPassword: getEnv("DB_PASSWORD", ""),
		DBHost:     getEnv("DB_HOST", "localhost"),
		DBPort:     getEnvInt("DB_PORT", 5432),
		AppPort:    getEnvInt("GO_PORT", 8005),
		JWTSecret:  getEnv("BOLT_JWT_SECRET", getEnv("SECRET_KEY", "change-me-in-production")),
		JWTExpires: getEnvInt("BOLT_JWT_EXPIRES_SECONDS", 3600),
	}
}

func getEnv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

func getEnvInt(key string, fallback int) int {
	if v := os.Getenv(key); v != "" {
		if i, err := strconv.Atoi(v); err == nil {
			return i
		}
	}
	return fallback
}

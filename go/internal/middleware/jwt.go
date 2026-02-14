package middleware

import (
	"context"
	"encoding/json"
	"net/http"
	"strings"

	"high_performance_api_benchmark/internal/config"

	"github.com/golang-jwt/jwt/v5"
)

type contextKey string

const UserContextKey contextKey = "user"

// UserInfo holds authenticated user data.
type UserInfo struct {
	ID       int
	Username string
	Role     string
	IsStaff  bool
}

// JWT validates Bearer token and sets user in context.
func JWT(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		auth := r.Header.Get("Authorization")
		if auth == "" || !strings.HasPrefix(auth, "Bearer ") {
			writeJSONError(w, http.StatusUnauthorized, "Missing or invalid Authorization header")
			return
		}
		tokenStr := strings.TrimSpace(auth[7:])
		if tokenStr == "" {
			writeJSONError(w, http.StatusUnauthorized, "Missing token")
			return
		}

		cfg := config.Load()
		token, err := jwt.Parse(tokenStr, func(t *jwt.Token) (any, error) {
			return []byte(cfg.JWTSecret), nil
		})
		if err != nil || !token.Valid {
			writeJSONError(w, http.StatusUnauthorized, "Invalid token")
			return
		}

		claims, ok := token.Claims.(jwt.MapClaims)
		if !ok {
			writeJSONError(w, http.StatusUnauthorized, "Invalid token claims")
			return
		}

		userID, _ := claims["user_id"].(float64)
		username, _ := claims["username"].(string)
		role, _ := claims["role"].(string)
		isStaff, _ := claims["is_staff"].(bool)
		if userID == 0 || username == "" {
			writeJSONError(w, http.StatusUnauthorized, "Invalid token payload")
			return
		}
		if role == "" {
			role = "CUSTOMER"
		}

		user := UserInfo{
			ID:       int(userID),
			Username: username,
			Role:     role,
			IsStaff:  isStaff,
		}
		ctx := context.WithValue(r.Context(), UserContextKey, user)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

// RequireStaff ensures user is staff (must be used after JWT).
func RequireStaff(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		user, ok := r.Context().Value(UserContextKey).(UserInfo)
		if !ok || !user.IsStaff {
			writeJSONError(w, http.StatusForbidden, "Staff access required")
			return
		}
		next.ServeHTTP(w, r)
	})
}

func writeJSONError(w http.ResponseWriter, status int, detail string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(map[string]string{"detail": detail})
}

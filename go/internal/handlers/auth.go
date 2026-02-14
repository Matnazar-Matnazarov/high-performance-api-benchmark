package handlers

import (
	"encoding/json"
	"net/http"
	"time"

	"high_performance_api_benchmark/internal/config"
	"high_performance_api_benchmark/internal/database"

	"github.com/alexandrevicenzi/unchained"
	"github.com/golang-jwt/jwt/v5"
)

// LoginRequest is the request body for POST /auth/login.
type LoginRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

// LoginResponse is the JWT token response (Bolt-compatible).
type LoginResponse struct {
	AccessToken string `json:"access_token"`
	ExpiresIn   int    `json:"expires_in"`
	TokenType   string `json:"token_type"`
}

// Login handles POST /auth/login - Bolt-compatible JWT.
func Login(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		writeJSON(w, http.StatusMethodNotAllowed, map[string]string{"detail": "Method not allowed"})
		return
	}
	var body LoginRequest
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"detail": "Invalid request body"})
		return
	}
	username := body.Username
	password := body.Password
	if username == "" || password == "" {
		writeJSON(w, http.StatusBadRequest, map[string]string{"detail": "username and password required"})
		return
	}

	pool := database.Pool()
	if pool == nil {
		writeJSON(w, http.StatusInternalServerError, map[string]string{"detail": "Database not available"})
		return
	}

	var id int
	var storedHash, role string
	var isStaff bool
	err := pool.QueryRow(r.Context(),
		"SELECT id, password, COALESCE(role, 'CUSTOMER'), is_staff FROM accounts_user WHERE username = $1",
		username,
	).Scan(&id, &storedHash, &role, &isStaff)
	if err != nil {
		writeJSON(w, http.StatusUnauthorized, map[string]string{"detail": "Invalid credentials"})
		return
	}

	ok, err := unchained.CheckPassword(password, storedHash)
	if err != nil || !ok {
		writeJSON(w, http.StatusUnauthorized, map[string]string{"detail": "Invalid credentials"})
		return
	}

	cfg := config.Load()
	claims := jwt.MapClaims{
		"user_id":  id,
		"username": username,
		"role":     role,
		"is_staff": isStaff,
		"exp":      time.Now().Add(time.Duration(cfg.JWTExpires) * time.Second).Unix(),
		"iat":      time.Now().Unix(),
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	accessToken, err := token.SignedString([]byte(cfg.JWTSecret))
	if err != nil {
		writeJSON(w, http.StatusInternalServerError, map[string]string{"detail": "Token creation failed"})
		return
	}

	writeJSON(w, http.StatusOK, LoginResponse{
		AccessToken: accessToken,
		ExpiresIn:   cfg.JWTExpires,
		TokenType:   "bearer",
	})
}

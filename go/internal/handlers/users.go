package handlers

import (
	"encoding/json"
	"net/http"
	"strconv"
	"strings"

	"high_performance_api_benchmark/internal/database"
	"high_performance_api_benchmark/internal/middleware"

	"github.com/alexandrevicenzi/unchained"
	"github.com/go-chi/chi/v5"
)

var validRoles = map[string]bool{"ADMIN": true, "SHOPKEEPER": true, "CUSTOMER": true}

// UserSchema is the user response model.
type UserSchema struct {
	ID       int    `json:"id"`
	Username string `json:"username"`
	Role     string `json:"role"`
}

// UserListResponse is the paginated user list (Bolt-compatible).
type UserListResponse struct {
	Results  []UserSchema `json:"results"`
	Count    int          `json:"count"`
	Next     *string      `json:"next"`
	Previous *string      `json:"previous"`
}

// ListUsers returns paginated users with search and role filter.
func ListUsers(w http.ResponseWriter, r *http.Request) {
	pool := database.Pool()
	if pool == nil {
		writeJSON(w, http.StatusInternalServerError, map[string]string{"detail": "Database not available"})
		return
	}

	q := r.URL.Query()
	search := strings.TrimSpace(q.Get("search"))
	roleFilter := strings.TrimSpace(strings.ToUpper(q.Get("role")))
	if roleFilter == "" {
		roleFilter = strings.TrimSpace(strings.ToUpper(q.Get("role_code")))
	}
	if roleFilter != "" && !validRoles[roleFilter] {
		roleFilter = ""
	}

	page := 1
	if p := q.Get("page"); p != "" {
		if i, err := strconv.Atoi(p); err == nil && i >= 1 {
			page = i
		}
	}
	pageSize := 10
	if ps := q.Get("page_size"); ps != "" {
		if i, err := strconv.Atoi(ps); err == nil && i >= 1 && i <= 100 {
			pageSize = i
		}
	}
	offset := (page - 1) * pageSize

	var conditions []string
	args := []any{}
	argIdx := 1
	if search != "" {
		conditions = append(conditions, "username ILIKE $"+strconv.Itoa(argIdx))
		args = append(args, "%"+search+"%")
		argIdx++
	}
	if roleFilter != "" {
		conditions = append(conditions, "role = $"+strconv.Itoa(argIdx))
		args = append(args, roleFilter)
		argIdx++
	}
	whereClause := "1=1"
	if len(conditions) > 0 {
		whereClause = strings.Join(conditions, " AND ")
	}

	// Count
	var total int
	countQuery := "SELECT COUNT(*)::int FROM accounts_user WHERE " + whereClause
	err := pool.QueryRow(r.Context(), countQuery, args...).Scan(&total)
	if err != nil {
		writeJSON(w, http.StatusInternalServerError, map[string]string{"detail": "Database error"})
		return
	}

	// Fetch page
	args = append(args, pageSize, offset)
	limitArg := argIdx
	offsetArg := argIdx + 1
	rows, err := pool.Query(r.Context(),
		`SELECT id, username, COALESCE(role, 'CUSTOMER') as role FROM accounts_user 
		 WHERE `+whereClause+` ORDER BY id LIMIT $`+strconv.Itoa(limitArg)+` OFFSET $`+strconv.Itoa(offsetArg),
		args...,
	)
	if err != nil {
		writeJSON(w, http.StatusInternalServerError, map[string]string{"detail": "Database error"})
		return
	}
	defer rows.Close()

	var results []UserSchema
	for rows.Next() {
		var u UserSchema
		if err := rows.Scan(&u.ID, &u.Username, &u.Role); err != nil {
			continue
		}
		results = append(results, u)
	}

	var nextURL, prevURL *string
	if offset+len(results) < total {
		s := "?page=" + strconv.Itoa(page+1) + "&page_size=" + strconv.Itoa(pageSize)
		nextURL = &s
	}
	if page > 1 {
		s := "?page=" + strconv.Itoa(page-1) + "&page_size=" + strconv.Itoa(pageSize)
		prevURL = &s
	}

	writeJSON(w, http.StatusOK, UserListResponse{
		Results:  results,
		Count:    total,
		Next:     nextURL,
		Previous: prevURL,
	})
}

// GetUser returns user by ID.
func GetUser(w http.ResponseWriter, r *http.Request) {
	userIDStr := chi.URLParam(r, "user_id")
	userID, err := strconv.Atoi(userIDStr)
	if err != nil {
		writeJSON(w, http.StatusNotFound, map[string]string{"detail": "User not found"})
		return
	}

	pool := database.Pool()
	if pool == nil {
		writeJSON(w, http.StatusInternalServerError, map[string]string{"detail": "Database not available"})
		return
	}

	var u UserSchema
	err = pool.QueryRow(r.Context(),
		"SELECT id, username, COALESCE(role, 'CUSTOMER') FROM accounts_user WHERE id = $1",
		userID,
	).Scan(&u.ID, &u.Username, &u.Role)
	if err != nil {
		writeJSON(w, http.StatusNotFound, map[string]string{"detail": "User not found"})
		return
	}
	writeJSON(w, http.StatusOK, u)
}

// GetMe returns current user (requires JWT).
func GetMe(w http.ResponseWriter, r *http.Request) {
	user, ok := r.Context().Value(middleware.UserContextKey).(middleware.UserInfo)
	if !ok {
		writeJSON(w, http.StatusUnauthorized, map[string]string{"detail": "Unauthorized"})
		return
	}

	pool := database.Pool()
	if pool == nil {
		writeJSON(w, http.StatusInternalServerError, map[string]string{"detail": "Database not available"})
		return
	}

	var u UserSchema
	err := pool.QueryRow(r.Context(),
		"SELECT id, username, COALESCE(role, 'CUSTOMER') FROM accounts_user WHERE id = $1",
		user.ID,
	).Scan(&u.ID, &u.Username, &u.Role)
	if err != nil {
		writeJSON(w, http.StatusNotFound, map[string]string{"detail": "User not found"})
		return
	}
	writeJSON(w, http.StatusOK, u)
}

// UserCreateRequest is the request body for POST /users.
type UserCreateRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
	Email    string `json:"email"`
	Role     string `json:"role"`
}

// CreateUser creates a new user (staff only).
func CreateUser(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		writeJSON(w, http.StatusMethodNotAllowed, map[string]string{"detail": "Method not allowed"})
		return
	}

	var body UserCreateRequest
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"detail": "Invalid request body"})
		return
	}
	if body.Username == "" || body.Password == "" {
		writeJSON(w, http.StatusBadRequest, map[string]string{"detail": "username and password required"})
		return
	}

	role := strings.TrimSpace(strings.ToUpper(body.Role))
	if role == "" {
		role = "CUSTOMER"
	}
	if !validRoles[role] {
		writeJSON(w, http.StatusBadRequest, map[string]string{
			"detail": "Invalid role. Must be one of: ADMIN, SHOPKEEPER, CUSTOMER",
		})
		return
	}

	pool := database.Pool()
	if pool == nil {
		writeJSON(w, http.StatusInternalServerError, map[string]string{"detail": "Database not available"})
		return
	}

	// Django-compatible password hashing (use unchained)
	hashed, err := unchained.MakePassword(body.Password, unchained.GetRandomString(12), "default")
	if err != nil {
		writeJSON(w, http.StatusInternalServerError, map[string]string{"detail": "Password hashing failed"})
		return
	}

	email := body.Email
	if email == "" {
		email = body.Username + "@example.com"
	}

	var id int
	err = pool.QueryRow(r.Context(),
		`INSERT INTO accounts_user (username, password, email, first_name, last_name, role, is_staff, is_active, is_superuser, date_joined)
		 VALUES ($1, $2, $3, '', '', $4, false, true, false, NOW())
		 RETURNING id`,
		body.Username, hashed, email, role,
	).Scan(&id)
	if err != nil {
		if strings.Contains(err.Error(), "duplicate") || strings.Contains(err.Error(), "unique") {
			writeJSON(w, http.StatusBadRequest, map[string]string{"detail": "Username already exists"})
			return
		}
		writeJSON(w, http.StatusInternalServerError, map[string]string{"detail": "Create failed"})
		return
	}

	writeJSON(w, http.StatusCreated, UserSchema{
		ID:       id,
		Username: body.Username,
		Role:     role,
	})
}

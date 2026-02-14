package handlers

import (
	"net/http"
	"strings"

	"github.com/go-chi/chi/v5"
)

var roleChoices = []struct {
	Code string `json:"code"`
	Name string `json:"name"`
}{
	{"ADMIN", "Administrator"},
	{"SHOPKEEPER", "Shopkeeper"},
	{"CUSTOMER", "Customer"},
}

// ListRoles returns all roles (Bolt-compatible).
func ListRoles(w http.ResponseWriter, r *http.Request) {
	writeJSON(w, http.StatusOK, roleChoices)
}

// GetRoleByCode returns role by code.
func GetRoleByCode(w http.ResponseWriter, req *http.Request) {
	code := strings.TrimSpace(strings.ToUpper(chi.URLParam(req, "code")))
	for _, role := range roleChoices {
		if role.Code == code {
			writeJSON(w, http.StatusOK, role)
			return
		}
	}
	writeJSON(w, http.StatusNotFound, map[string]string{"detail": "Role not found"})
}

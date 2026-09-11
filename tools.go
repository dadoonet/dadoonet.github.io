//go:build tools

// Dependabot gomod only bumps *direct* requires. This blank import keeps
// hugo-theme-devrel direct after `go mod tidy` / `hugo mod tidy`.
package tools

import _ "github.com/dadoonet/hugo-theme-devrel"

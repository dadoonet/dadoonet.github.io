module github.com/dadoonet/dadoonet.github.io

go 1.22.2

// Direct (no // indirect) so Dependabot gomod will propose version bumps.
// tools.go imports the module; that import needs theme package `devrel`.
require github.com/dadoonet/hugo-theme-devrel v0.1.1-0.20260910094858-ca65e0580b35

package adapter

import "context"

// Adapter defines the interface all source adapters must implement.
type Adapter interface {
	// Name returns the adapter name.
	Name() string

	// Connect establishes a connection to the data source.
	Connect(ctx context.Context) error

	// Close shuts down the connection.
	Close() error
}

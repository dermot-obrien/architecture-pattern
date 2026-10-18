# Cache aside

The application reads through a cache it manages itself, so the primary store is read only on a miss.

- Application: owns the read path and fills the cache
- Cache: holds recently read items for a short time
- Primary Store: the system of record

# Version History

## 0.1.0
### Added
- Added methods for user registration and authentication
- Added methods for generating and decoding JWT tokens

## 0.1.1
### Added
- Added basic documentation to the project
### Changed
- Structure changed. Test structure now matches the application structure. `main.py` file renamed to `service.py`

## 0.2.0
### Added
- Added token verification method
- Added API
- Added integration tests
### Changed
- Structure changed. Test structure now matches the application structure. Entry point is `main.py`. All business logic moved to the `service` folder.

## 0.2.1
### Added
- Added Dockerfile
- Added CI step for container build and push to DockerHub

## 0.2.2
### Added
- Added Health check

## 0.3.0
### Added
- Added Kafka integration

## 0.4.0
### Added
- Added database
- Added tests for database queries

## 0.5.0
### Added
- Added manifests for Kubernetes deployment
- Added Helm charts

## 0.6.0
### Added
- Added metrics for Prometheus

## 0.6.1
### Added
- Added tracing

## 0.7.0
### Changed
- Tokens are now stored in Redis
- Database structure changed (token table removed), corresponding migration created

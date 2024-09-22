[![main](https://github.com/inferno681/shift_auth_service/actions/workflows/main.yaml/badge.svg?branch=main)](https://github.com/inferno681/shift_auth_service/actions/workflows/main.yaml)
[![codecov](https://codecov.io/gh/inferno681/shift_auth_service/graph/badge.svg?token=P80YM7D0MW)](https://codecov.io/gh/inferno681/shift_auth_service)
# Auth service

Authorization service.

## Implemented features

### Registration

Based on a login and password, it creates a new user record in the storage. Returns a JWT token as a response.

### Authorization

Based on a login and password, it checks for the user in the storage. Then:
- If the JWT token is not in the storage, it creates a new one and saves it to the storage.
- If the JWT token is already in the storage, it updates it.
It returns a JWT token as a response.
If the incoming data is incorrect, it returns `None`.

### Token validation

In response to the provided token, it returns the user ID and a response indicating whether the token is valid.

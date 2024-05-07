# crawler_monitoring
```python
basic_auth_document = {
    'url': 'https://www.example-basic.com',
    'timeout': 10,
    'max_threads': 10,
    'auth_type': 'basic',
    'credentials': {'username': 'user1', 'password': 'password1'}
}
digest_auth_document = {
    'url': 'https://www.example-digest.com',
    'timeout': 10,
    'max_threads': 10,
    'auth_type': 'digest',
    'credentials': {'username': 'user2', 'password': 'password2'}
}
bearer_auth_document = {
    'url': 'https://www.example-bearer.com',
    'timeout': 10,
    'max_threads': 10,
    'auth_type': 'bearer',
    'credentials': {'token': 'bearer_token_here'}
}
form_auth_document = {
    'url': 'https://www.example-form.com',
    'timeout': 10,
    'max_threads': 10,
    'auth_type': 'form',
    'login_url': 'https://www.example-form.com/login',
    'form_data': {'username_field': 'user3', 'password_field': 'password3', 'other_field': 'value'},
    'credentials': {}  # Credentials might not be stored directly in the document for form-based auth
}
```

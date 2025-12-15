import secrets


def generate_key():\
    return 'sk-'+ secrets.token_urlsafe(16)


print(generate_key())
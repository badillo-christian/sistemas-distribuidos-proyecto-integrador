from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Genera las claves para el servidor
server_private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
server_private_pem = server_private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)
server_public_key = server_private_key.public_key()
server_public_pem = server_public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)

# Genera las claves para el cliente
client_private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
client_private_pem = client_private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)
client_public_key = client_private_key.public_key()
client_public_pem = client_public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)

# Guarda las claves en archivos
with open("server_private_key.pem", "wb") as f:
    f.write(server_private_pem)
with open("server_public_key.pem", "wb") as f:
    f.write(server_public_pem)

with open("client_private_key.pem", "wb") as f:
    f.write(client_private_pem)
with open("client_public_key.pem", "wb") as f:
    f.write(client_public_pem)

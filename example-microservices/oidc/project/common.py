import nacl.secret
import nacl.encoding
import nacl.hash
import json
from django.conf import settings


secret_box_key = nacl.encoding.HexEncoder.decode(settings.OIDC_SECRETBOX_KEY)
secret_box = nacl.secret.SecretBox(secret_box_key)


def encode_object(obj):
    obj_json = json.dumps(obj).encode()
    return nacl.encoding.URLSafeBase64Encoder.encode(
        secret_box.encrypt(obj_json)
    ).decode()


def decode_object(obj):
    obj_encrypted = nacl.encoding.URLSafeBase64Encoder.decode(obj)
    obj_decrypted = secret_box.decrypt(obj_encrypted)
    obj_json = json.loads(obj_decrypted)
    return obj_json


def extract_permissions(id_token):
    perms = id_token.get('ext', None)
    if perms is None:
        return set()
    return set(
        decode_object(
            perms
        )
    )


def hash_user_sub(user):
    return nacl.hash.sha256(str(user.id).encode(), encoder=nacl.encoding.URLSafeBase64Encoder).decode().rstrip('=')



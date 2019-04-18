import base64
import json
import logging
from time import time
import jwt
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from jwt.algorithms import RSAAlgorithm
import requests
from django.conf import settings
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from .signals import missing_user_signal

logger = logging.getLogger(__name__)


def base64_to_object(segment):
    b64string = segment
    b64string = b64string.encode('ascii')
    padded1 = b64string + b'=' * (4 - len(b64string) % 4)
    encoded_string = json.loads(base64.urlsafe_b64decode(padded1))
    return encoded_string


class OIDCProvider(object):
    client_id = None
    well_known_url = None
    _well_known = None

    def __init__(self):
        self.client_id = settings.OIDC_CLIENT_ID
        self.well_known = settings.OIDC_WELL_KNOWN_CONFIGURATION
        self._well_known = None
        self._jwks_uri_response = None
        self._jwks_keys = dict()

    @property
    def arn(self):
        return 'wallet:oidc_provider:well_known:{}'.format(self.client_id)

    @property
    def jwks_arn(self):
        return 'wallet:oidc_provider:jwks:{}'.format(self.client_id)

    @property
    def well_known_configuration(self):
        if self._well_known is None:
            result = cache.get(self.arn)
            if result is None:
                with cache.lock(self.arn, expire=60):
                    result = cache.get(self.arn)
                    if result is None:
                        result = requests.get(self.well_known).json()
                        cache.set(self.arn, result)
            self._well_known = result
        return self._well_known

    @property
    def issuer(self):
        return self.well_known_configuration.get('issuer')

    @property
    def token_endpoint(self):
        return self.well_known_configuration.get('token_endpoint')

    @property
    def jwks_uri(self):
        return self.well_known_configuration.get('jwks_uri')

    @property
    def jwks_uri_response(self):
        if self._jwks_uri_response is None:
            result = cache.get(self.jwks_arn)
            if result is None:
                with cache.lock(self.jwks_arn, expire=60):
                    result = cache.get(self.jwks_arn)
                    if result is None:
                        result = requests.get(self.jwks_uri).json()
                        cache.set(self.jwks_arn, result)
            self._jwks_uri_response = result
        return self._jwks_uri_response

    def get_key_for_kid(self, kid):
        if kid not in self._jwks_keys:
            jwks_uri_response = self.jwks_uri_response
            keys = jwks_uri_response.get('keys', list())
            for items in keys:
                if items.get('kid') == kid:
                    self._jwks_keys[kid] = items
                    break
        public_key = self._jwks_keys.get(kid)
        if public_key is None:
            msg = 'Public key not found: kid ({})'.format(kid)
            logger.error(msg)
            raise AuthenticationFailed(msg)
        return public_key


class OpenIdAuthentication(BaseAuthentication):

    def __init__(self):
        self.provider = OIDCProvider()
        self.id_token = None
        self.id_token_jwt = None
        self.id_token_kid = None

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != 'bearer'.encode():
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise AuthenticationFailed(msg)
        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise AuthenticationFailed(msg)

        if len(token.split('.')) != 3:
            msg = 'Invalid token header. No credentials wrong format. {}'.format(len(token.split('.')))
            raise AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_header(self, request):
        return 'Bearer'

    def authenticate_credentials(self, id_token):
        self.validate(id_token)
        user_model = get_user_model()
        user_sub = self.id_token_jwt.get('sub', 'unknown')
        user = user_model.objects.filter(**{user_model.USERNAME_FIELD: user_sub}).first()
        if user is None:
            with cache.lock('wallet:missing_user:{}'.format(user_sub), expire=60):
                user = user_model.objects.filter(**{user_model.USERNAME_FIELD: user_sub}).first()
                if user is None:
                    missing_user_signal.send(sender=self.__class__, username=user_sub)
                    user = user_model.objects.filter(**{user_model.USERNAME_FIELD: user_sub}).first()
        if user is None:
            raise AuthenticationFailed('Wrong Token')
        return user, self.id_token_jwt

    def validate(self, id_token):
        self.id_token = id_token
        self.id_token_jwt = get_payload_from_response(id_token, 1)
        self.id_token_kid = get_payload_from_response(self.id_token, 0).get('kid', 'unknown')
        self.validate_exp()
        self.validate_public_key()
        self.validate_iss()
        self.validate_aud()

    def validate_exp(self):
        if self.id_token_jwt.get('exp') < int(time()):
            msg = 'Validation time expired: {}'.format(self.id_token_jwt.get('exp'))
            logger.error(msg)

    def validate_public_key(self):
        public_key = self.provider.get_key_for_kid(self.id_token_kid)
        public_key = RSAAlgorithm.from_jwk(json.dumps(public_key))
        try:
            jwt.decode(
                self.id_token,
                key=public_key,
                algorithms='RS256',
                verify_signature=True,
                audience=self.provider.client_id
            )
        except jwt.ExpiredSignatureError as e:
            msg = 'Expired Signature: {}'.format(e)
            logger.exception(msg)
            raise AuthenticationFailed(msg)
        except jwt.InvalidTokenError as e:
            msg = 'Invalid Token Error: {}'.format(e)
            logger.exception(msg)
            raise AuthenticationFailed(msg)

    def validate_iss(self):
        if self.id_token_jwt.get('iss') != self.provider.issuer:
            msg = 'Wrong \'iss\' id_token value.'
            logger.error(msg)
            raise AuthenticationFailed(msg)

    def validate_aud(self):
        if self.id_token_jwt.get('aud') != self.provider.client_id:
            msg = 'Wrong \'aud\' id_token value.'
            logger.error(msg)
            raise PermissionDenied(msg)


def get_payload_from_response(response, index):
    payload = response.split('.')[index]
    payload = base64_to_object(payload)
    return payload

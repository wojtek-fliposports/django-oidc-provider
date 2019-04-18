import logging
from oidc_provider.models import Client as OidcClient
from oidc_provider.lib.utils.token import create_id_token, encode_id_token
from project.common import extract_permissions
from .idtoken import add_permissions
logger = logging.getLogger(__name__)


def get_id_token(request):
    client = OidcClient.objects.all().first()
    if client is None:
        return 'No client'
    id_token_dic = create_id_token(
        token=None,
        user=request.user,
        aud=client.client_id,
        nonce='pytech',
        request=request,
        scope=['openid'],
    )
    return encode_id_token(id_token_dic, client)


def get_id_token_permissions(self):
    return self.user_permissions_model.permissions.all()


def inject_user_token(get_response):
    def middleware(request):
        if hasattr(request, 'user') and request.user and request.user.is_authenticated:
            logger.info('Patching..')
            request.user.get_id_token = lambda: get_id_token(request)
            request.user.get_id_token_permissions = lambda: get_id_token_permissions(request.user)
            request.user.get_permissions_from_id_token = lambda: extract_permissions(
                add_permissions(dict(), request.user)
            )
        response = get_response(request)
        return response

    return middleware

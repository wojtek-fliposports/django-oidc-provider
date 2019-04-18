from project import common


def add_permissions(id_token, user, **kwargs):
    id_token['ext'] = common.encode_object(
        [x.name for x in user.user_permissions_model.permissions.all()]
    )
    return id_token

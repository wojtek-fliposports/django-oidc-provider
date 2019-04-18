from django.core.management.base import BaseCommand, no_translations
import requests
import json


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('for_user')
        parser.add_argument('username')
        parser.add_argument('password')
        parser.add_argument('client_id')
        parser.add_argument('client_secret')
        parser.add_argument('amount', type=int)

    def get_id_token(self, client_id, client_secret, username, password):
        result = requests.post(
            'http://localhost:8080/openid/token',
            data={
                'grant_type': 'password',
                'client_id': client_id,
                'client_secret': client_secret,
                'username': username,
                'password': password,
            }
        )
        result.raise_for_status()
        return result.json().get('id_token')

    def top_up_user(self, id_token, for_user, amount):
        requests.post(
            'http://localhost:8000/wallet/top_up_for_user',
            headers={
                'Authorization': 'Bearer {}'.format(id_token)
            },
            json={
                'for_user': for_user,
                'amount': amount,
            }
        ).raise_for_status()

    @no_translations
    def handle(self, *args, **options):
        for_user = options.get('for_user')
        username = options.get('username')
        password = options.get('password')
        client_id = options.get('client_id')
        client_secret = options.get('client_secret')
        amount = options.get('amount')

        id_token = self.get_id_token(client_id, client_secret, username, password)

        self.top_up_user(id_token, for_user, amount)



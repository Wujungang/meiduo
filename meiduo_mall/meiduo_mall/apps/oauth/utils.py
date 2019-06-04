from urllib.parse import urlencode
from django.conf import settings


class OAuthQQ():
    def __init__(self,client_id=None, client_secret=None, redirect_uri=None, state=None):
        self.client_id = client_id if client_id else settings.QQ_CLIENT_ID,
        print(self.client_id)
        self.redirect_uri = redirect_uri if redirect_uri else settings.QQ_REDIRECT_URI,
        self.client_secret = client_secret if client_id else settings.QQ_CLIENT_SECRET,
        self.state = state if state else settings.QQ_STATE

    def get_qq_login_url(self):
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state,
            'scope': 'get_user_info',
        }
        url = 'https://graph.qq.com/oauth2.0/authorize?' + urlencode(params)
        return url
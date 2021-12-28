import datetime

from rest_framework.authentication import TokenAuthentication


def DT_Str_DT(tiempo):
    formato = '%Y-%m-%d %H:%M:%S'
    new_tiempo = datetime.datetime.strptime(tiempo.strftime(formato), formato)
    return new_tiempo


class ExpiringTokenAuthentication(TokenAuthentication):
    def token_expire_handler(self, token):
        token_time = DT_Str_DT(token.created) - DT_Str_DT(datetime.date.today())
        close_off_time = (DT_Str_DT(datetime.date.today()) +
                datetime.timedelta(days=1))
        token_time_left = close_off_time - DT_Str_DT(token.created)
        if token_time < datetime.timedelta(seconds = 0):
            self.is_token_expired = True
        elif token_time_left < datetime.timedelta(seconds = 0):
            self.is_token_expired = True
        else:
            self.is_token_expired = False
        return self.is_token_expired

    def authenticate_credentials(self, key):
        message, token, user = None, None, None
        try:
            token = self.get_model().objects.select_related(
                'user'
                ).get(key = key)
            user = token.user
        except self.get_model().DoesNotExist:
            message = 'Token Invalid!'

        if token is not None:
            if not token.user.is_active:
                message = 'Usuario Inactive o Deleted!'

            is_expired = self.token_expire_handler(token)
            if is_expired:
                message = 'Su Token is Expired!'
        return (message, token, user)

from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from .models import Usuario


class EmailOrUsernameBackend(ModelBackend):
    """
    Backend de autenticação que permite login com username ou email
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        # Converte para minúsculas
        username = username.lower()

        try:
            # Tenta encontrar o usuário por username ou email
            user = Usuario.objects.get(
                Q(username=username) | Q(email__iexact=username)
            )
        except Usuario.DoesNotExist:
            # Executa o hasher de senha padrão para evitar timing attacks
            Usuario().set_password(password)
            return None
        except Usuario.MultipleObjectsReturned:
            # Se houver múltiplos usuários, retorna o primeiro
            user = Usuario.objects.filter(
                Q(username=username) | Q(email__iexact=username)
            ).first()

        # Verifica a senha
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

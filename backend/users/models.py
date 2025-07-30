from django.contrib.auth.models import AbstractUser
from django.db import models

FIRST_NAME_MAX_LENGTH = 150
LAST_NAME_MAX_LENGTH = 150


class User(AbstractUser):
    email = models.EmailField('Email', unique=True)
    first_name = models.CharField('Имя', max_length=FIRST_NAME_MAX_LENGTH)
    last_name = models.CharField('Фамилия', max_length=LAST_NAME_MAX_LENGTH)
    avatar = models.ImageField(upload_to='users/avatars/')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribers'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'

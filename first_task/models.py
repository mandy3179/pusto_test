from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Player(models.Model):
    """
    Модель игрока, которая хранит информацию о пользователе,
    его баллах и датах входа в систему.

    Attributes:
        player (OneToOneField): Связь с моделью User.
        first_login (DateTimeField): Дата и время первого входа игрока.
        last_login (DateTimeField): Дата и время последнего входа игрока.
        points (PositiveIntegerField): Общее количество баллов, накопленных игроком.
    """
    player = models.OneToOneField(to=User, on_delete=models.CASCADE, verbose_name='Игрок')
    first_login = models.DateTimeField(auto_now_add=True, verbose_name='Первый вход')
    last_login = models.DateTimeField(auto_now=True, verbose_name='Последний вход')
    points = models.PositiveIntegerField(default=0, verbose_name='Баллы')

    class Meta:
        verbose_name = 'Игрок'
        verbose_name_plural = 'Игроки'

    def __str__(self):
        return self.player.username

    def daily_login(self):
        """
        Начисление баллов за ежедневный вход.
        Если игрок входит в систему в первый раз за день.
        
        Raises:
            ValueError: Если игрок уже получал бонус за сегодняшний день.
        """
        today = timezone.now().date()
        last_login_date = self.last_login.date()

        if today == last_login_date:
            raise ValueError('Бонус уже получен сегодня.')

        if today > last_login_date:
            self.points += 5
            self.save()


class Boost(models.Model):
    """
    Модель буста, которая хранит информацию о различных бустах,
    их эффекте и описании.

    Attributes:
        title (CharField): Название буста.
        description (TextField): Описание буста.
        effect (IntegerField): Количество баллов, которое добавляется при применении буста.
    """
    title = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    effect = models.IntegerField(verbose_name='Эффект')

    class Meta:
        verbose_name = 'Буст'
        verbose_name_plural = 'Бусты'

    def __str__(self):
        return self.title


class PlayerBoost(models.Model):
    """
    Модель для связи игрока и буста.

    Attributes:
        player (ForeignKey): Связь с моделью Player.
        boost (ForeignKey): Связь с моделью Boost.
        active (BooleanField): Статус активности буста (активен/неактивен).
        applied_at (DateTimeField): Дата и время применения буста.
    """
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='players_boosts')
    boost = models.ForeignKey(Boost, on_delete=models.CASCADE, related_name='players_boosts')
    active = models.BooleanField(default=True, verbose_name='Активность')
    applied_at = models.DateTimeField(default=timezone.now, verbose_name='Дата применения')

    def __str__(self):
        return f'{self.player.id} - {self.boost.title} (Active: {self.active})'

    def apply_boost(self):
        """
        Применение буста к игроку, если он активен.
        Увеличивает баллы игрока на значение эффекта буста
        и деактивирует буст после применения.

        Raises:
            ValueError: Если буст неактивен для данного игрока.
        """
        if self.active:
            self.player.points += self.boost.effect
            self.player.save()

            self.active = False
            self.save
        else:
            raise ValueError('Буст неактивен для данного игрока.')

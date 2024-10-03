import random
from typing import Optional


from django.db import models
from django.db.transaction import atomic
from django.utils import timezone


class Player(models.Model):
    # тут можно использовать one_to_one с user или переопределить его
    # так же можно использовать id, который  по умолчанию генерируется
    player_id = models.CharField(max_length=100)


class Level(models.Model):
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)


class Prize(models.Model):
    title = models.CharField(max_length=52)  # добавил max_length


class PlayerLevel(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    completed = models.DateField()
    is_completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)

    @atomic
    def award_prize(self) -> Optional[str]:
        """
        Присваивает случайный приз игроку за успешное завершение уровня.
        
        Returns:
            str: Название присвоенного приза, если уровень завершен и приз был выдан.
            None: Если уровень не завершен или призов нет.
        """
        if self.is_completed:
            level_prizes = LevelPrize.objects.filter(level=self.level)
            if level_prizes.exists():
                random_prize = random.choice(level_prizes)
                random_prize.received = timezone.now().date()
                random_prize.save()
                return random_prize.prize
        return None


class LevelPrize(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)
    received = models.DateField()
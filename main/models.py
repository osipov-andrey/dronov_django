from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import Signal
from django.db.models.signals import post_save

from .utilities import send_activation_notification, get_timestamp_path, send_new_comment_notification


# ----------------------------------------------АВТОРИЗАЦИЯ-------------------------------------------------------#
user_registrated = Signal(providing_args=['instance'])


def user_registrated_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])


user_registrated.connect(user_registrated_dispatcher)


# Create your models here.


class AdvUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name='Прошел активацию?')
    send_messages = models.BooleanField(default=True, verbose_name='Слать оповещения о новых  комментариях?')

    def delete(self, *args, **kwargs):
        for bb in self.bb_set.all():  # Bb - объявление, у которого FK на пользователя.
            bb.delete()  # при вызове delete() возникает сигнал post_delete, обрабатываемый приложением django_cleanup,
            # которое удалит все объекты, хранящиеся в только что удаленной записи
        super().delete(*args, **kwargs)

    class Meta(AbstractUser.Meta):
        pass
# ----------------------------------------------АВТОРИЗАЦИЯ-------------------------------------------------------#


# ----------------------------------------------РУБРИКИ-----------------------------------------------------------#
class Rubric(models.Model):
    """ С этой моделью пользователи не будут работать непосредственно. Поэтому параметры модели не задаются. """
    name = models.CharField(max_length=20, db_index=True, unique=True, verbose_name='Название')
    order = models.SmallIntegerField(default=0, db_index=True,
                                     verbose_name='Порядок')  # Порядок следования рубрик дргу за другом
    super_rubric = models.ForeignKey('SuperRubric', on_delete=models.PROTECT, null=True,
                                     blank=True, verbose_name='Надрубрика')


class SuperRubricManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=True)


class SuperRubric(Rubric):
    objects = SuperRubricManager()

    def __str__(self):
        return self.name

    class Meta:
        proxy = True
        ordering = ('order', 'name')
        verbose_name = 'Надрубрика'
        verbose_name_plural = 'Надрубрики'


class SubRubricManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=False)


class SubRubric(Rubric):
    objects = SubRubricManager()

    def __str__(self):
        return f'{self.super_rubric.name} - {self.name}'

    class Meta:
        proxy = True
        ordering = ('super_rubric__order', 'super_rubric__name', 'order', 'name')
        verbose_name = 'Подрубрика'
        verbose_name_plural = 'Подрубрики'
# ----------------------------------------------РУБРИКИ-----------------------------------------------------------#


# ----------------------------------------------ОБЪЯВЛЕНИЯ--------------------------------------------------------#
class Bb(models.Model):  # Объявление
    rubric = models.ForeignKey(SubRubric, on_delete=models.PROTECT, verbose_name='Рубрика')
    title = models.CharField(max_length=40, verbose_name='Товар')
    content = models.TextField(verbose_name='Описание')
    price = models.FloatField(default=0, verbose_name='Цена')
    contacts = models.TextField(verbose_name='Контакты')
    image = models.ImageField(blank=True, upload_to=get_timestamp_path, verbose_name='Изображение')
    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='Автор объявления')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Выводить в списке?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')

    def delete(self, *args, **kwargs):
        for ai in self.additionalimage_set.all():  # модель дополнительных иллюстраций
            ai.delete()  # при вызове delete() возникает сигнал post_delete, обрабатываемый приложением django_cleanup,
            # которое удалит все объекты, хранящиеся в только что удаленной записи
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-created_at']


class AdditionalImage(models.Model):
    bb = models.ForeignKey(Bb, on_delete=models.CASCADE, verbose_name='Объявление')
    image = models.ImageField(upload_to=get_timestamp_path, verbose_name='Изображение')

    class Meta:
        verbose_name = 'Дополнительная иллюстрация'
        verbose_name_plural = 'Дополнительные иллюстрации'
# ----------------------------------------------ОБЪЯВЛЕНИЯ--------------------------------------------------------#


# ----------------------------------------------КОММЕНТАРИИ-------------------------------------------------------#
class Comment(models.Model):
    bb = models.ForeignKey(Bb, on_delete=models.CASCADE, verbose_name='Объявление')
    author = models.CharField(max_length=30, verbose_name='Автор')
    content = models.TextField(verbose_name='Содержание')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Выводить на экран?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликован')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']


def post_save_dispatcher(sender, **kwargs):
    author = kwargs['instance'].bb.author
    if kwargs['created'] and author.send_messages:
        send_new_comment_notification(kwargs['instance'])


post_save.connect(post_save_dispatcher, sender=Comment)
# ----------------------------------------------КОММЕНТАРИИ-------------------------------------------------------#

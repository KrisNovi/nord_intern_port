from django.db import models


class TypeCode(models.Model):
    CHOICES = (
        ('ABB', 'ABB'),
        ('DFS', 'Danfoss'),
        ('VCN', 'VACON'),
        ('ONI', 'ONI'),
        ('SNR', 'Schneider'),
    )
    name = models.CharField(
        max_length=150,
        verbose_name='Наименование или типовой код',
    )
    code = models.CharField(
        max_length=150,
        verbose_name='Код вендора'
    )
    vendor = models.CharField(
        max_length=30,
        choices=CHOICES,
    )
    price = models.FloatField(
        verbose_name='Стоимость без учёта НДС, рубли'
    )

    def __str__(self):
        return self.name


class Proposal(models.Model):
    typecode = models.ManyToManyField(
        TypeCode,
        verbose_name='Типовой код',
    )
    qty = models.IntegerField(
        verbose_name='Количество, шт.'
    )
    amount = models.FloatField(
        verbose_name='Сумма без учёта НДС, рубли'
    )
    prop_id = models.TextField(
        verbose_name='Номер коммерческого предложения'
    )

    def __str__(self):
        return self.prop_id

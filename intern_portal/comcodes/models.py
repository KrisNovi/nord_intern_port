from django.db import models
from django.db.models.signals import pre_save, post_save, m2m_changed
from django.dispatch import receiver
from django.utils import timezone


class TypeCode(models.Model):
    CHOICES = (
        ('ABB', 'ABB'),
        ('Danfoss', 'Danfoss'),
        ('VACON', 'VACON'),
        ('ONI', 'ONI'),
        ('Schneider', 'Schneider'),
    )
    name = models.TextField(
        max_length=150,
        verbose_name='Наименование или типовой код',
    )
    code = models.TextField(
        max_length=150,
        verbose_name='Код вендора'
    )
    vendor = models.CharField(
        max_length=30,
        choices=CHOICES,
    )
    price = models.FloatField(
        verbose_name='Стоимость, валюта'
    )

    def __repr__(self):
        return self.name
    
    def __str__(self):
        return f'{self.name} ({self.code})'


class Proposal(models.Model):
    typecodes = models.ManyToManyField(
        TypeCode,
        through='TypeCodeInProposal',
        verbose_name='Типовой код',
        related_name='typecodes'
    )

    amount = models.FloatField(
        verbose_name='Сумма КП, валюта',
        default=0
    )
    prop_id = models.TextField(
        verbose_name='Номер коммерческого предложения',
        unique=True
    )
    company = models.CharField(
        max_length=500,
        verbose_name='Название организации',
        default=None
    )
    person = models.TextField(
        verbose_name='Контактное лицо',
        default=None
    )
    supply_per = models.TextField(
        verbose_name='Срок поставки',
        default=None
    )
    payment = models.TextField(
        verbose_name='Условия оплаты',
        default=None
    )
    publication_date = models.DateTimeField(
        'Дата создания',
        auto_now=True,
    )   

    def __repr__(self):
        return self.prop_id
    
    def __str__(self):
        return self.prop_id

@receiver(post_save, sender=Proposal)
def generate_prop_id(sender, instance, created, **kwargs):
    if created and not instance.prop_id:
        if not instance.publication_date:
            instance.publication_date = timezone.now()
        date_part = instance.publication_date.astimezone(timezone.get_current_timezone()).strftime('%d%m%y')
        count = Proposal.objects.filter(publication_date__date=instance.publication_date.date(), prop_id__contains=f'{date_part}-').count() + 1
        while Proposal.objects.filter(prop_id=f'{date_part}-{count}').exists():
            count += 1
        instance.prop_id = f'{date_part}-{count}'
        instance.save()


class TypeCodeInProposal(models.Model):
    typecodes = models.ForeignKey(
        TypeCode,
        on_delete=models.CASCADE,
        verbose_name='Типовые коды',
        blank=False,
        null=False
    )
    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        verbose_name='Коммерческое предложение',
        null=True,
        related_name='typecode_in_proposals'
    )
    qty = models.IntegerField(
        verbose_name='Количество'
    )

    def __str__(self):
        return f'{self.typecodes} в "{self.proposal}"'
    
    class Meta:
        ordering = ('-id',)
        verbose_name = 'Типовой код в КП'
        verbose_name_plural = 'Типовые коды в КП'
        constraints = (
            models.UniqueConstraint(
                fields=('proposal', 'typecodes'),
                name='unique_proposal_typecode'
            ),
        )

@receiver(post_save, sender=TypeCodeInProposal)
def generate_amount(sender, instance, created, **kwargs):
    if created:
        proposal = instance.proposal
        amount = 0
        typecodes = proposal.typecodes.all()
        for code in typecodes:
            typecode_in_proposal = TypeCodeInProposal.objects.get(proposal=proposal, typecodes=code)
            amount += code.price * typecode_in_proposal.qty
        proposal.amount = amount
        proposal.save()
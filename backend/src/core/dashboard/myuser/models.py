from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    profile_user = models.OneToOneField(
        User, on_delete=models.PROTECT, verbose_name="The User Profile"
    )
    profile_id = models.BigAutoField("profile id", primary_key=True)
    profile_tin = models.PositiveIntegerField(
        "Taxpayer Identification Number", default=0, blank=True
        )
    imagen = models.ImageField(
        default='default.jpeg', upload_to='profile_pics'
        )
    birth_date = models.DateField(
        "Date of Birth", default='2000-01-01', blank=True
        )
    tax_country = models.CharField(
        "Tax country", max_length=80, default='', blank=True
        )
    tax_state = models.CharField(
        "Tax State (tax state for US persons only)",
        max_length=80, default='', blank=True
    )
    address = models.CharField(
        "Address (Street address, City, State/Region, Country, Postal Code)",
        max_length=255, default='', blank=True
    )
    balance_usd = models.FloatField(
        "Balance in USD/$", default=100000.00, blank=False
        )
    balance_btc = models.FloatField(
        "Balance in BitCoin", default=2.096, blank=False
        )

    def __str__(self):
        return f'{self.profile_user.username} Profile'

    class Meta:
        verbose_name = "Alfred Profile"
        verbose_name_plural = "Alfred Profiles"


    def update(self, instance, data, **kwargs):
        """
            Update and return an existing Profile instance,
            given the data.
        """
        instance.profile_tin = data.get(
            'profile_tin', instance.profile_tin
            )
        instance.birth_date = data.get(
            'birth_date', instance.birth_date
            )
        instance.tax_country = data.get(
            'tax_country', instance.tax_country
            )
        instance.tax_state = data.get(
            'tax_state', instance.tax_state
        )
        instance.address = data.get(
            'address', instance.address
        )
        instance.balance_usd = validated_data.get(
            'balance_usd', instance.balance_usd
        )
        instance.balance_btc = validated_data.get(
            'balance_btc', instance.balance_btc
        )
        instance.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    print(instance)
    if created:
        Profile.objects.create(profile_user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

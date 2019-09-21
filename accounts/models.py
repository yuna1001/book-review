import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomUserManager(UserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('Emailを入力してください')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    uuid = models.UUIDField(_('uuid'), primary_key=True,
                            default=uuid.uuid4, editable=False)
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_(
            'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    # emailをCusomUserの主キーとして使うのでUniqueにする必要がある
    email = models.EmailField(_('email address'), unique=True, blank=True)

    profile_pic = models.ImageField(
        _('プロフィール画像'), blank=True, null=True, default='noimage.jpg')

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'  # ログイン時にusernameではなくemailを使用する
    REQUIRED_FIELDS = ['email']  # createsuperuserコマンドでユーザーを作成する際に聞かれるフィールド

    class Meta:
        verbose_name = _('CusomUser')
        verbose_name_plural = _('CusomUsers')
        db_table = 'custom_user'

    def get_username(self):
        """
        usernameのgetter
        """
        return self.username

    def email_user(self, subject, message, from_email=None, **kwargs):
        """メール送信関数"""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_followers(self):
        '''
        Userインスタンスがフォローしているuserを返す関数
        '''
        relations = Relation.objects.filter(user=self)
        return [relation.follow for relation in relations]


class Relation(models.Model):
    """
    フォロー・フォロワーのモデル
    """

    uuid = models.UUIDField(verbose_name='uuid', primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='ユーザ', null=True,
                             on_delete=models.SET_NULL, related_name='follow_user')

    # ユーザがフォローしている人
    followed = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='フォロー', null=True,
                                 on_delete=models.SET_NULL, related_name='followed_user')

    class Meta:
        unique_together = ('user', 'followed')

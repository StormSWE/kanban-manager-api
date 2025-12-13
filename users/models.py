from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import EmailValidator
from django.db import models
from django.utils import timezone

from .utils import user_avatar_upload_path


class UserManager(BaseUserManager):
	"""Custom user manager that uses email as the username field."""

	use_in_migrations = True

	def _create_user(self, email, password, **extra_fields):
		if not email:
			raise ValueError("The email address must be set")
		if not password:
			raise ValueError("The password must be set")
		email = self.normalize_email(email)
		user = self.model(email=email, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, email, password=None, **extra_fields):
		extra_fields.setdefault("is_staff", False)
		extra_fields.setdefault("is_superuser", False)
		return self._create_user(email, password, **extra_fields)

	def create_superuser(self, email, password, **extra_fields):
		extra_fields.setdefault("is_staff", True)
		extra_fields.setdefault("is_superuser", True)

		if extra_fields.get("is_staff") is not True:
			raise ValueError("Superuser must have is_staff=True.")
		if extra_fields.get("is_superuser") is not True:
			raise ValueError("Superuser must have is_superuser=True.")

		return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
	"""Custom user model for the Kanban platform."""

	email = models.EmailField(
		unique=True,
		max_length=255,
		validators=[EmailValidator()],
	)
	name = models.CharField(max_length=150, blank=True)
	bio = models.TextField(blank=True)
	avatar = models.ImageField(upload_to=user_avatar_upload_path, blank=True, null=True)

	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)

	created_at = models.DateTimeField(default=timezone.now)
	updated_at = models.DateTimeField(auto_now=True)

	objects = UserManager()

	EMAIL_FIELD = "email"
	USERNAME_FIELD = "email"
	REQUIRED_FIELDS: list[str] = []

	class Meta:
		ordering = ("-created_at",)
		verbose_name = "User"
		verbose_name_plural = "Users"

	def __str__(self):
		return self.email

	def get_full_name(self):
		return self.name or self.email

	def get_short_name(self):
		return self.name.split(" ")[0] if self.name else self.email

	@property
	def avatar_url(self):
		if self.avatar and hasattr(self.avatar, "url"):
			return self.avatar.url
		return None

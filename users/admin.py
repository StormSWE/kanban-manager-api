from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


class UserCreationForm(forms.ModelForm):
	password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
	password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput)

	class Meta:
		model = User
		fields = ("email", "name")

	def clean_password2(self):
		password1 = self.cleaned_data.get("password1")
		password2 = self.cleaned_data.get("password2")
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords do not match")
		return password2

	def save(self, commit=True):
		user = super().save(commit=False)
		user.set_password(self.cleaned_data["password1"])
		if commit:
			user.save()
		return user


class UserChangeForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ("email", "name", "bio", "avatar", "is_active", "is_staff")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
	add_form = UserCreationForm
	form = UserChangeForm
	model = User
	ordering = ("email",)
	list_display = ("email", "name", "is_staff", "is_active", "created_at")
	list_filter = ("is_staff", "is_superuser", "is_active")
	search_fields = ("email", "name")

	fieldsets = (
		(_("Credentials"), {"fields": ("email", "password")}),
		(_("Personal info"), {"fields": ("name", "bio", "avatar")}),
		(_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
		(_("Important dates"), {"fields": ("last_login", "created_at", "updated_at")}),
	)
	readonly_fields = ("created_at", "updated_at", "last_login")

	add_fieldsets = (
		(
			None,
			{
				"classes": ("wide",),
				"fields": ("email", "name", "password1", "password2", "is_staff", "is_active"),
			},
		),
	)

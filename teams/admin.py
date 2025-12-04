from django.contrib import admin

from .models import Team, TeamInvite, TeamMember


class TeamMemberInline(admin.TabularInline):
	model = TeamMember
	extra = 0
	autocomplete_fields = ("user",)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
	list_display = ("name", "created_by", "created_at")
	search_fields = ("name", "created_by__email")
	inlines = (TeamMemberInline,)


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
	list_display = ("team", "user", "role", "joined_at")
	list_filter = ("role",)
	search_fields = ("team__name", "user__email")


@admin.register(TeamInvite)
class TeamInviteAdmin(admin.ModelAdmin):
	list_display = ("team", "email", "role", "status", "created_at")
	list_filter = ("status",)
	search_fields = ("team__name", "email")

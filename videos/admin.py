from django.contrib import admin
from videos.models import Videos


class VideoAdmin(admin.ModelAdmin):
    list_display = ('course', 'title', 'category', 'access', 'duration', 'date', 'author')
    search_fields = ('title', 'description')
    list_filter = ('category', 'access', 'date', 'author')


admin.site.register(Videos, VideoAdmin)

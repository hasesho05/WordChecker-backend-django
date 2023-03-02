from django.contrib import admin
from .models import *

admin.site.register(Account)
admin.site.register(History)
admin.site.register(Post)
admin.site.register(LikePost)
admin.site.register(CommentPost)
admin.site.register(LikeComment)
admin.site.register(Notification)

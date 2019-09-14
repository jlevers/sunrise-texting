from django.contrib import admin
from .models import Question, QuestionResponse, Survey

admin.site.register(Question, admin.ModelAdmin)
admin.site.register(QuestionResponse, admin.ModelAdmin)
admin.site.register(Survey, admin.ModelAdmin)

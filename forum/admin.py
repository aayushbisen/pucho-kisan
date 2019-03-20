from django.contrib import admin
from .models import Farmer, Question, Answer, Specialist, QuestionFile
# Register your models here.


admin.site.register(Farmer)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Specialist)
admin.site.register(QuestionFile)
# remove questions and Answer if not needed

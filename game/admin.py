from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Lifeline)
admin.site.register(Level)
admin.site.register(Category)
admin.site.register(Option)
admin.site.register(ChosenOption)
admin.site.register(Question)
admin.site.register(Session)
admin.site.register(QuestionOrder)
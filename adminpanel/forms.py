from django.forms import ModelForm, Form
from django.utils.functional import cached_property
from django.db.models import ManyToManyField
from game.models import Question, Option, Lifeline, Category
from copy import deepcopy


class ModifiedModelForm(ModelForm):
    _newly_created: bool

    def __init__(self, *args, **kwargs):
        self._newly_created = kwargs.get('instance') is None
        super().__init__(*args, **kwargs)

    @cached_property
    def changed_data(self):
        apparent_changed_data = [name for name, bf in self._bound_items() if bf._has_changed()]
        if self._newly_created or not self.has_changed:
            return apparent_changed_data
        objectInstance = self.instance
        model = self._meta.model
        actual_changed_fields = list()
        differenceBetweenFields = [(getattr(objectInstance, x), self.cleaned_data[x]) for x in apparent_changed_data]
        for idx in range(len(apparent_changed_data)):
            field = apparent_changed_data[idx]
            initialData, newData = differenceBetweenFields[idx]
            if isinstance(model._meta.get_field(field), ManyToManyField):
                initialData = initialData.all()
                if set(initialData) == set(newData):
                    continue
            elif not isinstance(model._meta.get_field(field), ManyToManyField) and newData == initialData:
                continue
            actual_changed_fields.append(field)
        return actual_changed_fields
    
    def save(self, commit=True, *args, **kwargs):
        if not commit: 
            raise NotImplementedError("Many-to-many relationships and/or unchanged data need to be taken care of.")
        model = self._meta.model
        if self._newly_created:
            m2mFields = list(filter(lambda x: isinstance(model._meta.get_field(x), ManyToManyField), self.cleaned_data.keys()))
            m2mData = dict(list(map(lambda x: (x, self.cleaned_data[x]), m2mFields)))
            new_cleaned_data = deepcopy(self.cleaned_data)
            for field in m2mFields:
                del(new_cleaned_data[field])
            objectInstance = model.objects.create(**new_cleaned_data)
            for field, data in m2mData.items():
                getattr(objectInstance, field).set(data)
            return objectInstance
        else:
            objectInstance = self.instance
            if self.has_changed:
                changed_fields = self.changed_data
                differenceBetweenFields = [self.cleaned_data[x] for x in changed_fields]
                for idx in range(len(changed_fields)):
                    field = changed_fields[idx]
                    newData = differenceBetweenFields[idx]
                    if isinstance(model._meta.get_field(field), ManyToManyField):
                        getattr(objectInstance, field).set(newData)
                    else:
                        setattr(objectInstance, field, newData)
            return objectInstance


class QuestionForm(ModifiedModelForm):
    template_name = "adminpanel/formTemplates/question.html"        

    class Meta:
        model = Question
        fields = [
            "who_added",
            "falls_under",
            "question_type",
            "difficulty",
            "text",
            "correct_option",
            "incorrect_options",
            "date_added",
        ]
        exclude = ["asked_to"]

class OptionForm(ModifiedModelForm):
    template_name = "adminpanel/formTemplates/option.html"

    class Meta:
        model = Option
        fields = [
            "text",
            "date_added",
        ]
        exclude = ["hits"]

class LifelineForm(ModifiedModelForm):
    template_name = "adminpanel/formTemplates/lifeline.html"

    class Meta:
        model = Lifeline
        fields = [
            "name",
            "date_created",
            "description",
        ]

class CategoryForm(ModifiedModelForm):
    template_name = "adminpanel/formTemplates/category.html"

    class Meta:
        model = Category
        fields = [
            "date_created",
            "name",
        ]
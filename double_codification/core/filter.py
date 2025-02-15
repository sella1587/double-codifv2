import django_filters
from django.db import models
from django import forms
from .models import ConsolidatedObjects

class ConsolidateFilter(django_filters.FilterSet):  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.Meta.model._meta.fields:
            if isinstance(field, models.CharField): 
                field_name = field.name                
                self.filters[f"{field_name}_contains"] = django_filters.CharFilter(
                    field_name=field_name,
                    lookup_expr="icontains",
                    label=f"{field.verbose_name} Contient..."
                    
                )
                self.filters[f"{field_name}_not_contains"] = django_filters.CharFilter(
                    field_name=field_name,
                    lookup_expr="icontains",
                    exclude=True,
                    label=f"{field.verbose_name} Ne contient pas..."
                )
                self.filters[f"{field_name}_starts_with"] = django_filters.CharFilter(
                    field_name=field_name,
                    lookup_expr="istartswith",
                    label=f"{field.verbose_name} Commence par..."
                )
                self.filters[f"{field_name}_ends_with"] = django_filters.CharFilter(
                    field_name=field_name,
                    lookup_expr="iendswith",
                    label=f"{field.verbose_name} Se termine par..."
                )
                distinct_values = self.Meta.model.objects.values_list(field_name, flat=True).distinct().order_by(f'-{field_name}')
                self.filters[f"{field_name}_multiple_choice"] = django_filters.MultipleChoiceFilter(
                    field_name=field_name,
                    choices=[(value, value) for value in distinct_values],
                    label=f"{field.verbose_name} (Select)",
                    widget=forms.CheckboxSelectMultiple
                )
    class Meta:
        model = ConsolidatedObjects # replace with ConsolidatedObjects            
        fields = []
       
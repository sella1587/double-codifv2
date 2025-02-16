from rest_framework import serializers
from .models import ConsolidatedObjects, ObjectsFromCao
from .models import OwnerCodeDetails, OwnerCodeProperties

class DynamicConsolidatedObjectsSerializer(serializers.ModelSerializer):
    generate_data_config = serializers.SerializerMethodField()
    render_code_client_ouvrage = serializers.SerializerMethodField()

    # Définition explicite des champs relationnels
    facteur_choc = serializers.StringRelatedField()
    degre_choc = serializers.StringRelatedField()
    avec_plots = serializers.StringRelatedField()
    avec_carlingage = serializers.StringRelatedField()

    def __init__(self, *args, **kwargs):
        fields_to_include = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

        if fields_to_include:
            allowed = set(fields_to_include)
            existing = set(self.fields)
            for field in existing - allowed:
                self.fields.pop(field)

    class Meta:
        model = ConsolidatedObjects
        fields = '__all__'

    def get_generate_data_config(self, obj):
        return obj.generate_data_config()
    
    def get_render_code_client_ouvrage(self, obj):
        return obj.render_code_client_object()



class SerialObjectFromCao(serializers.ModelSerializer):
    class Meta:
        model = ObjectsFromCao
        fields = '__all__'




class OwnerCodeDetailsSerializer(serializers.ModelSerializer):
    objconso = serializers.PrimaryKeyRelatedField(queryset=ConsolidatedObjects.objects.all())
    ownercode = serializers.PrimaryKeyRelatedField(queryset=OwnerCodeProperties.objects.all())

    class Meta:
        model = OwnerCodeDetails
        fields = ['objconso', 'ownercode', 'fieldvalue']

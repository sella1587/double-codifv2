from django.db import models
import json
from django_tenants.models import TenantMixin
from django.db.models import Case, When, Value, CharField
from django.contrib.auth.models import Group
from django.utils.timezone import now
from .otheruse import getcodeclientbydata

import unidecode

DROIT_COLOR = ( 
    ("#42f56c", "Vert"), 
    ("#FFA500", "Orange"), 
    ("#FFFF00", "Jaune"), 
   
) 
class Ouvrage(TenantMixin):
    """Model Ouvrage
    Args:
        TenantMixin (_type_): Tenant
    Role: qui assure la propagation des models dedier pour tout les ouvrages
    """
    ouvrage = models.CharField(max_length=25, unique=True)
    type = models.CharField(max_length=50)
    schema_name = models.CharField(max_length=25, unique=True)
    description = models.TextField(null=True, blank=True)
    code_client = models.CharField(max_length=150)
    image = models.FileField(upload_to='media/core/img')
    created_on = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    auto_create_schema = True

    def save(self, *args, **kwargs):
        """forcer le schema name en miniscule et pas despace et sans accent
        """
        if self.schema_name:
            self.schema_name = "".join(self.schema_name.split())
            self.schema_name = unidecode.unidecode(self.schema_name.lower())
        super(Ouvrage, self).save(*args, **kwargs)

    class Meta:
        db_table = "ouvrages"
       

class FacteurChoc(models.Model):
    """Facteur choc
    Args:
        models (Model): rows ou rows(value de facteur choc)
    Returns:
        QuerySet: List des valeur des facteurs choc
    """
    value = models.CharField(max_length=5, unique=True)  
    class Meta:
        db_table = "facteur_choc"
        # managed = False
    def __str__(self):
        return self.value

class DegreChoc(models.Model):
    """Degre choc

    Args:
        models (_type_): _description_

    Returns:
        _type_: _description_
    """
    value  = models.CharField(max_length=50, unique=True)    
    class Meta:
        db_table = "degre_choc"
        # managed = False
    def __str__(self):
        return self.value

class AvecPlot(models.Model):
    """Avec Plot

    Args:
        models (rows): valeur ou options possible pour le champ avec_plot

    Returns:
        queryset: list des valeur possible pour Avec_plot
    """
    value = models.CharField(max_length=150, unique=True)   
    class Meta:
        db_table = "avec_plots"
        # managed = False
    def __str__(self):
        return self.value
    
class AvecCarlingage(models.Model):
    """Avec Carlingage

    Args:
        models (rows): list des valeur possible pour la colonne avec_carlingage

    Returns:
        queryste: list des valeur avec_carlingage
    """
    value = models.CharField(max_length=75)    
    class Meta:
        db_table = "avec_carlingage"
        # managed = False
    def __str__(self):
        return self.value

class ObjectsFromCao(models.Model):
    """Objects from cao

    Args:
        models (row): element recuper depuis le CAO
    """
    uid = models.CharField(max_length=75, null=False, unique=True)
    source = models.CharField(max_length=150, null=False)
    name = models.CharField(max_length=255, null=False)
    component_type = models.CharField(max_length=75, null=True, blank=True)
    description = models.CharField(max_length=254, null=True, blank=True)
    trade = models.CharField(max_length=100, null=True, blank=True)
    function = models.CharField(max_length=50, null=True, blank=True)
    lot = models.CharField(max_length=50, null=True, blank=True)
    room = models.CharField(max_length=50, null=True, blank=True)
    code_client_object = models.CharField(max_length=75, null=True, blank=True)    
    code_fournisseur = models.CharField(max_length=50, null=True, blank=True)
    facteur_choc = models.ForeignKey(FacteurChoc, on_delete=models.DO_NOTHING, db_constraint=False, null=True)
    degre_choc = models.ForeignKey(DegreChoc, on_delete=models.DO_NOTHING, db_constraint=False, null=True)
    avec_plots = models.ForeignKey(AvecPlot, on_delete=models.DO_NOTHING, db_constraint=False, null=True)
    avec_carlingage = models.ForeignKey(AvecCarlingage, on_delete=models.DO_NOTHING, db_constraint=False, null=True)
    date_traitement_cao = models.DateTimeField(blank=True, null=True)
    creation_date = models.DateTimeField(default=now, editable=False)
    date_last_modified = models.DateTimeField(blank=True, null=True)
    date_last_modified_dc = models.DateTimeField(blank=True, null=True)
    status= models.CharField(max_length=1, null=True) 
    class Meta:
        db_table = "objects_from_cao"

class ConsolidatedObjects(models.Model):
    """Data Consolider

    Args:
        models (_type_): represente les lignes consolider de la table object from cao

    Returns:
        _querySet: list des données consolidé
    """    
    source = models.CharField(max_length=150, null=False)
    name = models.CharField(max_length=255, null=False)
    component_type = models.CharField(max_length=75,null=True, blank=True)
    description = models.CharField(max_length=254, null=True, blank=True)
    trade = models.CharField(max_length=100,null=True, blank=True)
    function = models.CharField(max_length=50,null=True, blank=True)
    lot = models.CharField(max_length=50, null=True, blank=True)
    room = models.CharField(max_length=50, null=True, blank=True)
    code_client_object = models.CharField(max_length=75, null=True, blank=True)   
    code_fournisseur = models.CharField(max_length=50, null=True, blank=True)
    facteur_choc = models.ForeignKey(FacteurChoc, on_delete=models.DO_NOTHING, db_constraint=False, null=True)
    degre_choc = models.ForeignKey(DegreChoc, on_delete=models.DO_NOTHING, db_constraint=False, null=True)
    avec_plots = models.ForeignKey(AvecPlot, on_delete=models.DO_NOTHING, db_constraint=False, null=True)
    avec_carlingage = models.ForeignKey(AvecCarlingage, on_delete=models.DO_NOTHING, db_constraint=False, null=True)
    date_traitement_cao = models.DateTimeField(blank=True, null=True)
    creation_date = models.DateTimeField(default=now, editable=False)
    date_last_modified = models.DateTimeField(blank=True, null=True)
    date_last_modified_dc = models.DateTimeField(blank=True, null=True)
    status= models.CharField(max_length=1, null=True)

    #pour les input dans le cellule code_client
    def render_code_client_object(self):
        return self.code_client_object.lower()
    
    def generate_data_config(self):       
        # parametrages = ParametrageChamp.objects.filter(colonne="Code Client").order_by("position")
        qs = OwnerCodeProperties.objects.annotate(
            typeinput=Case(
                When(fieldtype__in = [1], then=Value('Fixe')),
                When(fieldtype__in = [3], then = Value('Regex')),
                When(fieldtype=2, then=Value('select')),
                default=Value('input'),
                output_field=CharField()
            )
        ).values("id", "fieldorder","typeinput", "fieldvalue", "fieldlabel")
        data_config = []
        for element in qs:
            if element['typeinput'] == 'select':
                filtra = element['fieldvalue']
                val = OwnerCodeLov.objects.filter(name__iexact=filtra).values_list('value','description')
                element['options'] = list(val)              
            else:
                element['options'] = ''
            #get value if exists
            # 
            res = ""  
            values_input = OwnerCodeDetails.objects.filter(objconso_id = self.id , ownercode_id = element["id"]).values('fieldvalue').first()         
            if values_input:
                res =values_input.get('fieldvalue')
            element['valueExist'] = res
            data_config.append(element)
 
     
        DataSorted = sorted(data_config, key=lambda d: d['fieldorder'])
        # code_client  = getcodeclientbydata(DataSorted) #"".join([k['valueExist'] if k['typeinput'] != 'Fixe' else k['fieldvalue'] for k in DataSorted])
        # self.code_client_object = code_client        
        # sorti = {"DadaSorted": DataSorted, "codeClient": code_client}         
        return json.dumps(DataSorted)
    
    class Meta:
        db_table = "consolidated_objects"

class OwnerCodeProperties(models.Model):
    """owner code properties
    Args:
        models (_type_): paramètrage de l'emplacement et propriete de chaque champ qui doit former le code client
    """
    fieldorder = models.IntegerField(null=False, unique=True)
    fieldtype = models.IntegerField(null=False)
    fieldvalue = models.CharField(max_length=50)
    fieldlabel = models.CharField(max_length=50)
    class Meta:
        db_table = "owner_code_properties"

class OwnerCodeDetails(models.Model):
    """Owner Code Details

    Args:
        models (_type_): qui stocke le code client éclate
    """
    objconso  = models.ForeignKey(ConsolidatedObjects, on_delete=models.DO_NOTHING, null=True)
    ownercode = models.ForeignKey(OwnerCodeProperties, on_delete=models.DO_NOTHING, null=True)    
    fieldvalue = models.CharField(max_length=150)
    fieldorder = models.IntegerField(null=False, blank=False)    
    class Meta:
        db_table = "owner_code_details"

class PropertyConsolidationParam (models.Model):
    """Regle de consolidation des données
    Args:
        models (_type_): param
    """
    property_name = models.CharField(max_length=50, null=False, unique=True)
    source_priority = models.CharField(max_length=150, null=True)
    display_mode = models.CharField(max_length=50, null=True)
    position_index = models.SmallIntegerField(null=True, blank=True)   
    class Meta:
        db_table = "property_consolidation_param"
        # managed = False

class OwnerCodeLov(models.Model):
    name = models.CharField(max_length=50, null=False)
    value = models.CharField(max_length=50)  
    description = models.TextField(null=True, blank=True)
    class Meta:
        db_table = "owner_code_lov"
    def __str__(self):
        return self.value
    
class OuvrageAd(models.Model):
    name_ad = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    class Meta:
        db_table = "ouvrage_ad" 
    def __str__(self):
        return f"{self.name_ad} - {self.description}"

        
class OuvrageGroupe(models.Model):
    ouvrage = models.ForeignKey(Ouvrage, on_delete=models.CASCADE)
    groupe = models.ForeignKey(Group,  on_delete=models.CASCADE)
    droit = models.ForeignKey(OuvrageAd, on_delete=models.CASCADE)
    color = models.CharField(
        max_length=20,
        choices=DROIT_COLOR,
        default="#C70039"
    )
    class Meta:
        unique_together = ("ouvrage", "groupe")
        db_table = "ouvrage_groupe"
    def __str__(self):
        return f"{self.groupe} - {self.droit}"


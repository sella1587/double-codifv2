from rest_framework.views import APIView
from rest_framework.response import Response
from .outils import merge_objects_from_json
from .otheruse import getcodeclientbydata
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser
from .models import ConsolidatedObjects, ObjectsFromCao
from .models import PropertyConsolidationParam, OwnerCodeDetails, OwnerCodeLov, OwnerCodeProperties
from .models import Ouvrage, FacteurChoc, DegreChoc, AvecPlot, AvecCarlingage, OuvrageGroupe
from .serializers import DynamicConsolidatedObjectsSerializer
from .serializers import SerialObjectFromCao as ObjectsFromCaoSerializer
from .serializers import OwnerCodeDetailsSerializer
from .filter import ConsolidateFilter
from rest_framework import status
import json
import logging

from django.db.models import Case, When, Value, CharField, Aggregate
from django.db import models
from django.utils.timezone import now
from django.contrib.postgres.aggregates import StringAgg
from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm
import pandas as pd
from django_tenants.utils import schema_context
from django.db.models.expressions import Window
from django.db.models.functions import DenseRank
from django.db.models import F, Q, Count
from django.core import serializers
from datetime import datetime
from django .shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view
from django.utils.dateparse import parse_datetime
logger = logging.getLogger('core')

class CustomLoginView(LoginView):
    authentication_form = CustomLoginForm

@login_required
def home2(request):
    ouv= request.session['SelectedOuvrage'].lower()
    with schema_context(ouv):   
        optionFacteurChoc = [element for element in FacteurChoc.objects.values('id', 'value').distinct().order_by('-id')]
        optionDegreChoc = [element for element in DegreChoc.objects.values('id', 'value').distinct().order_by('-id') ]
        optionavec_plots = [element for element in AvecPlot.objects.values('id', 'value').distinct().order_by('-id') ]
        optionaavec_carlingage = [element for element in AvecCarlingage.objects.values('id', 'value').distinct().order_by('-id') ]
        context = {
                "facteur_choc" : optionFacteurChoc,
                "degre_choc" : optionDegreChoc,
                "avec_plots" : optionavec_plots,
                "avec_carlingage" : optionaavec_carlingage
        }
        return render(request, 'pages/consolidation.html', context)

@login_required
def index(request):
    optionFacteurChoc = [element for element in FacteurChoc.objects.values('id', 'value').distinct().order_by('-id')]
    optionDegreChoc = [element for element in DegreChoc.objects.values('id', 'value').distinct().order_by('-id') ]
    optionavec_plots = [element for element in AvecPlot.objects.values('id', 'value').distinct().order_by('-id') ]
    optionaavec_carlingage = [element for element in AvecCarlingage.objects.values('id', 'value').distinct().order_by('-id') ]
    ouv= request.session['SelectedOuvrage'].lower()   
    with schema_context(ouv):  
        queryset = ConsolidateFilter(request.GET, queryset=ConsolidatedObjects.objects.all())
    
        dataOption = {
            "facteur_choc" : optionFacteurChoc,
            "degre_choc" : optionDegreChoc,
            "avec_plots" : optionavec_plots,
            "avec_carlingage" : optionaavec_carlingage
        }
        context = {        
            "filtreform": queryset,
            # 'oVselected': selected,
            "tables_consolide": queryset.qs,
            "checkSelection":dataOption
        }
        return render(request, 'pages/home.html', context)

@login_required
def menu(request):
    user = request.user    
    groupes = user.groups.all()  
    list_ouvrage = OuvrageGroupe.objects.filter(ouvrage__is_active=True, groupe__in=groupes).select_related('ouvrage').values("id", "ouvrage__description", "groupe__name", "color", "ouvrage", "ouvrage__type", "ouvrage__image")
    ouvrageSelected = request.GET.get('ouvrage')
    droit = request.GET.get('droit')  
    request.session['SelectedOuvrage'] = ouvrageSelected 
    request.session['droit'] = droit
    context = {
        "datas": "consolidated_data",
        "formulaire": "si besoin",
        "listofOuvrage": list_ouvrage,
    }
    return render(request, 'pages/menu.html', context)

class ImportJsonView(APIView):
    """Load Json data To objects_from_cao

    Args:
        APIView (_type_): Recupere un fichier json et l'injecté dans la base

    Returns:
        _type_: json qui contient l'etat des processus
    """
    authentication_classes = []
    parser_classes = [MultiPartParser] 
    def post(self, request):
        if 'file' not in request.FILES:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)        
        file = request.FILES['file']
        try:
            import json
            data = json.load(file)            
            Project = data['Project'].lower()
            Source = data['Source']
            dt_processing = datetime.strptime(data['DateTraitement'], "%Y%m%d%H%M%S")
            # load datas sjon           
            with schema_context(Project):
                df_raw = pd.DataFrame(data["Datas"])
                df_raw["source"] =  Source 
                df_raw["project"] = Project
                df_raw["dt_processing"] = dt_processing
                df_raw.rename(columns={
                    "Oid": "uid",
                    "Name": "name",
                    "ComponentType": "component_type",
                    "Description": "description",
                    "Trade": "trade",
                    "Function": "function",
                    "Lot": "lot",
                    "Room": "room",
                    "CodeFournisseur": "code_fournisseur",
                    "FacteurChoc": "facteur_choc",
                    "DegreChoc":"degre_choc",
                    "AvecPlots":"avec_plots",
                    "AvecCarlingage": "avec_carlingage"
                }, inplace=True)
                # check df_raw if ok and load then load it into database
                # merge_objects_from_json
                df_raw = df_raw.where(pd.notnull(df_raw), None) 
                list_of_dicts = df_raw.to_dict(orient='records') 
                retour = merge_objects_from_json(list_of_dicts)
                return Response({"message": "Data imported and flagged successfully", "data": retour}, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(e)
            return Response({"error": "Invalid JSON file", "error_details":str(e)}, status=status.HTTP_400_BAD_REQUEST) 


class GetObjectConsolidated(APIView):    
    def get(self, request):
        ouvrage = request.GET.get('ouvrage')       
        if ouvrage:
            ouvrage = ouvrage.lower()
            with schema_context(ouvrage):
                try: 
                    ObjectGrouper = ObjectsFromCao.objects.annotate(
                        rank=Window(
                            expression=DenseRank(),
                            order_by=F('name').asc()
                        )
                    ).exclude(status='D').order_by('rank').values()
                    ConsolidationRules = PropertyConsolidationParam.objects.values("property_name", "source_priority", "display_mode")                  
                    json_data = list(ObjectGrouper)
                    rules = list(ConsolidationRules)
                    # lisofcol = [k['property_name'] for k in rules]                   
                    df_data = pd.DataFrame(json_data)                   
                    unique_values = df_data['rank'].unique()                                      
                    consolidate_row = []
                    for g in unique_values:
                        row_consolide = {}
                        df_ = df_data[df_data['rank'] == g]
                        # if len(df_) == 1:  
                        #     consolidate_row.append(df_.iloc[0][lisofcol].to_dict())                                 
                        if True:
                            for rule in rules:
                                col_name = rule['property_name']
                                flag = rule['display_mode'].lower()
                                priorites  = rule['source_priority']
                                if len(priorites) == 0:
                                    priorites = []
                                else:
                                    priorites = priorites.split(";")
                                resultat = []     
                                if len(priorites) > 0:
                                    for priorite in priorites:                   
                                        filtre = df_['source'] == priorite
                                        if filtre.any():
                                            if flag == 'first':                           
                                                ligne_min_id = df_.loc[filtre].nsmallest(1, 'id')
                                                resultat = ligne_min_id[col_name].iloc[0]
                                                if resultat is not None:
                                                    resultat = [str(resultat)]  
                                            elif flag == 'all':                            
                                                resultat.extend(df_.loc[filtre, col_name].tolist())
                                else: 
                                
                                    if flag == 'first':                    
                                        ligne_min_id = df_.nsmallest(1, 'id')
                                        resultat = [ligne_min_id[col_name].iloc[0]]
                                    elif flag == 'all':                                                                            
                                        resultat = df_[col_name].tolist()                               
                                if resultat is not None:                
                                    resultat = list(set(resultat)) 
                                    resultat.sort() 
                                    resultat_concatene = ";".join(resultat) 
                                    if resultat_concatene.startswith(";"):
                                        resultat_concatene = resultat_concatene.replace(";","")                                   
                                    row_consolide[col_name] = resultat_concatene
                                else:                                    
                                    row_consolide[col_name] = ""
                            consolidate_row.append(row_consolide)
                    #load consolidation
                    ConsolidatedObjects.objects.bulk_create([ConsolidatedObjects(**t) for t in consolidate_row])
                    #                   
                    return Response({'datas': consolidate_row, 'ouvrage': ouvrage}, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response ({'error':str(e)}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({"error": "aucune ouvrage a été séléctionner"}, status=status.HTTP_400_BAD_REQUEST)

class CheckOwnerCodeUnicity(APIView):
    def get(self, request):
        if not request.GET.get('ouvrage') and not request.GET.get('code_client'):
            return Response({"error": "il faut spécifier un ouvrage et le code_client à vérifier"}, status=status.HTTP_400_BAD_REQUEST)
        ouvrage = request.GET.get('ouvrage').lower()
        code_client = request.GET.get('code_client')
        with schema_context(ouvrage):
            retour = ConsolidatedObjects.objects.filter(code_client_object__iexact=code_client).count()           
            if retour == 0:
                return Response({'status': True}, status=status.HTTP_200_OK) # unique
            return  Response({'status': False}, status=status.HTTP_200_OK) # not unique
        
class CheckNameUnicity(APIView):
    def get(self, request):
        if not request.GET.get('ouvrage') and not request.GET.get('name'):
            return Response({"error": "il faut spécifier un ouvrage et un repère fonctionnel"}, status=status.HTTP_400_BAD_REQUEST)
        ouvrage = request.GET.get('ouvrage').lower()
        name = request.GET.get('name')
        with schema_context(ouvrage):
            retour = ConsolidatedObjects.objects.filter(name__iexact=name).count()           
            if retour == 0:
                return Response({'status': True}, status=status.HTTP_200_OK) # unique
            return  Response({'status': False}, status=status.HTTP_200_OK) # not unique

class GetCatalogData(APIView):
    def get(self, request):
        ouvrage = request.GET.get('ouvrage')
        cat = request.GET.get('categorie')       
        if ouvrage and cat:          
            with schema_context(ouvrage.lower()):
                data = ""
                if cat.lower() == 'facteurchoc':                   
                    data = FacteurChoc.objects.values()                   
                if cat.lower() == "degrechoc":
                    data = DegreChoc.object.values()
                if cat.lower() == 'avecplots':
                    data = AvecPlot.objects.values()
                if cat.lower() == 'avecarlingage':
                    data = AvecCarlingage.objects.values()                
                return Response({"data":  [entry for entry in data]}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "ouvrage ou cat non trouve"}, status=status.HTTP_404_NOT_FOUND)
        
class GetDatasForCao(APIView):
    def get(self, request, ouvrage, date):
        with schema_context(ouvrage.lower()):
            data = get_object_or_404(ObjectsFromCao, date_last_modified_dc__gt = date)
            return Response({"datas": data}, status=status.HTTP_200_OK)
        
class CustomPagination(PageNumberPagination):   
    page_size_query_param = 'length'   
    page_query_param = 'start' 
    page_size = 10
    
    def get_page_number(self, request, paginator):
        """
        Cette méthode est nécessaire pour convertir le paramètre 'start' (utilisé par DataTables)
        en numéro de page correct pour la pagination.
        """
        page_size = self.get_page_size(request)
        start = int(request.GET.get(self.page_query_param, 0))  # Valeur de 'start' par défaut à 0
        page_number = start // page_size + 1  # Calcul du numéro de page
        return page_number

class ConsolidatedObjectsView(APIView):
    def get(self, request):
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        column_index = int(request.GET.get('order[0][column]', 0))
        column_name = request.GET.get(f'columns[{column_index}][data]', 'id')
        order_dir = request.GET.get('order[0][dir]', 'asc')
        ouvrage = request.GET.get('ouvrage')
        if not ouvrage:
            return Response({"error": "Ouvrage is required"}, status=400)
        filters = Q()
        filter_fields = [
            "name", "source", "description", "component_type",
            "trade", "function", "lot", "room",
            "code_client_object", "code_fournisseur","date_creation","last_date_modified"
        ]
        for field in filter_fields:
            search_value = request.GET.get(f"{field}-search", None)
            start_with_value = request.GET.get(f"{field}-start-with", None)
            end_with_value = request.GET.get(f"{field}-end-with", None)
            not_contain_value = request.GET.get(f"{field}-not-contain", None)
            not_start_with_value = request.GET.get(f"{field}-not-start-with", None)
            not_end_with_value = request.GET.get(f"{field}-not-end-with", None)
            checkbox_values = request.GET.getlist(f"{field}-checkbox[]") 
            if search_value:
                filters &= Q(**{f"{field}__icontains": search_value})

            if start_with_value:
                filters &= Q(**{f"{field}__istartswith": start_with_value})
            if end_with_value:
                filters &= Q(**{f"{field}__iendswith": end_with_value})
            if not_end_with_value:
                filters &= ~Q(**{f"{field}__iendswith": not_end_with_value})

            if not_contain_value:
                filters &= ~Q(**{f"{field}__icontains": not_contain_value}) 

            if not_start_with_value:
                filters &= ~Q(**{f"{field}__istartswith": not_start_with_value}) 

            if checkbox_values:
                filters &= Q(**{f"{field}__in": checkbox_values}) 

        with schema_context(ouvrage.lower()):
            queryset = ConsolidatedObjects.objects.filter(filters)            
            total_records = queryset.count()            
            queryset = queryset.order_by(column_name if order_dir == 'asc' else f'-{column_name}')         
            paginator = CustomPagination()
            paginator.page_size = length
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            serializer = DynamicConsolidatedObjectsSerializer(
                paginated_queryset or [],
                many=True,
                fields=[
                    "id", "name", "source", "description", "component_type",
                    "trade", "function", "lot", "room", "code_client_object",
                    "code_fournisseur", "facteur_choc", "degre_choc",
                    "avec_plots", "avec_carlingage", "creation_date",
                    "date_last_modified", "generate_data_config"
                ]
            )

            return Response({
                "draw": draw,
                "recordsTotal": total_records,
                "recordsFiltered": total_records,
                "data": serializer.data
            })



@api_view(['GET'])
def filtered_objects(request):
    """
    API pour filtrer les objets en fonction de l'ouvrage et d'une date donnée.
    Prend en charge la pagination via les paramètres `page` (offset) et `limit`.
    """
    ouvrage = request.GET.get('ouvrage', None)
    date_str = request.GET.get('date', None)
    source = request.GET.get('source', None)
    limit = request.GET.get('limit', 1000)
    if not ouvrage:
        return Response({"error": "ouvrage is required"}, status=400)
    if not source:
        return Response({"error": "souce is required"}, status=400)
    
    with schema_context(ouvrage.lower()):
        queryset = ObjectsFromCao.objects.all() 
        if date_str:
            try:
                date_filter = parse_datetime(date_str)
                if date_filter:
                    queryset = queryset.filter(date_last_modified_dc__gte=date_filter, source__iexact = source)
                else:
                    queryset = queryset.filter(source__iexact = source)
            except ValueError:
                return Response({"error": "Format de date invalide. Utilisez YYYY-MM-DDTHH:MM:SSZ"}, status=400)

        # Pagination personnalisée
        paginator = PageNumberPagination()
        paginator.page_size = int(limit)
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = ObjectsFromCaoSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
    
@api_view(['PUT'])
def update_objects(request):
    """
    API pour mettre à jour un ou plusieurs champs des objets ayant le même `name`.
    Requête JSON attendue : { "name": "nom_objet", "fields": { "champ1": "valeur1", "champ2": "valeur2" } }
    """
    data = request.data
    name = data.get("name")
    ouvrage = data.get("ouvrage")
    fields_to_update = data.get("fields", {})

    if not name or not fields_to_update or ouvrage:
        return Response({"error": "Le paramètre 'name', 'fields' et ouvrage sont requis"}, status=status.HTTP_400_BAD_REQUEST)
    
    with schema_context(ouvrage.lower()):  
        objects = ObjectsFromCao.objects.filter(name=name)
        if not objects.exists():
            return Response({"error": f"Aucun objet trouvé avec le name '{name}'"}, status=status.HTTP_404_NOT_FOUND)    
        updated_count = objects.update(**fields_to_update)
        return Response({
            "message": f"{updated_count} enregistrement(s) mis à jour.",
            "updated_fields": fields_to_update
        }, status=status.HTTP_200_OK)
                

class check_code_client_exists(APIView):
    def post(self, request):
        data = request.data       
        ouvrage = data.get("ouvrage")
        if not ouvrage:
            return Response(json.dumps({"error": "l'ouvrage est obligatoire"}), status = status.HTTP_400_OK)
        data_entries = data.get("data", [])
        cd_client = getcodeclientbydata(data_entries)
        ret = 0
        with schema_context(ouvrage):
            ret = ConsolidatedObjects.objects.filter(code_client_object__iexact = cd_client).count()
        if ret == 0:
            return Response(json.dumps({"code_client": cd_client, "nb": ret, "message": "code client unique"}), status = status.HTTP_200_OK)
        else:
            return Response(json.dumps({"code_client": cd_client, "nb": ret, "message": "code client exist déjà"}), status = status.HTTP_200_OK)


class AddNewLigneConsolidated(APIView):
    def get(self, request, *args, **kwargs):
        ouvrage = request.GET.get('ouvrage')          
        if not ouvrage:
            return Response({"error": "Ouvrage is required"}, status=400)
        with schema_context(ouvrage.lower()):
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
                    filtra = element['fieldvalue'].lower()
                    val = OwnerCodeLov.objects.filter(name=filtra).values_list('value','description')
                    element['options'] = list(val)              
                else:
                    element['options'] = ''            
                data_config.append(element)
            
            DataSorted = sorted(data_config, key=lambda d: d['fieldorder'])                  
            default_value = {
                "id":"",
                "name":"",
                "source":"USER",
                "description":"",
                "component_type":"",
                "trade":"",
                "function":"",
                "lot":"",
                "room":"",
                "code_client_object":"",
                "code_fournisseur":"",
                "facteur_choc":"",
                "degre_choc":"",
                "avec_plots":"",
                "avec_carlingage":"",
                "creation_date": str(now()),
                "date_last_modified":str(now()),
                "generate_data_config": DataSorted
            }
        return Response(json.dumps(default_value), status = status.HTTP_200_OK)
    
class LoadOwnerCodeDetails(APIView):
    def post(self, request):
        datas = request.data
        print(datas)
        updated_entries = [] 
        created_entries = []
        for data in datas:
            print("----", data)
            objconso_id = data.get("objconso")
            ouvrage = data.get("ouvrage")
            data_entries = data.get("data", [])
            with schema_context(ouvrage.lower()):            
                code_cli_new  = getcodeclientbydata(data_entries)                       
                try:
                    objconso = ConsolidatedObjects.objects.get(id=objconso_id)
                    objconso.code_client_object = code_cli_new
                    objconso.save()
                except ConsolidatedObjects.DoesNotExist:
                    return Response({"error": "objconso non trouvé"}, status=status.HTTP_404_NOT_FOUND) 
                for entry in data_entries:
                    ownercode_id = entry.get("id")
                    fieldvalue = entry.get("valueExist")
                    fieldorder = entry.get("fieldorder")
                    if entry.get('typeinput') == "Fixe":
                        fieldvalue = entry.get("fieldvalue")
                    else:
                        fieldvalue = entry.get("valueExist")             
                
                    try:
                        ownercode = OwnerCodeProperties.objects.get(id=ownercode_id)
                    except OwnerCodeProperties.DoesNotExist:
                        return Response({"error": f"ownercode {ownercode_id} non trouvé"}, status=status.HTTP_404_NOT_FOUND)
                
                    try:
                        print(objconso, ownercode)
                        owner_code_detail = OwnerCodeDetails.objects.get(objconso=objconso, ownercode=ownercode)
                                       
                        owner_code_detail.fieldvalue = fieldvalue
                        owner_code_detail.fieldorder = fieldorder
                        owner_code_detail.save()
                        updated_entries.append(OwnerCodeDetailsSerializer(owner_code_detail).data)
                    except Exception as e:#OwnerCodeDetails.DoesNotExist:                                          
                        owner_code_detail = OwnerCodeDetails.objects.create(
                            objconso=objconso,
                            ownercode=ownercode,
                            fieldvalue=fieldvalue,
                            fieldorder = fieldorder
                        )
                        created_entries.append(OwnerCodeDetailsSerializer(owner_code_detail).data)

        return Response({
            "message": "Données traitées avec succès",
            "created": created_entries,
            "updated": updated_entries
        }, status=status.HTTP_200_OK)




            
            

                

        
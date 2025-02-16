import pandas as pd
from .models import ObjectsFromCao, PropertyConsolidationParam, Ouvrage
from .models import FacteurChoc, DegreChoc, AvecCarlingage, AvecPlot
from datetime import date
from django.utils.timezone import now
# from django_tenants.utils import schema_context


def getListCategorie():
    listcat = Ouvrage.objects.values("ouvrage","id").distinct()
    return [(c['ouvrage'], c['id']) for c in listcat]

def bulk_insert_with_logging(model, data):
    valid_objects = []
    for item in data:
        try:
            obj = model(**item)
            valid_objects.append(obj)
        except Exception as e:
            print(f"Erreur lors de la création de l'objet : {item} - {str(e)}")    
    try:
        model.objects.bulk_create(valid_objects, ignore_conflicts=True) 
    except Exception as e:
        print(f"Erreur lors du bulk_create : {str(e)}")



def merge_objects_from_json(source_data, source):
    """
    Fonction qui effectue le traitement de fusion :
    - Met à jour les objets existants
    - Insère les nouveaux objets
    - Flague les objets absents
    """
    source_uids = {item['uid'] for item in source_data}
    TargetData = ObjectsFromCao.objects.select_related("facteur_choc", "degre_choc", "avec_plots", "avec_carlingage").filter(source__iexact=source).all()    
    targetList = {f.uid for f in TargetData}
    ToUpdateInTarget = source_uids.intersection(targetList)
    ToInsertInTarget = source_uids - targetList    
    ToFlaged = targetList - source_uids  
    error = []
    #insertion
    for item in source_data:
        if item['uid'] in ToInsertInTarget:
            try:
                new_objects = [
                    ObjectsFromCao(
                        uid=item['uid'],
                        source=item['source'],
                        name=item['name'],
                        component_type=item.get('component_type'),
                        description=item.get('description'),
                        trade=item.get('trade'),
                        function=item.get('function'),
                        lot=item.get('lot'),
                        room=item.get('room'),   
                        code_fournisseur=item.get('code_fournisseur'),
                        facteur_choc = FacteurChoc.objects.get(value=item.get('facteur_choc')),
                        degre_choc = DegreChoc.objects.get(value=item.get('degre_choc')),
                        avec_plots = AvecPlot.objects.get(value=item.get('avec_plots')),
                        avec_carlingage = AvecCarlingage.objects.get(value=item.get('avec_carlingage')),
                        date_traitement_cao = item.get('dt_processing'),
                        creation_date=now(),
                        date_last_modified =now(),                   
                        status='A'
                    )                    
                ]    
                ObjectsFromCao.objects.bulk_create(new_objects, ignore_conflicts=True)
            except Exception as e:
                #logger l'erreur et continue
                error.append({"error": e, "uid": item['uid']})
                print(e, 'pour uid', item['uid'])
   
    #update
    existing_objects = TargetData.filter(uid__in =ToUpdateInTarget).all()
    data_json_target = []
    for f in existing_objects:
        data_ = {}
        data_['uid'] = f.uid
        data_['source'] = f.source
        data_['name'] = f.name
        data_['component_type'] = f.component_type
        data_['description'] = f.description
        data_['trade'] = f.trade
        data_['function'] = f.function
        data_['lot'] = f.lot
        data_['room'] = f.room
        data_['code_fournisseur'] = f.code_fournisseur
        data_['facteur_choc'] = f.facteur_choc.value
        data_['degre_choc'] = f.degre_choc.value
        data_['avec_plots'] = f.avec_plots.value
        data_['avec_carlingage'] = f.avec_carlingage.value
        data_['code_client_object'] = f.code_client_object
        data_json_target.append(data_)

    for obj in data_json_target:       
        datas = next(item for item in source_data if item['uid'] == obj['uid'])             
        obj2update = {}
        key_fonc = ["name", "component_type","description", "trade", "function","lot", "room"]
        key_for_target_empty = ["code_fournisseur"] #"code_client_object",
        catalogue = ["facteur_choc","degre_choc","avec_plots","avec_carlingage"]
        uid = obj['uid']
        colcle = key_for_target_empty + catalogue 
        for k in key_fonc:            
            if datas[k] != obj[k] and str(datas[k]).lower() != 'none':
                obj2update[k] = datas[k]

        for y in colcle:           
            if (obj[y] == None or str(obj[y]).lower() == 'none' or str(obj[y]).strip()=='') and y !='code_client_object':
                if obj[y] != datas[y]:
                    obj2update[y] = datas[y]

        concat_target = "".join([str(datas[c]) for c in colcle])
        contact_source = "".join([str(obj[c]) for c in colcle])
        if contact_source != concat_target:
            obj2update['date_last_modified_dc'] = now()

        if len(obj2update) > 0:
            obj2update['status'] = 'M'
            obj2update['date_last_modified'] = now()         
            try:
                foreign_keys = {
                    'facteur_choc': FacteurChoc,
                    'degre_choc': DegreChoc,
                    'avec_plots': AvecPlot,
                    'avec_carlingage': AvecCarlingage
                }

                for key, model in foreign_keys.items():
                    if key in obj2update:                       
                        obj2update[key] = model.objects.get(value=obj2update[key]).id 
                ObjectsFromCao.objects.filter(uid=uid).update(**obj2update)
            except Exception as e:
                error.append({"erreur": "ERR-06", "uid": uid})
                #log ici
    for u in ToFlaged:
        try:
            ObjectsFromCao.objects.filter(
            uid=u
        ).update(date_last_modified=date.today(), status='D')
        except Exception as e:
            error.append({"erreur": "ERR-07", "uid": uid, "message": e})            
    return {"proc_status": error}


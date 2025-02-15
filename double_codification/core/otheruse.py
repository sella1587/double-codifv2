def getcodeclientbydata(data_entries):
    newCdl = []
    print(data_entries) 
    if isinstance(data_entries, list):
        if len(data_entries)  > 0:               
            DataSorted = sorted(data_entries, key=lambda d: d['fieldorder'])           
            for e in DataSorted:
                if e['typeinput'] == 'Fixe':
                    newCdl.append(e['fieldvalue'])
                else:
                    newCdl.append(e['valueExist']) 
    ret = str("".join(newCdl)).strip('- ').strip(' -')
    if len(ret) > 7:
        return ret
    else:
        return ""
    
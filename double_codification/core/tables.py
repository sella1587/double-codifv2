import django_tables2 as tables
from .models import ConsolidatedObjects

class TableConsolide(tables.Table):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        for col_name, column in self.base_columns.items():
            column.attrs = {
                "th": {"id": col_name}
            }
            if col_name =='code_client_object':
                self.row_attrs = {
                    "td": {
                    "class": "cell",
                    "data-config": column.generate_data_config
                    }
                }

    
    class Meta:
        model = ConsolidatedObjects
        per_page = 5
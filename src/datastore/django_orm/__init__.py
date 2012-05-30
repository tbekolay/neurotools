"""
Implementation of an SQL-based DataStore using the Django ORM.
"""

from NeuroTools.datastore.interface import AbstractDataStore
from NeuroTools.datastore.keygenerators import full_type
from django.conf import settings

DJANGO_CONFIGURED = False

class DjangoORMDataStore(AbstractDataStore):
    """Persistent data store using the Django ORM to store/retrieve keys/indices
       information with data stored using `pickle` on the filesystem."""
    
    def __init__(self, database_parameters, data_root_dir):
        global DJANGO_CONFIGURED
        if DJANGO_CONFIGURED:
           raise Exception("Django already configured. It is not possible to have more than one DjangoORMDataStore object at a time")
        self.root_dir = data_root_dir
        settings.configure(USE_I18N=False,
                           INSTALLED_APPS=('NeuroTools.datastore.django_orm',),
                           **database_parameters)
        DJANGO_CONFIGURED = True
        from django.core.management import call_command 
        call_command('syncdb') 
    
    def __del__(self):
        global DJANGO_CONFIGURED
        DJANGO_CONFIGURED = False
    
    def retrieve(self, component, attribute_name):
        __doc__ = AbstractDataStore.retrieve.__doc__
        import models
        # if the data exists,
        #  return it
        # else
        #  return None
        component_db_obj = self._get_component(component)  
        data_item = models.DataItem.objects.filter(component_state=component_db_obj,
                                                   attribute_name=attribute_name)
        assert len(data_item) == 1
        return data_item[0].get_data(self.root_dir)

    def store(self, component, attribute_name, data):
        __doc__ = AbstractDataStore.store.__doc__
        import models
        # possibly we could check if data already exists, and raise an Exception if
        # it is different to the new data (should probably be a flag to control this,
        # because it might be heavyweight
        component_db_obj = self._get_component(component)
        data_item, created = models.DataItem.objects.get_or_create(component_state=component_db_obj,
                                                                   attribute_name=attribute_name)
        data_item.store_data(self.root_dir, data)
    
    def _get_component(self, component):
        """
        Given a component, get the equivalent database object if it exists 
        """
        import models
        component_type, created = models.ComponentType.objects.get_or_create(name=full_type(component),
                                                                             version=str(component.version))
        args = dict(type=component_type,
                    parameters_uri=component.parameters._url)
        if component.input is None:
            try:
                component_db_obj = models.ComponentState.objects.get(input__isnull=True, **args)
            except models.ComponentState.DoesNotExist:
                component_db_obj = models.ComponentState(**args)
                component_db_obj.save()
        else:
            component_db_obj, created = models.ComponentState.objects.get_or_create(input=self._get_component(component.input), **args)
        return component_db_obj

    def list_contents(self):
        data_items = models.DataItem.objects.all()
        return list(data_items)
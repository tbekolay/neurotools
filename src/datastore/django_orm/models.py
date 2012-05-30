
from django.db import models
import os.path
import pickle
import hashlib



class ComponentType(models.Model):
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    
    def __unicode__(self):
        return "%s[%s]" % (self.name, self.version)


class ComponentState(models.Model):
    type = models.ForeignKey(ComponentType)
    parameters_uri = models.CharField(max_length=200)
    input = models.ForeignKey('ComponentState', null=True)

    def global_id(self):
        """
        Use pickle to convert the object state dictionary to a string, then
        hash this string to give a unique identifier of fixed length.
        """
        state = {'type': str(self.type),
                 'parameters_uri': str(self.parameters_uri)} # convert from unicode
        if self.input is None:
            state['input'] = 'None'
        else:
            state['input'] = self.input.global_id()
        return hashlib.sha1(pickle.dumps(state)).hexdigest()

    def __unicode__(self):
        return '<ComponentState: type=%s, uri=%s, input=%s>' % (str(self.type),
                                                                self.parameters_uri,
                                                                self.input and self.input.global_id() or 'None')

class DataItem(models.Model):
    attribute_name = models.CharField(max_length=100)
    component_state = models.ForeignKey(ComponentState)
 
    def _make_filename(self, root_dir):
        cs = self.component_state
        path = os.path.join(root_dir, cs.global_id() + ".dj")
        if not (os.path.exists(path) and os.path.isdir(path)):
            os.makedirs(path)
        filename = os.path.join(path, self.attribute_name)
        return filename
    
    def get_data(self, root_dir):
        path = self._make_filename(root_dir)
        f = open(path, 'r')
        data = pickle.load(f)
        f.close()
        return data
    
    def store_data(self, root_dir, data):
        path = self._make_filename(root_dir)
        f = open(path, 'w')
        pickle.dump(data, f)
        f.close()
        
    def __unicode__(self):
        return "(%s %s)" % (self.component_state, self.attribute_name)

from rest_framework import serializers
from eoftermapp.models import EFOterm,ParentRelationship

class DynamicFieldsEFOtermSerializer(serializers.ModelSerializer):
    parent_id = serializers.CharField(write_only=True, required=False)
    child_id = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = EFOterm
        fields = ['efo_term_id', 'term_name', 'synonyms', 'parent_id','child_id']

    def create(self, validated_data):
        parent_id = validated_data.pop('parent_id', None)
        child_id = validated_data.pop('child_id', None)
        efo_term = EFOterm.objects.create(**validated_data)
        if parent_id:
            parent_term = EFOterm.objects.get(efo_term_id=parent_id)
            ParentRelationship.objects.create(term=efo_term, parent=parent_term)
        if child_id:
            child_term=EFOterm.objects.get(efo_term_id=child_id)
            ParentRelationship.objects.create(term=child_term, parent=efo_term)
        return efo_term

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsEFOtermSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                if field_name!="efo_term_id":
                    self.fields.pop(field_name)
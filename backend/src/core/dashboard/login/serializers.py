from rest_framework import serializers


class MyUserTokenSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()

    def to_representation(self,instance):
        data = super().to_representation(instance)
        return {
            'id': data['id'],
            'username': data['username'],
        }

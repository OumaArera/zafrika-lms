from rest_framework import serializers
from ..models import Topic


class TopicNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Topic
        fields = ["id", "title", "content", "description"]
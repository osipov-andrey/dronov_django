from rest_framework import serializers

from main.models import Bb, Comment, SubRubric


class BbSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bb
        fields = ('id', 'title', 'content', 'price', 'created_at')  # остальные поля (контакты, изображения), в целях
        # компактности будем отправлять в составе сведений о выбранном рипложени


class BbDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bb
        fields = ('id', 'title', 'content', 'price', 'created_at', 'contacts', 'image')


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('bb', 'author', 'content', 'created_at')


class SubRubricSerializer(serializers.ModelSerializer):
    super_rubric = serializers.StringRelatedField()  # Беру из поля FK имя объекта связанной модели

    class Meta:
        model = SubRubric
        fields = ('id', 'name', 'super_rubric')

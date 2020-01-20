from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import RetrieveAPIView
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer

from main.models import Bb, Comment, SubRubric, SuperRubric
from .serializers import BbSerializer, BbDetailSerializer, CommentSerializer, SubRubricSerializer

# Create your views here.
@api_view(['GET'])
def bbs(request):
    if request.method == 'GET':
        bbs = Bb.objects.filter(is_active=True)[:10]
        serializer = BbSerializer(bbs, many=True)
        return Response(serializer.data)


class BbDetailView(RetrieveAPIView):
    queryset = Bb.objects.filter(is_active=True)
    serializer_class = BbDetailSerializer


# @api_view(['GET'])
# def sub_rubrics(request):
#     if request.method == 'GET':
#         rubrics = SubRubric.objects.all()
#         print(rubrics)
#         serializer = SubRubricSerializer(rubrics, many=True)
#         return Response(serializer.data)


class SubRubrics(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'rubrics.html'

    def get(self, request):
        rubrics = SubRubric.objects.all()
        serializer = SubRubricSerializer(rubrics, many=True)
        return Response({'serializer': serializer.data,})


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticatedOrReadOnly,))  # разграничение доступа. Добавлять комменты - зарегистрированные
# пользователи. Просматривать - все.
def comments(request, pk):
    if request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    else:
        comments = Comment.objects.filter(is_active=True, bb=pk)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
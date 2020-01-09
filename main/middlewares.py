from .models import SubRubric


# ----------------------------------------------РУБРИКИ-----------------------------------------------------------#
def bboard_context_processor(request):
    """ Добавление в контекст шаблонов переменной rubrics, содержащей все рубрики. """
    context = {}
    context['rubrics'] = SubRubric.objects.all()
    return context

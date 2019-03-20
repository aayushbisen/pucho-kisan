from django.template.defaulttags import register


@register.filter
def answer_markup(answer, farmer):
    return answer.markup(farmer)


@register.filter
def question_markup(question, farmer):
    return question.markup(farmer)
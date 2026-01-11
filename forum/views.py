from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import (
    get_object_or_404, redirect, render, reverse, Http404
)

from . import forms as custom_forms
from .models import Farmer, Question, Answer, Specialist, QuestionFile
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.translation import get_language

from .validators import validate_file_extension, validate_file_size

from django.contrib.auth.hashers import check_password, make_password
from django.views import generic

# Helpers

def language_details(request):
    
    language_code = get_language()

    another_language = {
        'en': 'हिंदी',
        'hi': 'english'
    }[language_code]

    current_url = request.get_full_path()

    url_for_language_change = {
        'hi': '/en' + current_url,
        'en': current_url[3:],
    }[language_code]

    return {
        'another_language': another_language,
        'url_for_language_change': url_for_language_change
    }


def loggined_farmer_id(request):
    """ Gives the id of the currently logged in farmer
        returns `None` if no farmer is logged in
    """

    return request.session.get("farmer_id", None)


def loggined_farmer(request):
    return get_object_or_404(
        Farmer,
        pk=loggined_farmer_id(request)
    )


def is_loggined(request):

    try:
        farmer_id = request.session.get("farmer_id")
        Farmer.objects.get(id=farmer_id)
        return True

    except Farmer.DoesNotExist:
        return False


def login_required(function):

    def wrapper(request, *args, **kwargs):

        if is_loggined(request):
            return function(request, *args, **kwargs)

        return redirect("forum:login")

    return wrapper


def basic_inner_context(request):
    """Basic context for inner views """

    farmer = loggined_farmer(request)
    top_questions = Question.trending()

    return {
        'farmer': farmer,
        'top_questions': top_questions,
        **language_details(request),
    }

# Create your views here.
# Views start here


def login(request, verify_message=""):

    login_form = custom_forms.LoginForm()

    if request.method == "POST":

        login_form = custom_forms.LoginForm(request.POST)

        if login_form.is_valid():

            phone_number = login_form.cleaned_data['phone_number']
            password = login_form.cleaned_data['password']

            try:
                farmer = Farmer.objects.get(phone_number=phone_number)

                if check_password(password, farmer.password):

                    # if not farmer.is_active:
                    #     login_form.add_error('phone_number', _(
                    #         "Account is not activated"))

                    # else:
                    request.session['farmer_id'] = farmer.id
                    return redirect("forum:home")

                if farmer.is_active:
                    login_form.add_error('password', _("Invalid password"))

            except Farmer.DoesNotExist:
                login_form.add_error('phone_number', _(
                    "No Farmer found with this phone number"))

    return render(request, "forum/outer/login.html", {
        'form': login_form,
        'verify_message': verify_message,
        **language_details(request),
    })


# def signup(request):

#     signup_form = custom_forms.SignupForm()

#     is_message_send = False

#     if request.method == "POST":

#         signup_form = custom_forms.SignupForm(request.POST)

#         if signup_form.is_valid():

#             new_farmer = signup_form.save()

#             password = make_password(signup_form.cleaned_data['password'])
#             new_farmer.password = password

#             new_farmer.save()

#             # verification message send
#             new_farmer.send_verification_link()
#             is_message_send = True

#     return render(request, "forum/outer/signup.html", {
#         'form': signup_form,
#         'is_message_send': is_message_send,
#         **language_details(request),

#     })


def goverment_rules(request):

    rules = [
        {
            'name': _("Rastriya Krishi Vikas Yojna (RKVY)"),
            'description': _("It is implemented with a view to promote organic farming in the country. To improve soil health and organic matter content and increase net income of the farmer so as to realise premium prices.  Under this scheme, an area of 5 lakh acre is targeted to be covered though 10,000 clusters of 50 acre each, from the year 2015-16 to 2017-18."),
            'link': 'http://agriportal.cg.nic.in/agridept/AgriEn/CentralScheme.html#collapseFive'
        },
        {
            'name': _("Crop Insurance"),
            'description': _("Crop insurance is purchased by agricultural producers, and subsidized by the federal government, to protect against either the loss of their crops due to natural disasters, such as hail, drought, and floods, or the loss of revenue due to declines in the prices of agricultural commodities."),
            'link': 'http://agriportal.cg.nic.in/agridept/AgriEn/CentralScheme.html#collapseOne'
        },
        {
            'name': _("National Mission on Sustainable Agriculture (NMSA)"),
            'description': _("NMSA is one of the eight Missions under National Action Plan on Climate Change (NAPCC). It aims at promoting Sustainable Agriculture through climate change adaptation measures, enhancing agriculture productivity especially in rainfed areas focusing on integrated farming, soil health management, and synergizing resource conservation. NMSA as a programmatic intervention caters to Mission Deliverables that focuses mainly on conservation agriculture to make farm sector more productive, sustainable, remunerative and climate resilient by promoting location specific integrated/composite farming systems."),
            'link': 'http://agriportal.cg.nic.in/agridept/AgriEn/CentralScheme.html#collapseOne'
        },
        {
            'name': _("National Food Security Mission (NFSM)"),
            'description': _("In view of the stagnating food grain production and an increasing consumption need of the growing population, Government of India has launched this Centrally Sponsored Scheme, ‘National Food Security Mission’ in October 2007. The Mission met with an overwhelming success and achieved the targeted additional production of rice, wheat and pulses. The Mission continued during 12th Five Year Plan with new targets of additional production of food grains of 25 million tonnes of food grains comprising of 10 million tonnes rice, 8 million tonnes of wheat, 4 million tonnes of pulses and 3 million tonnes of coarse cereals by the end of 12th Five Year Plan."),
            'link': 'http://agriportal.cg.nic.in/agridept/AgriEn/CentralScheme.html#collapseOne'
        },
        {
            'name': _("National Mission on Agriculture Extension & Technology (NMAET)"),
            'description': _("The objective of the Scheme is to make the extension system farmer-driven and farmer-accountable by way of new institutional arrangements for technology dissemination. It aims to restructure and strengthen agricultural extension to enable delivery of appropriate technology and improved agronomic practices to farmers."),
            'link': 'http://agriportal.cg.nic.in/agridept/AgriEn/CentralScheme.html#collapseOne'
        }
    ]

    return render(request, "forum/outer/govt_rules.html", {
        "rules": rules,
        **language_details(request),
    })


def index(request):

    # Show home if loggined

    if is_loggined(request):
        return home(request)

    # else show login page
    return login(request)


@login_required
def home(request):

    current_farmer = loggined_farmer(request)

    DEFAULT_CHOICE = 'all'
    categories = [DEFAULT_CHOICE, 'AN', 'PE', 'SU', 'SE', 'SA']
    category = request.GET.get("category")

    if category not in categories:
        category = DEFAULT_CHOICE

    all_questions = Question.objects.all()

    questions_from_nearby_farmers = (
        current_farmer.questions_from_nearby_farmers()
    )

    questions = {
        DEFAULT_CHOICE: all_questions,
        'AN': all_questions.filter(category='AN'),
        'PE': all_questions.filter(category='PE'),
        'SU': all_questions.filter(category='SU'),
        'SE': all_questions.filter(category='SE'),
        'SA': questions_from_nearby_farmers
    }[category]

    category_name = Question.full_category_name(category, _("All"))

    return render(request, "forum/inner/home.html", {
        **basic_inner_context(request),
        'questions': questions.order_by("-date_time_created"),
        'category': category,
        'category_name': category_name,
        'show_filter': True
    })


# def create_question(request):

#     FILE_LIMIT = 10
#     error_occured = False

#     create_form = custom_forms.CreateQuestionForm()

#     if request.method == "POST":

#         create_form = custom_forms.CreateQuestionForm(request.POST)
#         files = request.FILES.getlist('file_field')

#         if create_form.is_valid():

#             question = create_form.save(commit=False)
#             question.asked_by = loggined_farmer(request)
#             question.save()

#             if len(files) > FILE_LIMIT:
#                 create_form.add_error('file_field', _(
#                     "Upto 10 files can be attached with a question"))
#                 error_occured = True

#             for f in files:

#                 try:
#                     validate_file_extension(f)
#                     validate_file_size(f)

#                     question_file = QuestionFile.objects.create()
#                     question_file.save()

#                     question_file.question_file = f
#                     question_file.save()

#                     question.files.add(question_file)
#                     question.save()

#                 except ValidationError as e:
#                     create_form.add_error('file_field', e)
#                     error_occured = True

#             if error_occured:
#                 question.delete()

#             else:
#                 return HttpResponseRedirect(question.get_absolute_url())

#     return render(request, "forum/inner/question_create.html", {
#         **basic_inner_context(request),
#         'form': create_form
#     })


class QuestionUpdateView(generic.UpdateView):
    model = Question
    template_name = "question_update.html"


class QuestionDeleteView(generic.DeleteView):
    model = Question
    template_name = "question_delete.html"


class FarmerDetailView(generic.DetailView):
    model = Farmer
    template_name = "forum/inner/farmer_detail.html"

    def get_context_data(self, **kwargs):

        DEFAULT_CHOICE = 'all'
        categories = [DEFAULT_CHOICE, 'AN', 'PE', 'SU', 'SE']
        category = self.request.GET.get("category")

        if category not in categories:
            category = DEFAULT_CHOICE

        context = super().get_context_data(**kwargs)

        farmer = self.get_object()

        all_questions = Question.objects.filter(
            asked_by__id=farmer.id
        ).order_by("-date_time_created")

        questions = {
            DEFAULT_CHOICE: all_questions,
            'AN': all_questions.filter(category='AN'),
            'PE': all_questions.filter(category='PE'),
            'SU': all_questions.filter(category='SU'),
            'SE': all_questions.filter(category='SE'),
        }[category]

        category_name = Question.full_category_name(category, _("All"))

        context = {
            **basic_inner_context(self.request),
            'questions': questions,
            'show_filter': True,
            'category': category,
            'category_name': category_name,
            'profile': farmer
        }

        return context


class FarmerUpdateView(generic.UpdateView):

    template_name = "forum/inner/farmer_edit.html"
    form_class = custom_forms.FarmerEditForm

    def get_object(self):
        return loggined_farmer(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        farmer = loggined_farmer(self.request)

        context = {
            **context,
            **basic_inner_context(self.request),
        }

        return context


def question_detail_view(request, pk):

    question = get_object_or_404(Question, pk=pk)
    answer_form = custom_forms.CreateAnswerForm()

    if request.method == "POST":
        answer_form = custom_forms.CreateAnswerForm(request.POST)

        if answer_form.is_valid():

            answer = answer_form.save(commit=False)
            answer.answer_of = question
            answer.answered_by = loggined_farmer(request)
            answer.save()

    return render(request, "forum/inner/question_detail.html", {
        **basic_inner_context(request),
        'question': question,
        'form': answer_form
    })


@login_required
def search(request):

    search_term = request.GET.get("q", "")

    # Empty question sets
    questions = Question.objects.none()

    # Appending the results
    if search_term:
        # spliting the whole sentence into words
        search_words = search_term.split()

        for search_word in search_words:
            questions |= Question.objects.filter(
                question__icontains=search_word,
            )

            questions |= Question.objects.filter(
                category__icontains=search_word,
            )

    else:
        questions = Question.trending()

    return render(request, "forum/inner/search.html", {
        **basic_inner_context(request),
        'search_term': search_term,
        'questions': questions
    })


def specialists(request):

    specialist = Specialist.objects.all()

    return render(request, "forum/inner/specialist_list.html", {
        **basic_inner_context(request),
        'specialists': specialist
    })


def logout(request):

    try:
        del request.session['farmer_id']
        return redirect("forum:login")

    except KeyError:
        return HttpResponse("")


# AJAX views

@login_required
def upvote_question(request):

    if request.method == "POST":

        question_id = request.POST.get("question_id")
        question = get_object_or_404(Question, pk=question_id)

        farmer = loggined_farmer(request)

        question.toggle_upvote_by(farmer)

        return HttpResponse(question.upvotes, content_type="text/plain")

    raise Http404


@login_required
def upvote_answer(request):

    if request.method == "POST":

        answer_id = request.POST.get("answer_id")
        answer = get_object_or_404(Answer, pk=answer_id)

        farmer = loggined_farmer(request)

        answer.toggle_upvote_by(farmer)

        return HttpResponse(answer.upvotes, content_type="text/plain")

    raise Http404


def verify_farmer(request, phone_number, account_token):

    farmer = get_object_or_404(Farmer, phone_number=phone_number)

    status = farmer.activate_account(account_token)

    message = {
        200: _("Account activated"),
        300: _("This link has expired"),
        400: _("Account is already activated")
    }[status]

    return render(request, "forum/outer/verify.html", {
        'message': message
    })


def team_page(request):

    team_data = [
        {
            'name': "Aayush Bisen",
            'badge': "front end dev",
            'avatar_link': "https://avatars2.githubusercontent.com/u/41341387",
            'github_link': "https://github.com/aayushbisen",
            'linked_in_link': "https://www.linkedin.com/in/aayush-bisen-b79268157/",
            'description': "Aayush is a Computer Science Undergrad. \
                He is an open-source enthusiast and football lover.  ",
        },
        {
            'name': "Harsh Singh",
            'badge': "front end dev",
            'avatar_link': "https://avatars1.githubusercontent.com/u/29140145",
            'github_link': "https://github.com/harshsngh07",
            'linked_in_link': "https://www.linkedin.com/in/harsh-singh-4b950b46/",
            'description': "Harsh is a Computer Science Undergrad. \
            He is a passionate learner and wants to work in the field of \
                 Artificial Intelligence.",
        },
        {
            'name': "Piyush Kumar",
            'badge': "front end dev",
            'avatar_link': "https://avatars3.githubusercontent.com/u/41803008",
            'github_link': "https://github.com/piyushkumarsingh",
            'linked_in_link': "https://www.linkedin.com/in/piyush-kumar-singh-1b8374153/",
            'description': "Piyush is a Computer Science Undergrad. Music is my world. He wants to work in the field of ML and AI",
        },
        {
            'name': "Prateek Chatterjee",
            'badge': "front end dev",
            'avatar_link': "https://avatars0.githubusercontent.com/u/40174790",
            'github_link': "https://github.com/Prateek0803",
            'linked_in_link': "https://www.linkedin.com/in/prateek-chatterjee-103a6b15b/",
            'description': "Prateek is a Computer Science Undergrad, counter-strike lover and a passionate learner, loves to code in Python.",
        },
        {
            'name': "Suvansh Rana",
            'badge': "full stack dev",
            'avatar_link': "https://avatars0.githubusercontent.com/u/36293610",
            'github_link': "https://github.com/suvnshr",
            'linked_in_link': "https://www.linkedin.com/in/suvnshr",
            'description': "Suvansh Rana is a Full-stack software engineer with 4.5+ years of experience working with the MERN stack, focused on clean code, performance, and real-world products.",
        },
    ] 


    return render(request, "forum/outer/team_page.html", {
        'team_data': team_data,
        **language_details(request),
    })


def feedback(request):
    return render(request, "forum/outer/feedback.html", {
        **language_details(request),
    })

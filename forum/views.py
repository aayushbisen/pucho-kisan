from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import (
    get_object_or_404, redirect, render, reverse, Http404
)

from . import forms as custom_forms
from .models import Farmer, Question, Answer, Specialist, QuestionFile
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError

from .validators import validate_file_extension, validate_file_size

from django.contrib.auth.hashers import check_password, make_password
from django.views import generic

# Helpers


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
        'top_questions': top_questions
    }

# Create your views here.
# Views start here


def login(request):

    login_form = custom_forms.LoginForm()

    if request.method == "POST":

        login_form = custom_forms.LoginForm(request.POST)

        if login_form.is_valid():

            phone_number = login_form.cleaned_data['phone_number']
            password = login_form.cleaned_data['password']

            try:
                farmer = Farmer.objects.get(phone_number=phone_number)

                if check_password(password, farmer.password):
                    request.session['farmer_id'] = farmer.id
                    return redirect("forum:home")

                # Else
                login_form.add_error('password', _("Invalid password"))

            except Farmer.DoesNotExist:
                login_form.add_error('phone_number', _("No Farmer found with this phone number"))

    return render(request, "forum/outer/login.html", {
        'form': login_form
    })


def signup(request):

    signup_form = custom_forms.SignupForm()

    if request.method == "POST":

        signup_form = custom_forms.SignupForm(request.POST)

        if signup_form.is_valid():

            new_farmer = signup_form.save()

            password = make_password(signup_form.cleaned_data['password'])
            new_farmer.password = password

            new_farmer.save()

            return redirect("forum:home")

    return render(request, "forum/outer/signup.html", {
        'form': signup_form
    })


def goverment_rules(request):

    return render(request, "forum/outer/govt_rules.html")


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


def create_question(request):
    
    FILE_LIMIT = 10
    error_occured = False

    create_form = custom_forms.CreateQuestionForm()

    if request.method == "POST":
        
        create_form = custom_forms.CreateQuestionForm(request.POST)
        files = request.FILES.getlist('file_field')

        if create_form.is_valid():
            
            question = create_form.save(commit=False)
            question.asked_by = loggined_farmer(request)
            question.save()

            if len(files) > FILE_LIMIT:
                create_form.add_error('file_field', _("Upto 10 files can be attached with a question"))
                error_occured = True

            for f in files:

                try:
                    validate_file_extension(f)
                    validate_file_size(f)

                    question_file = QuestionFile.objects.create()
                    question_file.save()

                    question_file.question_file = f
                    question_file.save()

                    question.files.add(question_file)
                    question.save()

                except ValidationError as e:
                    create_form.add_error('file_field', e)
                    error_occured = True

            if error_occured:
                question.delete()
            
            else:
                return HttpResponseRedirect(question.get_absolute_url())


    return render(request, "forum/inner/question_create.html", {
        **basic_inner_context(request),
        'form': create_form
    })

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
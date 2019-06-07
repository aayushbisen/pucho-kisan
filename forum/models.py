import os
import uuid
import requests
from urllib.parse import urlencode

from django.db import models
from django.utils.translation import gettext as _
from django.shortcuts import reverse
from django.template.loader import render_to_string
from .validators import (
    validate_file_extension,
    validate_file_size,
    validate_phone_number,
    validate_zip_code
)
from .file_paths import question_file_path

# Create your models here.


class Farmer(models.Model):

    """ A farmer(also called an agriculturer) is a person engaged in agriculture,
    raising living organisms for food or raw materials.
    The term usually applies to people who do some combination of raising
    field crops, orchards, vineyards, poultry, or other livestock.
    A farmer might own the farmed land or might work as a laborer
    on land owned by others, but in advanced economies,
    a farmer is usually a farm owner, while employees
    of the farm are known as farm workers, or farmhands """

    name = models.CharField(_("Farmer's name"), max_length=50)
    password = models.CharField(_("Farmer's password"), max_length=100)
    phone_number = models.CharField(_("Phone number"), max_length=20, unique=True)
    zip_code = models.IntegerField(_("Zip code"),
                                   validators=[validate_zip_code], blank=True, null=True)

    date_time_created = models.DateTimeField(auto_now_add=True)
    account_token = models.CharField(max_length=20, default=str(uuid.uuid4())[:20], blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("forum:farmer_detail", kwargs={"pk": self.pk})

    @staticmethod
    def generate_account_token():
        return str(uuid.uuid4()[:20])

    def refresh_account_token(self):
        self.account_token = self.generate_account_token()
        self.save()

    def send_verification_link(self):

        TEMPLATE_ID = 8203
        API_KEY = "47ftJlFUczY3eVTSbupGm1yjMxH6QDgAWhXs5EKvOadoqkwLRBfDU8plrv70ncJFqKTIwXNb3QZYCt92"

        url = "https://www.fast2sms.com/dev/bulk"

        payload = {
            'sender_id': 'FSTSMS',
            'language': 'english',
            'route': 'qt',
            'numbers': f"{self.phone_number}",
            'message': TEMPLATE_ID,
            'variables': '{#BB#}|{#DD#}',
            'variables_values': f'{self.phone_number}|{self.account_token}'
        }

        payload = urlencode(payload)

        headers = {
            'authorization': API_KEY,
            'cache-control': "no-cache",
            'content-type': "application/x-www-form-urlencoded"
        }

        response = requests.request(
          "POST", url, data=payload, headers=headers)

        print(response.text)

    def activate_account(self, recieved_account_token):

        if self.is_active:
            return 400

        if self.account_token == recieved_account_token:
            self.is_active = True
            self.save()
            return 200

        # if account token is wrong
        return 300

    @property
    def region_and_sub_region_code(self):
        """ Getting the first 2 digits of this farmers `zip_code`
         the first digit represents the `region`
         the second digit represent the `sub region` """

        return self.zip_code // 10000

    def nearby_farmers(self):
        """ `QuerySet` of farmers present nearby """

        region_and_sub_region_code = self.region_and_sub_region_code
        return Farmer.objects.filter(
            zip_code__startswith=region_and_sub_region_code
        ).exclude(pk=self.pk)

    def questions_from_nearby_farmers(self):
        """ Get questions asked by nearby farmers """

        return Question.objects.filter(
            asked_by__id__in=self.nearby_farmers()
        )


class Question(models.Model):

    """ A questions is asked by a farmer  """

    CATEGORIES = (
        ('AN', _('Animals')),
        ('PE', _('Pests')),
        ('SU', _('Purchase')),
        ('SE', _('Crop')),
    )

    category = models.CharField(
        _("Category"), max_length=2, choices=CATEGORIES, default="PE")
    asked_by = models.ForeignKey(
        "Farmer", on_delete=models.CASCADE, related_name="asked_by")
    question = models.TextField(_("Ask a question"), max_length=1000)
    date_time_created = models.DateTimeField(auto_now_add=True)
    upvoted_by = models.ManyToManyField(
        "Farmer", related_name="question_upvoted_by")

    files = models.ManyToManyField("QuestionFile", blank=True)

    def __str__(self):
        return self.question

    def get_absolute_url(self):

        return reverse("forum:question_detail", kwargs={
            'pk': self.pk
        })

    def list_view(self):
        
        return render_to_string("forum//inner/question_list.html", {
            'question': self,
        })

    def card_view(self, farmer):

        is_upvoted = farmer in self.upvoted_by.all()

        return render_to_string("forum/inner/question_card.html", {
            'question': self,
            'is_upvoted': is_upvoted

        })

    @staticmethod
    def full_category_name(key_name, default=None):
        """ Get the category name according to the provided  `key_name` """

        return {
            'AN': _("Animals"),
            'PE': _("Pests"),
            'SU': _("Purchase"),
            'SE': _("Crop"),
            'SA': _("In your area"),
        }.get(key_name, default)

    def category_name(self):
        """ Get the full category name """

        return self.full_category_name(self.category)

    @property
    def upvotes(self):
        """ Gives the number of upvotes on this questions """
        return self.upvoted_by.all().count()

    def answers(self):
        """ Gives the answers of the current question """

        return Answer.objects.filter(
            answer_of__id=self.id
        )

    @classmethod
    def trending(cls):
        """ Gives the top questions """

        all_questions = cls.objects.all()

        top_questions = reversed(
            sorted(
                all_questions,
                key=lambda question: question.upvotes
            )
        )

        return list(top_questions)[:5]

    def most_upvoted_answers(self):
        """ Give the most upvoted answers on this question"""

        all_answers = self.answers()

        top_answers = reversed(
            sorted(
                all_answers,
                key=lambda answer: answer.upvotes
            )
        )

        return top_answers

    def toggle_upvote_by(self, farmer):
        """ Toggle upvote on this question by a `farmer` """

        if farmer not in self.upvoted_by.all():
            self.upvoted_by.add(farmer)

        else:
            self.upvoted_by.remove(farmer)


class Answer(models.Model):

    """ Answer to a question asked by farmer  """

    answered_by = models.ForeignKey(
        Farmer, on_delete=models.CASCADE, related_name="answered_by")
    answer_of = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField(_("Answer the question"), max_length=1000)
    date_time_created = models.DateTimeField(auto_now_add=True)
    upvoted_by = models.ManyToManyField(
        "Farmer", related_name="answer_upvoted_by")

    def __str__(self):
        return self.answer

    def markup(self, farmer):

        is_upvoted = farmer in self.upvoted_by.all()

        return render_to_string("forum/inner/answer.html", {
            'answer': self,
            'is_upvoted': is_upvoted
        })

    @property
    def upvotes(self):
        """ Gives the number of upvotes on this answer """
        return self.upvoted_by.all().count()

    def toggle_upvote_by(self, farmer):
        """ Toggle upvote on this answer by a `farmer` """

        if farmer not in self.upvoted_by.all():
            self.upvoted_by.add(farmer)

        else:
            self.upvoted_by.remove(farmer)


class Specialist(models.Model):

    """ People who are experts in farming """

    name = models.CharField(max_length=100)
    phone_number = models.CharField(
        _("Phone number"), max_length=10, validators=[validate_phone_number])
    subject = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class QuestionFile(models.Model):

    """ File to be attached to a question """
    image_extensions = ['.jpg', '.png', '.jpeg', '.svg', '.gif']
    video_extensions = ['.mp4', '.avi', '.3gp']

    question_file = models.FileField(_("Question file"),
                                     upload_to=question_file_path,
                                     validators=[
                                         validate_file_extension,
                                         validate_file_size],
                                     max_length=None)

    def __str__(self):
        return str(self.url)

    @property
    def url(self):
        return self.question_file.url

    @property
    def extension(self):
        return os.path.splitext(self.url)[1]

    @property
    def is_image(self):
        return self.extension.lower() in self.image_extensions

    @property
    def is_video(self):
        return not self.is_image

import os

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


def validate_file_extension(file):

    ext = os.path.splitext(file.name)[1]
    valid_extensions = [
        '.jpg',
        '.mp4',
        '.gif',
        '.png',
        '.avi',
        '.jpeg',
        '.mkv',
    ]

    if not ext.lower() in valid_extensions:

        valid = ", ".join(valid_extensions)

        raise ValidationError(_(f'Only images and videos are allowed'))


def validate_file_size(file):

    limit = 7 * 1024 * 1024

    if file.size > limit:
        raise ValidationError(_('File too large. Size should not exceed 7 MB'))


def validate_phone_number(number):

    if not number.isdigit():
        raise ValidationError(_("Enter a valid phone number"))


def validate_zip_code(zip_code):

    if len(str(zip_code)) != 6:
        raise ValidationError(_("Enter a valid zip code"))

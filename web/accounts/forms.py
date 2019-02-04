from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, PasswordChangeForm
from django.core.validators import EmailValidator

from . models import Profile


def validate_password_strength(value):
    """Validates that a password is as least 7 characters long and has at least
    1 digit and 1 letter.
    """
    min_length = 9

    if len(value) < min_length:
        raise forms.ValidationError(
            'Password must be at least ' + str(min_length) + ' characters long.')

    # check for digit
    if not any(char.isdigit() for char in value):
        raise forms.ValidationError('Password must contain at least 1 digit.')

    # check for letter
    if not any(char.isalpha() for char in value):
        raise forms.ValidationError('Password must contain at least 1 letter.')


class SignUpForm(UserCreationForm):
    class Meta:
        fields = ("username", "email", "password1", "password2")
        model = User

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)
        self.fields["email"].label = "Email Address"
        self.fields["email"].help_text = "Please use a valid .edu email address to register."
        self.fields["username"].label = "Display Name"
        self.fields["password2"].label = 'Confirm Password'


class LoginForm(AuthenticationForm):
    class Meta:
        fields = ("username", "email", "password1", "password2")
        model = User

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Display Name"

    def confirm_login_allowed(self, user):
        if not user.is_active or not user.is_authenticated:
            raise forms.ValidationError(
                'There was a problem with your login.', code='invalid_login')


class EditProfileForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields["username"].label = "Display Name"
        self.fields["email"].label = "Email Address"


class EditGradYearForm(forms.ModelForm):
    grad_year = forms.IntegerField(label='Graduation Year')

    class Meta:
        model = Profile
        fields = ('grad_year',)

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)


class EditProfPicForm(forms.ModelForm):
    avatar = forms.ImageField(label='Profile Picture')

    class Meta:
        model = Profile
        fields = ('avatar',)

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)

    def clean_image(self):
        image = self.cleaned_data.get('image', False)
        if image:
            if image._size > 4*1024*1024:
                raise forms.ValidationError("Image file too large ( > 4mb )")
            return image
        else:
            raise forms.ValidationError("Couldn't read uploaded image")


class EditDisplayNameForm(forms.ModelForm):
    error_messages = {
        'duplicate_username': 'A user with this display name already exists.'
    }

    class Meta:
        model = User
        fields = ("username",)

    def clean_username(self):
        username = self.cleaned_data["username"]

        try:
            User._default_manager.get(username=username)
            # if the user exists, then let's raise an error message

            raise forms.ValidationError(
                # user my customized error message
                self.error_messages['duplicate_username'],
                code='duplicate_username',  # set the error message key
            )
        except User.DoesNotExist:
            return username  # great, this user does not exist so we can continue the registration process

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Display Name"


class EditEmailForm(forms.ModelForm):
    email = forms.CharField(max_length=254, validators=[
                            EmailValidator(message="Please enter a valid email address.")])

    class Meta:
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)
        self.fields["email"].label = "Email"


class EditPasswordForm(PasswordChangeForm):
    class Meta:
        model = get_user_model()
        fields = ("old_password", "new_password1", "new_password2")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(EditPasswordForm, self).__init__(*args, **kwargs)
        # self.fields['new_password1'].validators.append(validate_password_strength)

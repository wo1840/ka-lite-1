from django import forms
from models import RegisteredDevicePublicKey, Zone, FacilityUser, Facility

class RegisteredDevicePublicKeyForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super(RegisteredDevicePublicKeyForm, self).__init__(*args, **kwargs)
        if not user.is_superuser:
            self.fields['zone'].queryset = reduce(lambda x,y: x+y,
                [orguser.get_zones() for orguser in user.organizationuser_set.all()])

    class Meta:
        model = RegisteredDevicePublicKey
        fields = ("zone", "public_key",)


class FacilityUserForm(forms.ModelForm):

    class Meta:
        model = FacilityUser
        fields = ("facility", "username", "first_name", "last_name",)

    password = forms.CharField(widget=forms.PasswordInput, label="Password")


class FacilityForm(forms.ModelForm):

    class Meta:
        model = Facility
        fields = ("name", "description", "address", "latitude", "longitude", "zone",)


class LoginForm(forms.ModelForm):
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    class Meta:
        model = FacilityUser
        fields = ("facility", "username", "password")

    def __init__(self, request=None, *args, **kwargs):
        self.user_cache = None
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['facility'].queryset = Facility.objects.all()


    def clean(self):
        username = self.cleaned_data.get('username')
        facility = self.cleaned_data.get('facility')
        password = self.cleaned_data.get('password')

        try:
            self.user_cache = FacilityUser.objects.get(username=username, facility=facility)
        except FacilityUser.DoesNotExist as e:
            raise forms.ValidationError("User not found. Did you type your username correctly, and choose the right facility?")
        
        if not self.user_cache.check_password(password):
            self.user_cache = None
            if password and "password" not in self._errors:
                self._errors["password"] = ["Password was incorrect."]
        
        return self.cleaned_data

    def get_user(self):
        return self.user_cache

# class OrganizationForm(forms.ModelForm):
#     class Meta:
#         model = Organization
#         fields = ("name", "description", "url",)
#         widgets = {
#             "name": forms.TextInput(attrs={"size": 70}),
#             "description": forms.Textarea(attrs={"cols": 74, "rows": 2}),
#             "url": forms.TextInput(attrs={"size": 70}),
#         }

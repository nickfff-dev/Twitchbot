from django import forms
from django.forms import DateInput
from django.forms import ModelChoiceField

from TwitchBot import main
from TwitchBot.models import TwitchBot, SocialMediaAccount, Post


# TAGS = (
#     (1, "Channel"),
#     (2, "Game"),
#     (3, "Creation Date"),
#     (4, "Views"),
#     (5, "Curator"),
#     (6, "Trending"),
# )


class SelectByName(ModelChoiceField):
    def label_from_instance(self, account):
        return account.username + " (" + main.account_types.get(account.type) + ")"


class SelectLanguage(ModelChoiceField):
    def label_from_instance(self, account):
        return account.username + " (" + main.account_types.get(account.type) + ")"


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class CreateBotForm(forms.ModelForm):
    account = SelectByName(queryset=SocialMediaAccount.objects.all(), empty_label=None)
    language = forms.ChoiceField(choices=[(lang, lang) for lang in main.languages.keys()])

    class Meta:
        model = TwitchBot
        fields = "__all__"
        exclude = ("last_run",)
        widgets = {
            'created_after': DateInput(attrs={'type': 'date'})
        }


class EditBotForm(CreateBotForm):
    class Meta:
        model = TwitchBot
        fields = "__all__"
        exclude = ("name", "last_run",)
        widgets = {
            'created_after': DateInput(attrs={'type': 'date'})
        }


class CreateTwitterAccount(forms.ModelForm):
    class Meta:
        model = SocialMediaAccount
        fields = ['username', 'consumer_key', 'consumer_key_secret', 'access_token', 'access_token_secret', 'period']


class CreateInstagramAccount(forms.ModelForm):
    class Meta:
        model = SocialMediaAccount
        fields = ['username', 'password', 'period']
        widgets = {
            'password': forms.PasswordInput(render_value=True),
        }


class EditPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['caption']


# class EditAccountForm(forms.ModelForm):
#     class Meta:
#         model = SocialMediaAccount
#         fields = "__all__"
#         widgets = {
#             'password': forms.PasswordInput(),
#         }


"""
channel: string
game: string
time: int, less than
views: int, greater than
created-after: day
curator: string
trending: boolean
-          Posts which are within a certain time constraint
-          Posts which are within a certain view amount
-          Posts created on a certain day
-          Posts by a certain curator
-          Posts that are trending

https://dev.twitch.tv/docs/v5/reference/clips/

"""

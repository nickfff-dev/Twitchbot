from django.db import models

from TwitchBot import util


class Post(models.Model):
    clip_url = models.TextField()
    clip_slug = models.TextField()
    thumbnail_url = models.TextField()
    download_url = models.TextField()
    caption = models.TextField()
    posted = models.BooleanField(default=False)
    post_minute = models.IntegerField()
    queued_time = models.DateField(default=util.get_current_time)
    post_time = models.DateField(null=True)
    bot = models.ForeignKey('TwitchBot', on_delete=models.CASCADE)
    account = models.ForeignKey('SocialMediaAccount', on_delete=models.CASCADE)


class IntegerRangeField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.IntegerField.__init__(self, verbose_name, name, **kwargs)


    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value': self.max_value}
        defaults.update(kwargs)
        return super(IntegerRangeField, self).formfield(**defaults)


class SocialMediaAccount(models.Model):
    type = models.IntegerField()
    username = models.CharField(max_length=100)
    password = models.CharField(null=True, max_length=100)
    consumer_key = models.CharField(null=True, max_length=100)
    consumer_key_secret = models.CharField(null=True, max_length=100)
    access_token = models.CharField(null=True, unique=True, max_length=100)
    access_token_secret = models.CharField(null=True, max_length=100)
    period = IntegerRangeField(min_value=5, max_value=24 * 60)
    followers = models.IntegerField(default=0)
    posts = models.IntegerField(default=0)


    def get_type_name(self):
        return "Twitter" if self.type == 1 else "Instagram"

    class Meta:
        unique_together = ('type', 'username',)


class TwitchBot(models.Model):
    name = models.CharField(unique=True, max_length=100)
    account = models.ForeignKey('SocialMediaAccount', on_delete=models.CASCADE)
    channel = models.CharField(blank=True, max_length=100)
    game = models.CharField(blank=True, max_length=100)
    curator = models.CharField(blank=True, max_length=100)
    created_after = models.DateField(default=util.get_current_time)
    max_length = models.IntegerField(default=60)
    min_views = models.IntegerField(default=0)
    trending = models.BooleanField(default=False)
    language = models.CharField(blank=True, max_length=100)
    priority = models.IntegerField(default=1)
    max_posts = models.IntegerField(default=1)
    post_count = models.IntegerField(blank=True, default=0)
    last_run = models.IntegerField(default=0)
    captions = models.TextField(blank=True)


    def is_active(self):
        return self.created_after <= util.get_current_time().date()

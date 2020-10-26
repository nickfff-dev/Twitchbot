from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect

from TwitchBot import main, util
from TwitchBot.forms import LoginForm, CreateTwitterAccount, CreateInstagramAccount, EditBotForm, CreateBotForm, \
    EditPostForm
from TwitchBot.models import TwitchBot, Post, SocialMediaAccount
from TwitchBot.util import AuthenticationError


def login(request):
    if (request.user.is_authenticated):
        return redirect("/dashboard")

    form = LoginForm(request.POST) if request.POST else LoginForm()
    if form.is_valid():
        print('here ', request.POST)
        if request.POST:
            username = request.POST['username']
            password = request.POST['password']

            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return redirect("/dashboard")

    if request.POST:
        # User not authenticated
        form.add_error("password", "Invalid username or password")

    return render(request, "login.html", {'form': form})


def logout(request):
    auth.logout(request)
    return redirect("/login")


@login_required(login_url='/login')
def dashboard(request):
    remove = "remove" in request.path

    if remove:
        delete_id = request.GET.get('id')
        if delete_id is not None:
            TwitchBot.objects.filter(id=delete_id).delete()  # If it doesn't exist this will just continue
            return redirect('dashboard')

    return render(request, "dashboard.html", {"twitch_bots": TwitchBot.objects.all().order_by("-priority"),
                                              "remove": remove})


@login_required(login_url='/login')
def create_bot(request):
    form = CreateBotForm(request.POST) if request.POST else CreateBotForm()
    if form.is_valid():
        form.save()
        return redirect('/dashboard')

    return render(request, "forms/bots.html", {"title": "Create Twitch Bot",
                                               "languages": main.languages,
                                               "form": form})


@login_required(login_url='/login')
def edit_bot(request):
    edit_id = request.GET.get('id')
    bot = TwitchBot.objects.filter(id=edit_id).first()
    if bot is None:
        return redirect('dashboard')

    form = EditBotForm(request.POST, instance=bot) if request.POST else EditBotForm(instance=bot)
    if form.is_valid():
        bot.captions = form.cleaned_data['captions']
        bot.save()
        return redirect('dashboard')

    return render(request, "forms/bots.html", {"title": "Editing " + bot.name,
                                               "languages": main.languages,
                                               "editing": True,
                                               "bot": bot,
                                               "form": form,
                                               "text": bot.captions})


@login_required(login_url='/login')
def upcoming(request):
    remove = "remove" in request.path

    if remove:
        delete_id = request.GET.get('id')
        if delete_id is not None:
            Post.objects.filter(id=delete_id).delete()  # If it doesn't exist this will just continue
            return redirect('delete_post')

    now = util.get_current_time()
    current_minute = (60 * now.hour) + now.minute
    regenerate = request.GET.get('regenerate')
    if regenerate is not None and regenerate:
        main.generate_queue(current_minute)
        return redirect('upcoming')

    upcoming_posts = Post.objects.filter(posted=False).order_by('post_minute')
    for post in upcoming_posts:
        diff = post.post_minute - current_minute
        if diff > 0:
            hours = diff // 60
            minutes = diff % 60
            post.time_remaining = "{:0>2d}:{:0>2d}".format(hours, minutes)
        else:
            post.time_remaining = "In Progress"

    return render(request, "upcoming_posts.html", {"upcoming_posts": upcoming_posts,
                                                   "remove": remove})


@login_required(login_url='/login')
def edit_upcoming(request):
    edit_id = request.GET.get('id')
    post = Post.objects.filter(id=edit_id).first()
    if post is None:
        return redirect('upcoming')

    form = EditPostForm(request.POST, instance=post) if request.POST else EditPostForm(instance=post)
    if form.is_valid():
        post.captions = form.cleaned_data['caption']
        post.save()
        return redirect('upcoming')

    return render(request, "forms/posts.html",
                  {"title": "Editing Post for " + post.account.username + " (" + post.account.get_type_name() + ")",
                   "editing": True,
                   "form": form,
                   "text": post.caption})


@login_required(login_url='/login')
def accounts(request):
    remove = "remove" in request.path

    if remove:
        delete_id = request.GET.get('id')
        if delete_id is not None:
            SocialMediaAccount.objects.filter(id=delete_id).delete()  # If it doesn't exist this will just continue
            return redirect('accounts')

    total_followers = SocialMediaAccount.objects.aggregate(Sum('followers'))['followers__sum']
    total_posts = SocialMediaAccount.objects.aggregate(Sum('posts'))['posts__sum']
    total_followers = 0 if total_followers is None else total_followers
    total_posts = 0 if total_posts is None else total_posts
    return render(request, "accounts.html",
                  {"accounts": SocialMediaAccount.objects.all(),
                   "remove": remove,
                   "total_followers": total_followers,
                   "total_posts": total_posts})


@login_required(login_url='/login')
def create_account(request):
    account_type = request.GET.get('type')
    account_type = int(account_type) if account_type is not None else None
    if request.POST:
        form = CreateTwitterAccount(request.POST) if account_type == 1 else CreateInstagramAccount(request.POST)
    else:
        form = CreateTwitterAccount() if account_type == 1 else CreateInstagramAccount()

    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.type = account_type
            util.update_stats(model)
            model.save()
            return redirect("/accounts")
        except AuthenticationError:
            form.add_error("access_token_secret" if account_type == 1 else "password",
                           "Invalid credentials! Please double check the provided credentials")

    return render(request, "forms/accounts.html", {
        "title": "Add {type} Account".format(
            type="Twitter" if account_type == 1 else "Instagram" if account_type == 2 else "Social Media"),
        "form": form,
        "account_type": account_type})


@login_required(login_url='/login')
def edit_account(request):
    edit_id = request.GET.get('id')
    account = SocialMediaAccount.objects.filter(id=edit_id).first()
    if account is None:
        return redirect('accounts')

    if request.POST:
        form = CreateTwitterAccount(request.POST, instance=account) if account.type == 1 \
            else CreateInstagramAccount(request.POST, instance=account)
    else:
        form = CreateTwitterAccount(instance=account) if account.type == 1 \
            else CreateInstagramAccount(instance=account)
    # form = EditAccountForm(request.POST, instance=account) if request.POST else EditAccountForm(instance=account)
    print(account.password)
    if form.is_valid():
        try:
            # account.password = form.cleaned_data['password']
            # account.period = form.cleaned_data['period']
            # account.save()
            # return redirect('accounts')
            model = form.save(commit=False)
            model.type = account.type
            util.update_stats(model)
            model.save()
            return redirect("/accounts")
        except AuthenticationError:
            form.add_error("access_token_secret" if account.type == 1 else "password",
                           "Invalid credentials! Please double check the provided credentials")

    return render(request, "forms/accounts.html", {
        "title": "Editing " + account.username + " (" + account.get_type_name() + ")",
        "account_type": account.type,
        "editing": True,
        "form": form})

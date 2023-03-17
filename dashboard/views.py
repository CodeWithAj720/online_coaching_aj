from pyexpat.errors import messages
from django.shortcuts import redirect, render
from . forms import *
from django.contrib import messages
from django.views import generic
from youtubesearchpython import VideosSearch
import requests
import wikipedia
from django.contrib.auth.decorators import login_required
# Create your views here
def home(request):
    return render(request,'dashboard/home.html')
@login_required
def notes(request):
    if request.method == "POST":
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user,title=request.POST['title'],description=request.POST['description'])
            notes.save()
        messages.success(request,f"Notes Added From {request.user.username} Successfully!")
    else:
        form = NotesForm()
    notes = Notes.objects.filter(user=request.user)
    context = {'notes':notes,'form':form}
    return render(request,'dashboard/notes.html',context)

@login_required
def delete_note(request,pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect("notes")

class NotesDetailView(generic.DetailView):
    model = Notes

@login_required
def homework(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            homeworks = Homework(
                user = request.user,
                subject = request.POST['subject'],
                title = request.POST['title'],
                description = request.POST['description'],
                due = request.POST['due'],
                is_finished = finished
            )
            homeworks.save()
            messages.success(request,f'Homework Added From {request.user.username}!!')
    else:
        form = HomeworkForm()
    homework = Homework.objects.filter(user=request.user)
    if len(homework) == 0:
        homework_done = True
    else:
        homework_done = False
    context = {
               'homeworks':homework, 
               'homework_done':homework_done,
               'form':form,
    }
    return render(request,'dashboard/homework.html',context)

@login_required
def update_homework(request,pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished == True
    homework.save()
    return redirect('homework')

@login_required
def delete_homework(request,pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect("homework")

def youtube(request):
    if request.method == "POST":
        form  = DashboardForm(request.POST)
        text = request.POST['text']
        video = VideosSearch(text,limit=10)
        result_list = []
        for i in video.result()['result']:
            result_dict = {
                'input':text,
                'title':i['title'],
                'duration':i['duration'],
                'thumbnail':i['thumbnails'][0]['url'],
                'channel':i['channel']['name'],
                'link':i['link'],
                'views':i['viewCount']['short'],
                'published':i['publishedTime']
            }
            desc = ''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc += j['text']
            result_dict['description'] = desc
            result_list.append(result_dict)
            context={
                'form':form,
                'results':result_list
            }
        return render(request,'dashboard/youtube.html',context)
    else:
        form = DashboardForm()
    context = {'form':form}
    return render(request,"dashboard/youtube.html",context)

@login_required
def liveclass(request):
    if request.method == "POST":
        form = LiveclassForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            liveclasses = Liveclass(
                user = request.user,
                subject = request.POST['subject'],
                title = request.POST['title'],
                description = request.POST['description'],
                due = request.POST['due'],
                is_finished = finished
            )
            liveclasses.save()
            messages.success(request,f'Liveclass Added From {request.user.username}!!')
    else:
        form = LiveclassForm()
    liveclass = Liveclass.objects.filter(user=request.user)
    if len(liveclass) == 0:
        liveclass_done = True
    else:
        liveclass_done = False
    context = {
               'liveclasses':liveclass, 
               'liveclass_done':liveclass_done,
               'form':form,
    }
    return render(request,'dashboard/liveclass.html',context)

@login_required
def update_liveclass(request,pk=None):
    liveclass = Liveclass.objects.get(id=pk)
    if liveclass.is_finished == True:
        liveclass.is_finished = False
    else:
        liveclass.is_finished == True
    liveclass.save()
    return redirect('liveclass')

@login_required
def delete_liveclass(request,pk=None):
    Liveclass.objects.get(id=pk).delete()
    return redirect("liveclass")

@login_required
def books(request):
    if request.method == "POST":
        form  = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q="+text
        r = requests.get(url)
        answer = r.json()
        result_list = []
        for i in range(10):
            result_dict = {
                'title':answer['items'][i]['volumeInfo']['title'],
                'subtitle':answer['items'][i]['volumeInfo'].get('subtitle'),
                'description':answer['items'][i]['volumeInfo'].get('description'),
                'count':answer['items'][i]['volumeInfo'].get('pageCount'),
                'categories':answer['items'][i]['volumeInfo'].get('categories'),
                'rating':answer['items'][i]['volumeInfo'].get('pageRating'),
                'thumbnail':answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
                'preview':answer['items'][i]['volumeInfo'].get('previewLink')
            }
            result_list.append(result_dict)
            context={
                'form':form,
                'results':result_list
            }
        return render(request,'dashboard/books.html',context)
    else:
        form = DashboardForm()
    context = {'form':form}
    return render(request,"dashboard/books.html",context)

@login_required
def dictionary(request):
    if request.method == "POST":
        form  = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/"+text
        r = requests.get(url)
        answer = r.json()
        try:
            phonetics = answer[0]['phonetics'][0]['text']
            audio = answer[0]['phonetics'][0]['audio']
            definition = answer[0]['meanings'][0]['definitions'][0]['definition']
            example = answer[0]['meanings'][0]['definitions'][0]['example']
            synonyms = answer[0]['meanings'][0]['definitions'][0]['synonyms']
            context = {
                'form':form,
                'input':text,
                'phonetics':phonetics,
                'audio':audio,
                'definition':definition,
                'example':example,
                'synonyms':synonyms,
            }
        except:
             context = {
                'form':form,
                'input':'',
            }
        return render(request,'dashboard/dictionary.html',context)
    else:
        form = DashboardForm()
        context = {'form':form}
    return render(request,'dashboard/dictionary.html',context)

@login_required
def wiki(request):
    if request.method =='POST':
        text = request.POST['text']
        form = DashboardForm(request.POST)
        search = wikipedia.page(text)
        context = {
             'form':form,
             'title':search.title,
             'link':search.url,
             'details':search.summary
        }
        return render(request,'dashboard/wiki.html',context)
    else:
        form = DashboardForm()
        context = {
            'form':form
        }
    return render(request,"dashboard/wiki.html",context)

@login_required
def conversion(request):
    return render(request,'dashboard/conversion.html')


def register(request):
    return render(request,'dashboard/register.html')

@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished=False,user = request.user)
    liveclasses = Liveclass.objects.filter(is_finished=False,user = request.user)
    if len(homeworks) == 0:
        homework_done = True
    else:
        homework_done = False

    if len(liveclasses) == 0:
        liveclass_done = True
    else:
        liveclass_done = False
    context = {
        'homeworks' : homeworks,
        'liveclasses' : liveclasses,
        'homework_done' : homework_done,
        'liveclass_done' : liveclass_done,
    }
    return render(request,'dashboard/profile.html',context)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f"Account Created For {username} !!")
            # reditect To The Login
    else:
        form = UserRegistrationForm()
    context = {
        'form':form
    }
    return render(request,"dashboard/register.html",context)

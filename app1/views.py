import io
import re
import time
from urllib.parse import urlencode
from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from app1.models import MyUser,Avatar
import json
from django.shortcuts import render ,HttpResponse, redirect
from gtts import gTTS
import os
import speech_recognition as sr
from django.conf import settings
from django.http import FileResponse
import json
from django.shortcuts import render
import requests
import random
from django.contrib import messages


def home(request):
    with open('para.json', 'r') as f:
        data = json.load(f)
    val = data['para'][0]['val']
    if request.method == "POST":
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Speak now...")
            audio = r.listen(source)
            try:
                text = r.recognize_google(audio)
                print("You said:", text)
                tts = gTTS(text)
                file_path = os.path.join(settings.MEDIA_ROOT, "output.mp3")
                tts.save(file_path)
                # os.system("start output.mp3")
                audio_file_path = file_path

                return render(request, "home.html", {"text": text, "val": val,"audio_file_path": audio_file_path})
            except sr.UnknownValueError:
                print("Speech recognition could not understand audio")
                return render(request, "home.html",{"val": val })
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                return render(request, "home.html",{"val": val })
    else:
        return render(request, "home.html",{"val": val })

# Create your views here.
def first(request):
    if request.method == 'POST':
        return redirect('login')


    return render(request, "first.html")

def login(request):
    if request.method == 'POST':
        mobile_number = request.POST['mobile_number']
        request.session['mobile_number'] = mobile_number

        # Validate the mobile number using regex
        if not re.match(r'^[1-9][0-9]{9}$', mobile_number):
            messages.error(request, 'Invalid mobile number. Please enter a valid number.')
            return redirect('login')
        # Check if the mobile number already exists in the database
        if MyUser.objects.filter(mobile_number=mobile_number).exists():
            # If the number already exists, show an error message
            messages.error(request, 'This mobile number is already registered. Please try again with a different number.')
            return redirect('login')
        
        username = f'user_{mobile_number}' # Set a default username
        new_user = MyUser.objects.create_user(username=username, mobile_number=mobile_number)
        new_user.save()
        return redirect('choose_avatar')
    else:
        return render(request, 'second.html')



def choose_avatar(request):
    if request.method == 'POST':
        child_name = request.POST['child_name']
        selected_image = request.POST['selected_image']
        avatar = Avatar(child_name=child_name, avatar_image=selected_image)
        avatar.save()
        request.session['child_name'] = child_name
        request.session['avatar_url'] = selected_image
        mobile_number = request.session.get('mobile_number')

        data={}
        data["name"]=child_name
        data["profile_pic"]= selected_image
        data["platform"]= 'web'
        data["phone_number"]= mobile_number
        
        print(data)
        url = 'https://parakh.pradigi.org/v1/createprofile/'
        files = []
        payload = {'data': json.dumps(data)}
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        print('***', response.text)

        return redirect('select_profile')

    return render(request, 'third.html')

def select_profile(request):
    if request.method == 'POST':
        return redirect('language')

    child_name = request.session.get('child_name')
    avatar_image = request.session.get('avatar_url')
    return render(request, 'four.html', {'child_name': child_name, 'avatar_url': avatar_image})

def language(request):
    child_name = request.session.get('child_name')
    avatar_image = request.session.get('avatar_url')
    return render(request, 'five.html',{'child_name': child_name, 'avatar_url': avatar_image})

def start_assesment(request):
    return render(request, 'six.html')

def paragraph(request):
    if request.method == 'POST':
        return redirect('start_recording')
    return render(request, 'seven.html')


def get_random_paragraph(request):
    with open('ParakhData_English.json', 'r') as f:
        data = json.load(f)
        data1 = random.choice(data['Paragraph'])
        print("the value ",data1['id'])
        data_id = data1['id']
        request.session['data_id'] = data_id
        print(data_id)
        print("dta",data1['data'])
        return (data1['data'])



def start_recording(request):
    if request.method == "POST":
        if "record" in request.POST:
            quest_val = request.POST.get('question')   
            print("question is ", quest_val)
            r = sr.Recognizer()
            should_continue = True
            while should_continue:
                with sr.Microphone() as source:
                    print("Speak now...")
                    audio = r.listen(source)
                    try:
                        data_id = request.session.get('data_id')
                        print(data_id)
                        file_name = data_id +'.wav'
                        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
                        with open(file_path, "wb") as f:
                            f.write(audio.get_wav_data())
                        print("Audio file saved at", file_path)
                        request.session['file_path'] = file_path
                        request.session['file_name'] = file_name
                        print("**", file_name)

                        # set session variable to indicate audio has been recorded
                        request.session['audio_recorded'] = True
                        with open('ParakhData_English.json') as f:
                            data = json.load(f)
                            paragraph = None
                            for d in data['Paragraph']:
                                if d['id'] == data_id:
                                    val = d['data']
                                    break

                        if val:
                            print(val)  
                          
                        return render(request, "eight_one.html", {"recording": True,"val":val,"msg":"Successfully Recorded" })
                    except sr.UnknownValueError:
                        print("Speech recognition could not understand audio")
                        error_msg = "Could not understand audio. Please try again."
                        return render(request, "eight_one.html", {"recording": True,"val":val,"msg":error_msg })
                        
                        
                        # continue recording if speech is not recognized
                    except sr.RequestError as e:
                        print(f"Could not request results from Google Speech Recognition service; {e}")
                  
                        # continue recording if there is an error with the speech recognition service
        elif "skip" in request.POST:
        # stop the recording if it's currently in progress
            if request.session.get('audio_recorded'):
                request.session['audio_recorded'] = False
        elif "submit" in request.POST:
            if request.session.get('audio_recorded'):
                request.session['audio_recorded'] = False
                r = sr.Recognizer()
                r.pause_threshold = 0.5
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source)
                    print("Recording stopped.")
            should_continue = False 
            quest_val = request.POST.get('question')
            print("the question is ",quest_val)
            file_path = request.session.get('file_path')
            print("file_path", file_path)
            # check if audio has been recorded before submitting
            
            file_name = os.path.basename(file_path)
            print("file_name", file_name)
            url = 'http://3.7.133.80:8000/gettranscript/'
            files = [('audio', (file_name, open(file_path, 'rb'), 'audio/wav'))]
            payload = {'language': 'English','question':quest_val}
            headers = {}
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            print('***', response.text)

            if response.status_code == 200:
                data_string = response.json().get('text')
                mistake = response.json().get('no_mistakes')
                fluency = response.json().get('wcpm')               
                return redirect(reverse('answer') + f'?transcript={data_string}&text={data_string}&audio_url={file_path}&no_mistakes={mistake}&wcpm={fluency}')
      
    return render(request, "eight.html", {"val": get_random_paragraph(request),"recording": True})



def answer(request):
    file_name = request.session.get('file_name')
    print("%",file_name)
    name, extension = os.path.splitext(file_name)
    print(name) 
    transcript = request.GET.get('transcript')
    text = request.GET.get('text')
    nomistake = request.GET.get('no_mistakes')
 

    print(nomistake)
    nomistake_list = []

    # Append the value of nomistake to the list
    if nomistake:
        nomistake_list.append(int(nomistake))
    
    print("nomistakelist",nomistake_list)
    nomistake_list = request.POST.get('nomistake_list')   


    wcpm = request.GET.get('wcpm')
    # Format wcpm to have only two decimal places
    wcpm_formatted = '{:.2f}'.format(float(wcpm)) if wcpm else None
    file_path = request.session.get('file_path')
    audio_url = None
    if file_path:
        # Check if the file exists
        if os.path.exists(file_path):
            # Get the file name from the file path
            file_name = os.path.basename(file_path)
            audio_url = request.build_absolute_uri(settings.MEDIA_URL + file_name)
        else:
            file_path = None  


    return render(request, 'nine.html', {'transcript': transcript, 'text': text, 'audio_url': audio_url, 'mis': nomistake, 'flu': wcpm_formatted})

def next_page(request):
    if request.method == 'POST':
        fluency = request.POST.get('fluency')
        nomistake_list = []
        nomistake_list.append(int(fluency))
        nomistake = nomistake_list[0]
        return HttpResponse(str(nomistake))


        

    # request.session['audio_recorded'] = True
    # nomistake_list = request.session.get('nomistake_list')
    # nomistake = request.GET.get('no_mistakes')
    # print("$$$$",nomistake_list)
    # if request.method == "POST":
    #     if 'next' in request.POST:
    #         nomistake = request.GET.get('no_mistakes')
    #         print("####",nomistake)
    #         nomistake_list = []

    #         # Append the value of nomistake to the list
    #         if nomistake:
    #             nomistake_list.append(int(nomistake))
    #         if nomistake is not None and int(nomistake) <= 3:
    #             return redirect('story')
    #         else:
    #             return redirect('word')
        
def next_para(request):
    data_id = request.session.get('data_id')

    request.session['audio_recorded'] = True
    with open('ParakhData_English.json') as f:
        data = json.load(f)
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break

    if val:
        print("the val",val)
    return render(request, "eight_two.html", {"recording": True,"val":val })
   



def story(request):
    if request.method == 'POST':
        return redirect('story_recording')
    return render(request, 'ten.html')


# def get_random_story():
#     with open('ParakhData_English.json', 'r') as f:
#         data = json.load(f)
#     return random.choice(data['Story'])['data']



def get_random_story(request):
    with open('ParakhData_English.json', 'r') as f:
        data = json.load(f)
        data1 = random.choice(data['Story'])
        print("the value ",data1['id'])
        data_id = data1['id']
        request.session['data_id'] = data_id
        print(data_id)
        return (data1['data'])



def story_recording(request):
    if request.method == "POST":
        if "record" in request.POST:
            quest_val = request.POST.get('question')   
            print("question is ", quest_val)
            r = sr.Recognizer()
            r.energy_threshold= 50
            should_continue = True
            recording_timeout = time.time() + 120  # set recording timeout to 120 seconds from now
            while should_continue and time.time() < recording_timeout:
            # while should_continue:
                with sr.Microphone() as source:
                    print("Speak now...")
                    audio = r.listen(source)
                    try:
                        data_id = request.session.get('data_id')
                        print(data_id)
                        file_name = data_id +'.wav'
                        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
                        with open(file_path, "wb") as f:
                            f.write(audio.get_wav_data())
                        print("Audio file saved at", file_path)
                        request.session['file_path'] = file_path
                        request.session['file_name'] = file_name
                        print("**", file_name)

                        # set session variable to indicate audio has been recorded
                        request.session['audio_recorded'] = True
                        with open('ParakhData_English.json') as f:
                            data = json.load(f)
                            Story = None
                            for d in data['Story']:
                                if d['id'] == data_id:
                                    val = d['data']
                                    break

                        if val:
                            print(val)
                        # if request.session.get('audio_recorded'):
                        #     request.session['audio_recorded'] = False
                        # quest_val = request.POST.get('question')
                        # print("the question is ",quest_val)
                        # file_path = request.session.get('file_path')
                        # print("file_path", file_path)
                        # # check if audio has been recorded before submitting
                        
                        # file_name = os.path.basename(file_path)
                        # print("file_name", file_name)
                        # url = 'http://3.7.133.80:8000/gettranscript/'
                        # files = [('audio', (file_name, open(file_path, 'rb'), 'audio/wav'))]
                        # payload = {'language': 'English','question':quest_val}
                        # headers = {}
                        # response = requests.request("POST", url, headers=headers, data=payload, files=files)
                        # print('***', response.text)

                        # if response.status_code == 200:
                        #     data_string = response.json().get('text')
                        #     mistake = response.json().get('no_mistakes')
                        #     fluency = response.json().get('wcpm')               
                        #     return redirect(reverse('story_answer') + f'?transcript={data_string}&text={data_string}&audio_url={file_path}&no_mistakes={mistake}&wcpm={fluency}')
                        return render(request, "eleven_one.html", {"recording": True,"val":val,"msg":"Successfully Recorded" })
                    except sr.UnknownValueError:
                        print("Speech recognition could not understand audio")
                        error_msg = "Could not understand audio. Please try again."
                        # continue recording if speech is not recognized
                    except sr.RequestError as e:
                        print(f"Could not request results from Google Speech Recognition service; {e}")
                        # continue recording if there is an error with the speech recognition service
        elif "skip" in request.POST:
        # stop the recording if it's currently in progress
            if request.session.get('audio_recorded'):
                request.session['audio_recorded'] = False

        elif "close" in request.POST:
            return redirect('story_answer')
        elif "submit" in request.POST:
            if request.session.get('audio_recorded'):
                request.session['audio_recorded'] = False
            quest_val = request.POST.get('question')
            print("the question is ",quest_val)
            file_path = request.session.get('file_path')
            print("file_path", file_path)
            # check if audio has been recorded before submitting
            
            file_name = os.path.basename(file_path)
            print("file_name", file_name)
            url = 'http://3.7.133.80:8000/gettranscript/'
            files = [('audio', (file_name, open(file_path, 'rb'), 'audio/wav'))]
            payload = {'language': 'English','question':quest_val}
            headers = {}
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            print('***', response.text)

            if response.status_code == 200:
                data_string = response.json().get('text')
                mistake = response.json().get('no_mistakes')
                fluency = response.json().get('wcpm')               
                return redirect(reverse('story_answer') + f'?transcript={data_string}&text={data_string}&audio_url={file_path}&no_mistakes={mistake}&wcpm={fluency}')
      
    return render(request, "eleven.html", {"val": get_random_story(request),"recording": True})


def story_answer(request):
    file_name = request.session.get('file_name')
    print("%",file_name)
    name, extension = os.path.splitext(file_name)
    print(name) 
    transcript = request.GET.get('transcript')
    text = request.GET.get('text')
    nomistake = request.GET.get('no_mistakes')
    print(nomistake)
    wcpm = request.GET.get('wcpm')
    # Format wcpm to have only two decimal places
    wcpm_formatted = '{:.2f}'.format(float(wcpm)) if wcpm else None
    file_path = request.session.get('file_path')
    audio_url = None
    if file_path:
        # Check if the file exists
        if os.path.exists(file_path):
            # Get the file name from the file path
            file_name = os.path.basename(file_path)
            audio_url = request.build_absolute_uri(settings.MEDIA_URL + file_name)
        else:
            file_path = None  
    if 'next' in request.POST:
        return redirect('word')
  
    return render(request, 'twelve.html', {'transcript': transcript, 'text': text, 'audio_url': audio_url, 'mis': nomistake, 'flu': wcpm_formatted})
    
def next_story(request):
    data_id = request.session.get('data_id')

    request.session['audio_recorded'] = True
    with open('ParakhData_English.json') as f:
        data = json.load(f)
        Story = None
        for d in data['Story']:
            if d['id'] == data_id:
                val = d['data']
                break
    if val:
        print("the val",val)

    return render(request, "eleven_two.html", {"recording": True,"val":val })
   

def thirteen(request):
    return render(request, 'thirteen.html')
def fourteen(request):
    return render(request, 'fourteen.html')
def word(request):
    if request.method == 'POST':
        audio_file = request.session.setdefault('audio_file', [])
        print(audio_file)
        file = request.session.setdefault('file', [])
        audio_file.clear()  # clear the audio_file list
        print(audio_file)
        file.clear()
        return redirect('word_recording')
    return render(request, 'fifteen.html')

def get_random_word(request):
    audio_file = request.session.setdefault('audio_file', [])

    with open('ParakhData_English.json', 'r') as f:
        data = json.load(f)
        data1 = random.choice(data['Word'])
        print("the value ",data1['id'])
        data_id = data1['id']
        request.session['data_id'] = data_id

        print(data_id)
       
 
        return (data1['data'])





def word_recording(request):
    if request.method == "POST":
        audio_file = request.session.setdefault('audio_file', [])
        responses = request.session.setdefault('responses', [])
        audio_file_name = request.session.setdefault('audio_file_name', [])
        copy_file = request.session.setdefault('copy_file', [])


        if len(responses)==5:
            responses.clear()
        print("check audio",audio_file)
        if "record" in request.POST:
            quest_val = request.POST.get('question')   
            print("question is ", quest_val)
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print("Speak now...")
                audio = r.listen(source)
                # if len(copy_file)==5:
                #     print("question is ", quest_val)
                #     with open('ParakhData_English.json') as f:
                #         data = json.load(f)
                #         Word = None
                #         for d in data['Word']:
                            
                #             if d['data'] == quest_val:
                #                 print("the",quest_val)
                #                 val = d['id']
                #                 print('@@@@@@@@@@@',val)
                #                 break

                #     # dataid[0] = request.session.get('dataid[0]')
                #     # print(dataid[0])

                #     return redirect('word_answer')
                    # file_name = val + '.wav' # Modified this line to use val instead of data_id
                    # file_path = os.path.join(settings.MEDIA_ROOT, file_name)
                    # with open(file_path, "wb") as f:
                    #     f.write(audio.get_wav_data())
                    # for i, path in enumerate(copy_file):
                    #     if path == file_path:
                    #         copy_file[i] = file_path
                    # print(copy_file)
                    # print(file_path)
                try:
                    data_id = request.session.get('data_id')
                    file_name = data_id +'.wav'
                    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
                    with open(file_path, "wb") as f:
                        f.write(audio.get_wav_data())
                    audio_file_name.append(file_name)
                    audio_file.append(file_path)
                    request.session['file_path'] = file_path
                    if len(audio_file) < 5:
                        request.session['audio_recorded'] = True
                        with open('ParakhData_English.json') as f:
                            data = json.load(f)
                            Word = None
                            for d in data['Word']:
                                if d['id'] == data_id:
                                    val = d['data']
                                    break
                         
                        # msg = f"Recording {len(audio_file) + 1} of 5. Please speak the next letter."
                        return render(request, "fifteen_one_one.html", {"recording": True,"val":val})
                    elif len(audio_file) == 5:
                        msg = "You have recorded 5 files. Please click the Submit button to proceed."
                        request.session['audio_recorded'] = True
                        with open('ParakhData_English.json') as f:
                            data = json.load(f)
                            Word = None
                            for d in data['Word']:
                                if d['id'] == data_id:
                                    val = d['data']
                                    break
                         
                        return render(request, "fifteen_one_one_submit.html", {"val":val})
        
                except sr.UnknownValueError:
                    print("Speech recognition could not understand audio")
                    error_msg = "Could not understand audio. Please try again."
                    return render(request, "fifteen_one.html", {"val": get_random_word(request), "error": error_msg})
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")
                    return render(request, "fifteen_one.html", {"val": get_random_word(request)}) 
        elif "stop" in request.POST:
            audio_file = request.session.setdefault('audio_file', [])
            dataid = request.session.setdefault('dataid', [])
            dataid.clear()

            responses = request.session.setdefault('responses', [])
            audio_file_name = request.session.setdefault('audio_file_name', [])

            audio_file_name.clear()

            responses.clear()
            print(audio_file)
            file = request.session.setdefault('file', [])
            audio_file.clear()  # clear the audio_file list
            print("res",responses)
            file.clear()  # clear the file list
            return render(request, "fifteen_one.html", {"msg": "", "val": get_random_word(request)})
        
      ##  only delet the last one
            # audio_file = request.session.setdefault('audio_file', [])
            # dataid = request.session.setdefault('dataid', [])

            # print(audio_file)
            # file = request.session.setdefault('file', [])
            # if len(audio_file) > 0:
            #     audio_file.pop()  # remove the last element from audio_file list
            # print(audio_file)
            # return render(request, "fifteen_one.html", {"msg": "", "val": get_random_word(request)})

        elif "submit" in request.POST:
            audio_file = request.session['audio_file']
            quest_val = request.POST.get('question')
            file_path = request.session.get('file_path')
            if file_path is None:
                return redirect('fifteen_one')
            # responses = []
            nomistake=[]
            wcpm=[]
            # for audio_file in audio_file:
            # file_path = os.path.join(settings.MEDIA_ROOT, audio_file)
            file_name = os.path.basename(file_path)
            url = 'http://3.7.133.80:8000/gettranscript/'
            files = [('audio', (file_name, open(file_path, 'rb'), 'audio/wav'))]
            payload = {'language': 'English', 'question': quest_val}
            headers = {}
            response = requests.request("POST", url, headers=headers, data=payload, files=files)

            if response.status_code == 200:
                responses.append(response.text)

                if len(responses)==5:
                    request.session['responses'] = responses
                    context = {'responses': responses}
                    url = reverse('word_answer')
                    if len(responses)==5:
                        
                        return redirect(url,context)
   
    return render(request, "fifteen_one.html", {"val": get_random_word(request), "recording": True})
def word_answer(request):
    audio_file = request.session.setdefault('audio_file', [])
    copy_file = request.session.setdefault('copy_file', [])
    audio_file_name = request.session.setdefault('audio_file_name', [])
    copy_file_name = request.session.setdefault('copy_file_name', [])


    if len(audio_file)==5:
        copy_file= audio_file.copy()
    if len(audio_file_name)==5:
        copy_file_name = audio_file_name.copy()

    print("$$$",copy_file_name)
    request.session['copy_file_name'] = copy_file_name

    # file_path = request.session.get('file_path')

    transcript = request.GET.get('transcript')
    text = request.GET.get('text')
    nomistake = request.GET.get('no_mistakes')
    wcpm = request.GET.get('wcpm')
    # audio_file = request.session['audio_file']
    
    audio_urls = []
    if copy_file:
        for file_path in copy_file:
            if os.path.exists(file_path):
                file_name = os.path.basename(file_path)
                audio_url = request.build_absolute_uri(settings.MEDIA_URL + file_name)
                audio_urls.append(audio_url)
       
                # copy_file.remove(file_path)
        request.session['copy_file'] = copy_file
    
    text = []
    mis=[]
    wcpm=[]
    responses = request.session.get('responses', [])

    for item in responses:
        text.append(eval(item)['text'])
        mis.append(eval(item)['no_mistakes'])
        wcpm.append(eval(item)['wcpm'])
    total_wcpm = sum(wcpm) 
    total_mis = sum(mis)
    print("total",total_wcpm)
    
    context = { 'transcript': transcript,'text': text, 'copy_file': copy_file, 'audio_urls': audio_urls ,'mis':mis ,'flu':wcpm,'total_wcpm': total_wcpm,'total_mis':total_mis}
    if len(audio_file)==5:
        audio_file.clear()
    if len(audio_file_name)==5:
        audio_file_name.clear()
        print("audio",copy_file_name)
    return render(request, 'word_answer.html', context)



def next_word(request):

    dataid = request.session.setdefault('dataid', [])
    copy_file_name = request.session.setdefault('copy_file_name', [])


    if request.method == "POST":
        copy_file_name = request.session.get('copy_file_name')

        copy_file_name = request.session.setdefault('copy_file_name', [])
        for file_name in copy_file_name:
            file_name_without_extension = file_name.split(".")[0]
            dataid.append(file_name_without_extension)
        print("^^^",dataid)
        if "record" in request.POST:
            print("dataid0",dataid[0])
            request.session['dataid[0]'] = dataid[0]

            request.session['audio_recorded'] = True
            with open('ParakhData_English.json') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == dataid[0]:
                        val = d['data']
                        break
                if val:
                    print("the val",val)
                

                return render(request, "fifteen_one.html", {"recording": True,"val":val })

        if "record2" in request.POST:
            print("dataid0",dataid[1])
            request.session['audio_recorded'] = True
            with open('ParakhData_English.json') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == dataid[1]:
                        val = d['data']
                        break
                if val:
                    print("the val",val)

                return render(request, "fifteen_one.html", {"recording": True,"val":val })

        if "record3" in request.POST:
            print("dataid0",dataid[2])
            request.session['audio_recorded'] = True
            with open('ParakhData_English.json') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == dataid[2]:
                        val = d['data']
                        break
                if val:
                    print("the val",val)

                return render(request, "fifteen_one.html", {"recording": True,"val":val })

        if "record4" in request.POST:
            print("dataid0",dataid[3])
            request.session['audio_recorded'] = True
            with open('ParakhData_English.json') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == dataid[3]:
                        val = d['data']
                        break
                if val:
                    print("the val",val)

                return render(request, "fifteen_one.html", {"recording": True,"val":val })
        
        if "record5" in request.POST:
            print("dataid0",dataid[4])
            request.session['audio_recorded'] = True
            with open('ParakhData_English.json') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == dataid[4]:
                        val = d['data']
                        break
                if val:
                    print("the val",val)

                return render(request, "fifteen_one.html", {"recording": True,"val":val })
        

    return redirect('word_answer')



def letter(request):
    if request.method == 'POST':
        return redirect('letter_recording')
    return render(request, 'sixteen.html')


def get_random_letter(request):
    with open('ParakhData_English.json', 'r') as f:
        data = json.load(f)
        data1 = random.choice(data['Letter'])
        print("the value ",data1['id'])
        data_id = data1['id']
        request.session['data_id'] = data_id
       
 
        return (data1['data'])





def letter_recording(request):
    if request.method == "POST":
        audio_file = request.session.setdefault('audio_file', [])
        responses = request.session.setdefault('responses', [])
        audio_file_name = request.session.setdefault('audio_file_name', [])
        if len(responses)==5:
            responses.clear()
        print("check audio",audio_file)
        if "record" in request.POST:
            quest_val = request.POST.get('question')   
            print("question is ", quest_val)
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print("Speak now...")
                audio = r.listen(source)
                try:
                    data_id = request.session.get('data_id')
                    file_name = data_id +'.wav'
                    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
                    with open(file_path, "wb") as f:
                        f.write(audio.get_wav_data())
                    audio_file_name.append(file_name)
                    audio_file.append(file_path)
                    request.session['file_path'] = file_path
                    if len(audio_file) < 5:
                        request.session['audio_recorded'] = True
                        with open('ParakhData_English.json') as f:
                            data = json.load(f)
                            Letter = None
                            for d in data['Letter']:
                                if d['id'] == data_id:
                                    val = d['data']
                                    break
                         
                        # msg = f"Recording {len(audio_file) + 1} of 5. Please speak the next letter."
                        return render(request, "fifteen_two_one.html", {"recording": True,"val":val})
                    elif len(audio_file) == 5:
                        msg = "You have recorded 5 files. Please click the Submit button to proceed."
                        request.session['audio_recorded'] = True
                        with open('ParakhData_English.json') as f:
                            data = json.load(f)
                            Letter = None
                            for d in data['Letter']:
                                if d['id'] == data_id:
                                    val = d['data']
                                    break
                         
                        return render(request, "fifteen_two_one.html", {"val":val})
        
                except sr.UnknownValueError:
                    print("Speech recognition could not understand audio")
                    error_msg = "Could not understand audio. Please try again."
                    return render(request, "fifteen_two.html", {"val": get_random_letter(request), "error": error_msg})
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")
                    return render(request, "fifteen_two.html", {"val": get_random_letter(request)}) 
        elif "stop" in request.POST:
            audio_file = request.session.setdefault('audio_file', [])
            dataid = request.session.setdefault('dataid', [])
            dataid.clear()

            responses = request.session.setdefault('responses', [])
            audio_file_name = request.session.setdefault('audio_file_name', [])

            audio_file_name.clear()

            responses.clear()
            print(audio_file)
            file = request.session.setdefault('file', [])
            audio_file.clear()  # clear the audio_file list
            print("res",responses)
            file.clear()  # clear the file list
            return render(request, "fifteen_two.html", {"msg": "", "val": get_random_letter(request)})
        
      ##  only delet the last one
            # audio_file = request.session.setdefault('audio_file', [])
            # dataid = request.session.setdefault('dataid', [])

            # print(audio_file)
            # file = request.session.setdefault('file', [])
            # if len(audio_file) > 0:
            #     audio_file.pop()  # remove the last element from audio_file list
            # print(audio_file)
            # return render(request, "fifteen_one.html", {"msg": "", "val": get_random_letter(request)})

        elif "submit" in request.POST:
            audio_file = request.session['audio_file']
            quest_val = request.POST.get('question')
            file_path = request.session.get('file_path')
            if file_path is None:
                return redirect('fifteen_one')
            # responses = []
            nomistake=[]
            wcpm=[]
            # for audio_file in audio_file:
            # file_path = os.path.join(settings.MEDIA_ROOT, audio_file)
            file_name = os.path.basename(file_path)
            url = 'http://3.7.133.80:8000/gettranscript/'
            files = [('audio', (file_name, open(file_path, 'rb'), 'audio/wav'))]
            payload = {'language': 'English', 'question': quest_val}
            headers = {}
            response = requests.request("POST", url, headers=headers, data=payload, files=files)

            if response.status_code == 200:
                responses.append(response.text)

                if len(responses)==5:
                    request.session['responses'] = responses
                    context = {'responses': responses}
                    url = reverse('letter_answer')
                    if len(responses)==5:
                        
                        return redirect(url,context)
   
    return render(request, "fifteen_two.html", {"val": get_random_letter(request), "recording": True})

def letter_answer(request):
    audio_file = request.session.setdefault('audio_file', [])
    copy_file = request.session.setdefault('copy_file', [])
    audio_file_name = request.session.setdefault('audio_file_name', [])
    copy_file_name = request.session.setdefault('copy_file_name', [])


    if len(audio_file)==5:
        copy_file= audio_file.copy()
    if len(audio_file_name)==5:
        copy_file_name = audio_file_name.copy()

    print("$$$",copy_file_name)
    request.session['copy_file_name'] = copy_file_name

    # file_path = request.session.get('file_path')

    transcript = request.GET.get('transcript')
    text = request.GET.get('text')
    nomistake = request.GET.get('no_mistakes')
    wcpm = request.GET.get('wcpm')
    # audio_file = request.session['audio_file']
    
    audio_urls = []
    if copy_file:
        for file_path in copy_file:
            if os.path.exists(file_path):
                file_name = os.path.basename(file_path)
                audio_url = request.build_absolute_uri(settings.MEDIA_URL + file_name)
                audio_urls.append(audio_url)
       
                # copy_file.remove(file_path)
        request.session['copy_file'] = copy_file
    
    text = []
    mis=[]
    wcpm=[]
    responses = request.session.get('responses', [])

    for item in responses:
        text.append(eval(item)['text'])
        mis.append(eval(item)['no_mistakes'])
        wcpm.append(eval(item)['wcpm'])
    total_wcpm = sum(wcpm) 
    total_mis = sum(mis)
    print("total",total_wcpm)
    
    context = { 'transcript': transcript,'text': text, 'copy_file': copy_file, 'audio_urls': audio_urls ,'mis':mis ,'flu':wcpm,'total_wcpm': total_wcpm,'total_mis':total_mis}
    if len(audio_file)==5:
        audio_file.clear()
    if len(audio_file_name)==5:
        audio_file_name.clear()
        print("audio",copy_file_name)
    return render(request, 'letter_answer.html', context)



def next_letter(request):

    dataid = request.session.setdefault('dataid', [])
    copy_file_name = request.session.setdefault('copy_file_name', [])


    if request.method == "POST":
        copy_file_name = request.session.get('copy_file_name')

        copy_file_name = request.session.setdefault('copy_file_name', [])
        print("@@@",copy_file_name)
        for file_name in copy_file_name:
            file_name_without_extension = file_name.split(".")[0]
            dataid.append(file_name_without_extension)
        print(dataid)

    return redirect('letter_answer')

# def letter_recording(request):
#     if request.method == "POST":
#         audio_file = request.session.setdefault('audio_file', [])
#         if "record" in request.POST:
#             quest_val = request.POST.get('question')   
#             print("question is ", quest_val)
#             r = sr.Recognizer()
#             with sr.Microphone() as source:
#                 print("Speak now...")
#                 audio = r.listen(source)
#                 try:
#                     data_id = request.session.get('data_id')
#                     file_name = data_id +'.wav'
#                     file_path = os.path.join(settings.MEDIA_ROOT, file_name)
#                     with open(file_path, "wb") as f:
#                         f.write(audio.get_wav_data())
#                     print("Audio file saved at", file_path)
#                     audio_file.append(file_path)
#                     request.session['file_path'] = file_path
#                     print(audio_file)
#                     if len(audio_file) < 5:
#                         msg = f"Recording {len(audio_file) + 1} of 5. Please speak the next letter."
#                         return render(request, "fifteen_two.html", {"val": get_random_letter(request), "audio_url":{file_name}, "msg": msg})
#                     elif len(audio_file) == 5:
#                         msg = "You have recorded 5 files. Please click the Submit button to proceed."
#                         request.session['audio_recorded'] = True
#                         with open('ParakhData_English.json') as f:
#                             data = json.load(f)
#                             Word = None
#                             for d in data['Letter']:
#                                 if d['id'] == data_id:
#                                     val = d['data']
#                                     break

#                         if val:
#                             print(val)    
#                         return render(request, "fifteen_two_one.html", {"recording": True,"val":val,"msg":msg })
#                         # return render(request, "fifteen_two_one.html", {"val": get_random_letter(request), "audio_url":{file_name}, "msg": msg})
#                     # return render(request, "fifteen_two.html", {"val": get_random_letter(request), "audio_url": file_path, "msg":"Successfully Recorded" })
#                 except sr.UnknownValueError:
#                     print("Speech recognition could not understand audio")
#                     error_msg = "Could not understand audio. Please try again."
#                     return render(request, "fifteen_two.html", {"val": get_random_letter(request), "error": error_msg})
#                 except sr.RequestError as e:
#                     print(f"Could not request results from Google Speech Recognition service; {e}")
#                     return render(request, "fifteen_two.html", {"val": get_random_letter(request)}) 
#         elif "stop" in request.POST:
#             audio_file = request.session.setdefault('audio_file', [])
#             print(audio_file)
#             file = request.session.setdefault('file', [])
#             audio_file.clear()  # clear the audio_file list
#             print(audio_file)
#             file.clear()  # clear the file list
#             return render(request, "fifteen_two.html", {"msg": "", "val": get_random_letter(request)})
#         elif "submit" in request.POST:
#             audio_file = request.session['audio_file']
#             print("%%",audio_file)
#             quest_val = request.POST.get('question')
#             print("teh quuestion is ",quest_val)
#             file_path = request.session.get('file_path')
#             if file_path is None:
#                 return redirect('fifteen_two')
#             print('file_path', file_path)
#             responses = []
#             nomistake=[]
#             wcpm=[]

#             for audio_file in audio_file:
#                 file_path = os.path.join(settings.MEDIA_ROOT, audio_file)
#                 file_name = os.path.basename(file_path)
#                 url = 'http://3.7.133.80:8000/gettranscript/'
#                 files = [('audio', (file_name, open(file_path, 'rb'), 'audio/wav'))]
#                 payload = {'language': 'English', 'question': quest_val}
#                 headers = {}
#                 response = requests.request("POST", url, headers=headers, data=payload, files=files)
#                 print('***', response.text)

#                 if response.status_code == 200:              
#                     responses.append(response.text)

#                     print("##",responses)
#             request.session['responses'] = responses
       
#             context = {'responses': responses}
#             url = reverse('letter_answer')
#             return redirect(url,context)
#     else:
#         return render(request, "fifteen_two.html", {"val": get_random_letter(request), "recording": True})
# def letter_answer(request):
#     audio_file = request.session.setdefault('audio_file', [])
#     file_path = request.session.get('file_path')

#     transcript = request.GET.get('transcript')
#     text = request.GET.get('text')
#     nomistake = request.GET.get('no_mistakes')
#     wcpm = request.GET.get('wcpm')
#     audio_file = request.session['audio_file']
    
#     print("###",audio_file)
#     audio_urls = []
#     if audio_file:
#         for file_path in audio_file:
#             if os.path.exists(file_path):
#                 file_name = os.path.basename(file_path)
#                 audio_url = request.build_absolute_uri(settings.MEDIA_URL + file_name)
#                 audio_urls.append(audio_url)
       
#                 # audio_file.remove(file_path)
#         request.session['audio_file'] = audio_file
#     if 'retake' in request.POST:
#         return redirect('letter_recording')
#     elif 'next' in request.POST:
#         return redirect('paragraph')
#     text = []
#     mis=[]
#     wcpm=[]
#     responses = request.session.get('responses', [])

#     for item in responses:
#         text.append(eval(item)['text'])
#         mis.append(eval(item)['no_mistakes'])
#         wcpm.append(eval(item)['wcpm'])
#     total_wcpm = sum(wcpm) 
#     total_mis = sum(mis)
#     context = { 'transcript': transcript,'text': text, 'audio_file': audio_file, 'audio_urls': audio_urls ,'mis':mis ,'flu':wcpm,'total_wcpm': total_wcpm,'total_mis':total_mis}
#     return render(request, 'letter_answer.html', context)

def seventeen(request):     
    return render(request,'seventeen.html')

def next_answer(request):
    child_name = request.session.get('child_name')

    return render(request,'eighteen.html',{'child_name': child_name})

def next_answer_story(request):
    child_name = request.session.get('child_name')

    return render(request,'answer_word.html',{'child_name': child_name})
    













































































# def next_word(request):
#     data_id = request.session.get('data_id')
#     copy_file_name = request.session.setdefault('copy_file_name', [])
#     print(copy_file_name)
    
#     request.session['audio_recorded'] = True
#     with open('ParakhData_English.json') as f:
#         data = json.load(f)
#         Word = None
#         for d in data['Word']:
#             if d['id'] == data_id:
#                 val = d['data']
#                 break
#     if val:
#         print("the val",val)

#     return render(request, "fifteen_one.html", {"recording": True,"val":val })
























































































############################################   mp3

# def eight(request):
#     if request.method == "POST":
#         if "record" in request.POST:
#             r = sr.Recognizer()
#             with sr.Microphone() as source:
#                 print("Speak now...")
#                 audio = r.listen(source)
#                 try:
#                     text = r.recognize_google(audio)
#                     print("You said:", text)

#                     tts = gTTS(text)
#                     file_path = os.path.join(settings.MEDIA_ROOT, "output.mp3")
#                     tts.save(file_path)
#                     # Add the text variable to the form data
#                     return render(request, "eight.html", {"val": get_random_paragraph(), "text": text})
#                 except sr.UnknownValueError:
#                     print("Speech recognition could not understand audio")
#                     error_msg = "Could not understand audio. Please try again."
#                     return render(request, "eight.html", {"val": get_random_paragraph(), "error": error_msg})
#                 except sr.RequestError as e:
#                     print(f"Could not request results from Google Speech Recognition service; {e}")
#                     return render(request, "eight.html", {"val": get_random_paragraph()})
#         elif "submit" in request.POST:
#             text = request.POST.get("text", "")
#             file_path = os.path.join(settings.MEDIA_ROOT, "output.mp3")
#             print("file_path",file_path)
#             url = "http://3.7.133.80:8000/gettranscript/"
#             files=[
#                 ('audio',('output.mp3',open(file_path,'rb'),'audio/mpeg'))
#                 ]
#             payload = {"language": ""} 
#             # encoded_payload = urllib.parse.urlencode(payload)
#             headers = {}
#             # response = requests.post(url, files=files, data=encoded_payload.encode('utf-8'), headers=headers)
#             response = requests.post(url, files=files, data=payload, headers=headers)
#             print("***", response)

    
#             if response.status_code == 200:
#                 transcript = response.json().get("transcript")
#                 print("***",transcript)
#                 return redirect(reverse('nine') + f'?transcript={transcript}&text={text}')

#             else:
#                 print("Error while sending the file:")
#                 return redirect('nine')
#         return render(request, "eight.html", {"val": get_random_paragraph()})

#     else:
#         return render(request, "eight.html", {"val": get_random_paragraph()})

############################################   wav
# def eight(request):
#     if request.method == "POST":
#         if "record" in request.POST:
#             r = sr.Recognizer()
#             with sr.Microphone() as source:
#                 print("Speak now...")
#                 audio = r.listen(source)
#                 try:
#                     text = r.recognize_google(audio)
#                     print("You said:", text)

#                     tts = gTTS(text)
#                     file_path = os.path.join(settings.MEDIA_ROOT, "output.wav")
#                     tts.save(file_path)
#                     # Add the text variable to the form data
#                     return render(request, "eight.html", {"val": get_random_paragraph(), "text": text})
#                 except sr.UnknownValueError:
#                     print("Speech recognition could not understand audio")
#                     error_msg = "Could not understand audio. Please try again."
#                     return render(request, "eight.html", {"val": get_random_paragraph(), "error": error_msg})
#                 except sr.RequestError as e:
#                     print(f"Could not request results from Google Speech Recognition service; {e}")
#                     return render(request, "eight.html", {"val": get_random_paragraph()})
#         elif "submit" in request.POST:
#             text = request.POST.get("text", "")
#             file_path = os.path.join(settings.MEDIA_ROOT, "output.wav")
#             print("file_path",file_path)
#             url = "http://3.7.133.80:8000/gettranscript/"
#             files=[
#                 ('audio',('output.wav',open(file_path,'rb'),'audio/wav'))
#                 ]
#             payload = {"language": ""} 
#             # encoded_payload = urllib.parse.urlencode(payload)
#             headers = {}
#             # response = requests.post(url, files=files, data=encoded_payload.encode('utf-8'), headers=headers)
#             response = requests.post(url, files=files, data=payload, headers=headers)
#             print("***", response)

    
#             if response.status_code == 200:
#                 transcript = response.json().get("transcript")
#                 print("***",transcript)
#                 return redirect(reverse('nine') + f'?transcript={transcript}&text={text}')

#             else:
#                 print("Error while sending the file:")
#                 return redirect('nine')
#         return render(request, "eight.html", {"val": get_random_paragraph()})

#     else:
#         return render(request, "eight.html", {"val": get_random_paragraph()})

# def nine(request):
#     transcript = request.GET.get('transcript')
#     text = request.GET.get('text')
#     file_path = os.path.join(settings.MEDIA_ROOT, "output.wav")
#     audio_url = request.build_absolute_uri(settings.MEDIA_URL + "output.wav")
#     if 'retake' in request.POST:
#         return redirect('eight')
#     return render(request, 'nine.html', {'transcript': transcript, 'text': text, 'audio_url': audio_url})

# if "record" in request.POST:
#     r = sr.Recognizer()
#     with sr.Microphone() as source:
#         print("Speak now...")
#         audio = r.listen(source)
#         try:
#             data_id = request.session.get('data_id')
#             session_id = request.session.session_key
#             file_name = f"{session_id}_{data_id}.wav"
#             file_path = os.path.join(settings.MEDIA_ROOT, file_name)
#             with open(file_path, "wb") as f:
#                 f.write(audio.get_wav_data())
#             print("Audio file saved at", file_path)
#             audio_files = request.session.get('audio_files', [])
#             audio_files.append(file_name)
#             request.session['audio_files'] = audio_files
#             sessions = request.session.get('sessions', [])
#             sessions.append(session_id)
#             request.session['sessions'] = sessions
#             if len(audio_files) == 5:
#                 msg = "You have recorded 5 stories. Please click the Submit button to proceed."
#                 return render(request, "eleven.html", {"val": get_random_story(request), "audio_url": audio_files, "msg": msg})
#             return render(request, "eleven.html", {"val": get_random_story(request), "audio_url": file_path, "msg":"Successfully Recorded" })
#         except sr.UnknownValueError:
#             print("Speech recognition could not understand audio")
#             error_msg = "Could not understand audio. Please try again."
#             return render(request, "eleven.html", {"val": get_random_story(request), "error": error_msg})
#         except sr.RequestError as e:
#             print(f"Could not request results from Google Speech Recognition service; {e}")
#             return render(request, "eleven.html", {"val": get_random_story(request)})

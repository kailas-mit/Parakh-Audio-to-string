import re
from urllib.parse import urlencode
from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from app1.models import MyUser,Avatar
from django.shortcuts import render ,HttpResponse, redirect
import os
from django.conf import settings
from django.http import FileResponse
import json
from django.shortcuts import render
import requests
import random
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import time as t



json_l1 = os.path.join(settings.STATICFILES_DIRS[0], 'json/ParakhData_English_L1.json')
json_l2 = os.path.join(settings.STATICFILES_DIRS[0], 'json/ParakhData_English_L2.json')
json_l3 = os.path.join(settings.STATICFILES_DIRS[0], 'json/ParakhData_English_L3.json')
json_l4 = os.path.join(settings.STATICFILES_DIRS[0], 'json/ParakhData_English_L4.json')
json_ass = os.path.join(settings.STATICFILES_DIRS[0], 'json/ParakhData_Assamese.json')
json_ben = os.path.join(settings.STATICFILES_DIRS[0], 'json/ParakhData_Bengali.json')
json_eng = os.path.join(settings.STATICFILES_DIRS[0], 'json/ParakhData_English.json')
json_guj = os.path.join(settings.STATICFILES_DIRS[0], 'json/ParakhData_Gujarati.json')
json_hin = os.path.join(settings.STATICFILES_DIRS[0], 'json/ParakhData_Hindi.json')
json_kan = os.path.join(settings.STATICFILES_DIRS[0], 'json/ParakhData_kannada.json')
json_mal = os.path.join(settings.STATICFILES_DIRS[0], 'json/ParakhData_malayalam.json')
json_mar = os.path.join(settings.STATICFILES_DIRS[0], 'json/ParakhData_marathi.json')
json_odi = os.path.join(settings.STATICFILES_DIRS[0], 'json/ParakhData_odiya.json')
json_pun = os.path.join(settings.STATICFILES_DIRS[0], 'json/ParakhData_Punjabi.json')
json_tami = os.path.join(settings.STATICFILES_DIRS[0], 'json/ParakhData_Tamil.json')
json_tel = os.path.join(settings.STATICFILES_DIRS[0], 'json/ParakhData_telugu.json')
json_urdu = os.path.join(settings.STATICFILES_DIRS[0], 'json/ParakhData_urdu.json')


base_path = os.path.join(settings.MEDIA_ROOT, "")

from .models import Program

def first(request):
    options = Program.OPTION_CHOICES
    if request.method == 'POST':
        selected_option = request.POST.get('option')
        print("selected_option",selected_option)
        if selected_option == 'General Program':
            return redirect('login')
        elif selected_option == 'AOP Program':
            return redirect('aop_language')
    return render(request, 'home.html',{'options': options})

from .models import Aop_lan
from .models import Aop_sub_lan

def aop_language(request):
    options = Aop_sub_lan.OPTION_CHOICES
    eng_option= Aop_lan.OPTION_CHOICES
    if request.method == 'POST':
        selected_level = request.POST.get('options')
        print("selected_level",selected_level)
    return render(request, 'AOP_PRO/language.html',{'options': options, 'eng_option': eng_option})

def aop_num(request,selected_option):
    print("start_assesment",selected_option)
    request.session['selected_option'] = selected_option
    return render(request, 'AOP_PRO/search_num.html')

def red_start(request):
    selected_option = request.session.get('selected_option')
    print("selected_option",selected_option)
    if request.method == 'GET':
        enrollment_id = request.GET.get('enrollment_id')
        print(enrollment_id)
        phone_number = request.session.get('phone_number')
        print("ph",phone_number)
        name = request.session.get('name')
        print("name",name)
        data={}
        data["name"]=name
        data["profile_pic"]= ""
        data["platform"]= 'web'
        data["phone_number"]= phone_number
        data["enrollment_id"]= enrollment_id
        print(data)
        url = 'https://parakh.pradigi.org/v1/createprofile/'
        files = []
        payload = {'data': json.dumps(data)}
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        response_data = json.loads(response.text)
        id_value = response_data["data"][0]["id"]
        request.session['id_value'] = id_value
        print("ID value:", id_value)
        request.session['enrollment_id'] = enrollment_id
        context = {
            'processed_data': 'some processed data'
        }
        url = reverse('start_assesment', args=[selected_option])
        return redirect(url)

    if "search" in request.POST:
        selected_option = request.session.get('selected_option')
        mobile_number = request.POST['mobile_number']
        request.session['phone_number'] = mobile_number
        url = f'https://prajeevika.org/apis/aop/children-details.php?phone_number={mobile_number}&token=eyNsWgAdBF0KafwGPwOC9h5rWABTBuAKYxDxv8zRgJyuP'
        response = requests.get(url)
        print("####",response)
        print("resposne",response.text )
        try:
            data = response.json()
            name = data[0]['name']
            request.session['name'] = name
            status = data[0]['status']
            request.session['status'] = status
            context = {
                'data': data,
                'selected_option': selected_option,
            }
            return render(request, 'AOP_PRO/search_num.html', context)
        except IndexError:
            context = {'error_message': 'Mobile number not found'}
            return render(request, 'AOP_PRO/search_num.html', context)
    return render(request, 'AOP_PRO/search_num.html')
    

def msg_api(request):
    if "search" in request.POST:
        now = datetime.now()
        today_date = now.strftime("%Y-%m-%d")
        selected_option = request.session.get('selected_option')
        enrollment_id = request.session.get('enrollment_id')
        id_value = request.session.get('id_value')
        url = f'https://prajeevika.org/apis/aop/update-result.php?token=eyNsWgAdBF0KafwGPwOC9h5rWABTBuAKYxDxv8zRgJyuP&enrollment_id={enrollment_id}&student_id={id_value}&assessment_type={selected_option}&assessment_date={today_date}&assessment_level=L1'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
        mobile_number = request.POST['mobile_number']
        request.session['phone_number'] = mobile_number

        url = f'https://prajeevika.org/apis/aop/children-details.php?phone_number={mobile_number}&token=eyNsWgAdBF0KafwGPwOC9h5rWABTBuAKYxDxv8zRgJyuP'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            name = data[0]['name']
            request.session['name'] = name
            status = data[0]['status']  
            request.session['status'] = status
            context = {
                'data': data,
                'selected_option': selected_option,
            }
            return render(request, 'AOP_PRO/search_num.html', context)

def login(request):
    if request.method == 'POST':
        mobile_number = request.POST['mobile_number']
        request.session['mobile_number'] = mobile_number
        if not re.match(r'^[1-9][0-9]{9}$', mobile_number):
            messages.error(request, 'Invalid mobile number. Please enter a valid number.')
            return redirect('login')
        if MyUser.objects.filter(mobile_number=mobile_number).exists():
            return redirect('choose_avatar')
        username = f'user_{mobile_number}' # Set a default username
        new_user = MyUser.objects.create_user(username=username, mobile_number=mobile_number)
        new_user.save()
        return redirect('choose_avatar')
    else:
        return render(request, 'login.html')


def choose_avatar(request):
    if request.method == 'POST':
        child_name = request.POST.get('child_name')
        if not child_name:
            messages.error(request, 'Please enter the child name.')
            return redirect('choose_avatar')
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
        url = 'https://parakh.pradigi.org/v1/createprofile/'
        files = []
        payload = {'data': json.dumps(data)}
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        return redirect('select_profile')

    return render(request, 'chooseavtar.html')

from .models import MyModel
from .models import Aop_sub_lan

def select_profile(request):
    if request.method == 'POST':
        return redirect('language')
    child_name = request.session.get('child_name')
    avatar_image = request.session.get('avatar_url')
    return render(request, 'selectavtar.html', {'child_name': child_name, 'avatar_url': avatar_image})

def language(request):
    child_name = request.session.get('child_name')
    avatar_image = request.session.get('avatar_url')
    options = MyModel.OPTION_CHOICES
    eng_level = Aop_sub_lan.OPTION_CHOICES

    if request.method == 'POST':
        selected_option = request.POST.get('option')
        selected_level = request.POST.get('options')
        request.session['selected_level'] = selected_level

        if selected_option == 'option1':
            with open('1.json') as f:
                json_data = json.load(f)
        elif selected_option == 'option2':
            with open('2.json') as f:
                json_data = json.load(f)
        else:
            pass
        if selected_option == 'BL':
            url = reverse('aop_num', args=[selected_option])
            return redirect(url)
        elif selected_option == 'ML1':
            url = reverse('aop_num', args=[selected_option])
            return redirect(url)
        elif selected_option == 'ML2':
            url = reverse('aop_num', args=[selected_option])
            return redirect(url)
        elif selected_option == 'EL':
            url = reverse('aop_num', args=[selected_option])
            return redirect(url)
        else:
            url = reverse('start_assesment', args=[selected_option])
            return redirect(url)
    return render(request, 'select_lan.html',{'child_name': child_name, 'avatar_url': avatar_image,'options': options,'eng_level':eng_level})

def aop_start_assesment(request):
    return render(request, 'AOP_PRO/six_one.html')

def start_assesment(request,selected_option):
    enrollment_id = request.session.get('enrollment_id')
    status = request.session.get('status')
    request.session['selected_option'] = selected_option
    selected_option = request.session.get('selected_option')
    selected_level = request.session.get('selected_level')
    if request.method == 'POST':

        if selected_level == 'BL':
            return redirect('bl')
        elif selected_level == 'ML1':
            return redirect('bl')
            


    return render(request, 'start_assesment.html',{'selected_option':selected_option,'selected_level':selected_level,'status':status})

def gen_aop_redirect(request,selected_option):
    print("start_assesment",selected_option)
    request.session['selected_option'] = selected_option
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    selected_level = request.session.get('selected_level')
    print("@",selected_level)
    if request.method == 'POST':
        selected_option = request.session.get('selected_option')
        print("@",selected_option)
        if selected_option == 'BL':
            return redirect('bl')
        elif selected_option == 'ML1':
            return redirect('ml1')
        else:
            return redirect('paragraph')

#############################################################################

#                   English Level



def nextpage(request):
    if request.method == 'POST':
        
        selected_option = request.POST.get('selected_option')
        nomistake_list = []
        nomistake_list.append(selected_option)
        nomistake = nomistake_list[0]
        return HttpResponse(str(nomistake))
    
    
def bl(request):
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    selected_level = request.session.get('selected_level')
    print("@",selected_level)
    enrollment_id = request.session.get('enrollment_id')
    print("enrollment_id",enrollment_id)
    phone_number = request.session.get('phone_number')
    print("ph", phone_number)
    enrollment_id = request.session.get('enrollment_id')
    print("enrollment_id",enrollment_id)

    context = {
        'mobile_number': phone_number,
    }
    phone_number = request.session.get('phone_number')
    print(phone_number)
    if request.method == 'POST':

        
        return redirect('start_recording_bl')
    return render(request, 'AOP_PRO/bl_startrecording.html',context)

def start_recording_bl(request):
    paragraph, data_id = get_random_paragraph(request)
    context = {"val": paragraph, "recording": True, "data_id": data_id}
    return render(request, "AOP_PRO/bl_recording.html", context)


def bl_next(request):
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    selected_level = request.session.get('selected_level')
    print("@",selected_level)
    phone_number = request.session.get('phone_number')
    print("ph", phone_number)
    enrollment_id = request.session.get('enrollment_id')
    print("enrollment_id",enrollment_id)
    if request.method == 'POST':
        
        return redirect('start_recording_next_bl')
    return render(request, 'AOP_PRO/bl_startrecording_next.html',{'mobile_number': phone_number})


def start_recording_next_bl(request):
    paragraph, data_id = get_random_paragraph(request)
    context = {"val": paragraph, "recording": True, "data_id": data_id}
    return render(request, "AOP_PRO/bl_recording_next.html", context)


def bl_answer_final(request):
    filepath = request.session.get('filepath')
    filename = request.session.get('filename')


    print(filename)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    
    
    if selected_option == 'English':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_eng) as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'BL':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_l1, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    else:
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_l1, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

    if val:
        print("the val",val)
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': 'English' ,'question':val}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    print('***', response.text)
    request.session['transcript'] = response.text
    phone_number = request.session.get('phone_number')
    enrollment_id = request.session.get('enrollment_id')

    if response.status_code == 200:

        print("text",val)
        data_string = response.json().get('text')
        mistake = response.json().get('no_mistakes')
        fluency = response.json().get('wcpm') 
        index = response.json().get('sub_details') 
        deld = response.json().get('del_details') 
        wcpm_formatted = '{:.2f}'.format(float(fluency)) if fluency else None              
        filepath = request.session.get('filepath')
        audio_url = None
        if filepath:
            if os.path.exists(filepath):
                filename = os.path.basename(filepath)
                audio_url = request.build_absolute_uri(settings.MEDIA_URL + filename)
            else:
                filepath = None  
        return render(request, 'AOP_PRO/bl_answer_final.html', {'transcript': data_string, 'text':data_string, 'originaltext':val , 'sub_details':index,'del_details':deld, 'audio_url': audio_url, 'no_mistakes': mistake, 'wcpm': wcpm_formatted,  'mobile_number': phone_number,})


@csrf_exempt
def save_file_bl(request):
    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        filename = f'{data_id}.wav'
        # filename = f'{data_id}'+'abc.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        phone_number = request.session.get('phone_number')
        enrollment_id = request.session.get('enrollment_id')

        if os.path.isfile(filepath):
            os.remove(filepath)
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
            request.session['filepath'] = filepath
            request.session['filename'] = filename
            return render(request, 'AOP_PRO/bl_answer.html', { 'filepath': filepath,'mobile_number': phone_number})


def bl_answer(request):
    filepath = request.session.get('filepath')
    filename = request.session.get('filename')
    selected_option = request.session.get('selected_option')
    
    if selected_option == 'English':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_eng) as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'BL':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_l1, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    
    else: 
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_l1, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

    if val:
        print("the val",val)
    phone_number = request.session.get('phone_number')
    print("ph", phone_number)
    enrollment_id = request.session.get('enrollment_id')
    print("enrollment_id",enrollment_id)
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': 'English' ,'question':val}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    print('***', response.text)
    request.session['transcript'] = response.text
    if response.status_code == 200:

        print("text",val)
        data_string = response.json().get('text')
        request.session['data_string'] = data_string
        mistake = response.json().get('no_mistakes')
        fluency = response.json().get('wcpm') 
        index = response.json().get('sub_details') 
        deld = response.json().get('del_details') 


    # Format wcpm to have only two decimal places
        wcpm_formatted = '{:.2f}'.format(float(fluency)) if fluency else None              
        filepath = request.session.get('filepath')
        audio_url = None
        if filepath:
            # Check if the file exists
            if os.path.exists(filepath):
                # Get the file name from the file path
                filename = os.path.basename(filepath)
                audio_url = request.build_absolute_uri(settings.MEDIA_URL + filename)
            else:
                filepath = None  
        return render(request, 'AOP_PRO/bl_answer.html', {'transcript': data_string, 'text':data_string, 'originaltext':val , 'sub_details':index,'del_details':deld, 'audio_url': audio_url, 'no_mistakes': mistake, 'wcpm': wcpm_formatted, 'mobile_number': phone_number})


def bl_retake(request):

    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    media_folder = os.path.join(settings.MEDIA_ROOT)
    for file in os.listdir(media_folder):
        file_path = os.path.join(media_folder, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)
    
    if selected_option == 'English':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        request.session['audio_recorded'] = True
        with open(json_eng) as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'BL':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        request.session['audio_recorded'] = True
        with open(json_l1, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    

    # with open(json_eng) as f:
    #     data = json.load(f)
    #     paragraph = None
    #     for d in data['Paragraph']:
    #         if d['id'] == data_id:
    #             val = d['data']
    #             break

    if val:
        print("the val",val)
    return render(request, "AOP_PRO/bl_retake.html", {"recording": True,"val":val })
   
def bl_skip(request):
        selected_option = request.session.get('selected_option')
        print("@",selected_option)
    
    # if selected_option == 'English':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_eng) as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # elif selected_option == 'BL':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_l1, 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # else:
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_l1, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

        words = val.split()
        my_list = list(words)

        # for i, word in enumerate(my_list):
        #     print("The index of", word, "in the list is:", i)

        phone_number = request.session.get('phone_number')
        print("ph", phone_number)
        enrollment_id = request.session.get('enrollment_id')
        print("enrollment_id",enrollment_id)
        last_index = len(my_list) 
        bl_response = {
                "no_mistakes": last_index,
                "no_del": 3,
                "del_details": "1-is,2-a,3-fox",
                "no_sub": 1,
                "sub_details": "0-that:",
                "status": "success",
                "wcpm": 0.0,
                "text": "",
                "audio_url": "",
                "process_time": 0.7457363605499268
            }
        transcript = json.dumps(bl_response)
        # response = {"no_mistakes": 4, "no_del": 3, "del_details": "1-is,2-a,3-fox", "no_sub": 1, "sub_details": "0-that:", "status": "success", "wcpm": 0.0, "text": "", "audio_url": "https://parakhsa.blob.core.windows.net/vakyansh/ENG_Paragraph_9.wav", "process_time": 0.7457363605499268}
        request.session['transcript'] = transcript
        return render(request, 'AOP_PRO/bl_answer.html', {'originaltext':val ,'wcpm': None,'no_mistakes': last_index, 'mobile_number': phone_number})

def bl_skip_next(request):
 
        # selected_option = request.session.get('selected_option')
        # print("@",selected_option)
    
    # if selected_option == 'English':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_eng) as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # elif selected_option == 'BL':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_l1, 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # else:
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_l1, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

        words = val.split()
        my_list = list(words)

        # for i, word in enumerate(my_list):
        #     print("The index of", word, "in the list is:", i)

        
        last_index = len(my_list)
        bl_response = {
            "no_mistakes": last_index,
            "no_del": 3,
            "del_details": "1-is,2-a,3-fox",
            "no_sub": 1,
            "sub_details": "0-that:",
            "status": "success",
            "wcpm": 0.0,
            "text": "",
            "audio_url": "",
            "process_time": 0.7457363605499268
        }
        transcript = json.dumps(bl_response)
        # response = {"no_mistakes": 4, "no_del": 3, "del_details": "1-is,2-a,3-fox", "no_sub": 1, "sub_details": "0-that:", "status": "success", "wcpm": 0.0, "text": "", "audio_url": "https://parakhsa.blob.core.windows.net/vakyansh/ENG_Paragraph_9.wav", "process_time": 0.7457363605499268}
        request.session['transcript'] = transcript
        phone_number = request.session.get('phone_number')
        print("ph", phone_number)
        enrollment_id = request.session.get('enrollment_id')
        print("enrollment_id",enrollment_id)

        return render(request, 'AOP_PRO/bl_answer_final.html', {'originaltext':val ,'wcpm': None,'no_mistakes': last_index, 'mobile_number': phone_number,})
    
def bl_store(request):
    if request.method == 'POST':   
        fluency_adjustment = request.POST.get('fluency_adjustment')
        print("fluency_adjustment", fluency_adjustment)
        # adjustment_from_storage = request.POST.get('adjustment')
        # print('adjustment_from_storage',adjustment_from_storage)
        # Store the value in the session
        # request.session['adjustment'] = adjustment
        # nomistake_list = []
        # nomistake_list.append(str(request.session['adjustment']))
        # nomistake = nomistake_list[0]
        # print("nomistake", nomistake)
        
        if fluency_adjustment == '0':
            request.session['ans_next_level'] = 'L2'
        else:
            request.session['ans_next_level'] = 'L1'
        enrollment_id = request.session.get('enrollment_id')
        status = request.session.get('status')
        filepath = request.session.get('filepath')
        bl_rec = request.session.get('transcript')
        print('BL_res:', bl_rec)
        transcript_dict = json.loads(bl_rec)
        no_mistakes = transcript_dict.get('no_mistakes')
        no_del = transcript_dict.get('no_del')
        del_details = transcript_dict.get('del_details')
        sub_details = transcript_dict.get('sub_details')
        text = transcript_dict.get('text')
        no_sub = transcript_dict.get('no_sub')
        audio_url = transcript_dict.get('audio_url')
        process_time = transcript_dict.get('process_time')
        id_value = request.session.get('id_value')
        # print("student_id",id_value)
        data_id = request.session.get('data_id')
        # print("sample_id",data_id)
        with open(json_l1, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

        if val:
            print("question",val)
    
        ans_next_level = request.session.get('ans_next_level')

        print("next level",ans_next_level)
   
        data={}
        data["student_id"]=id_value
        data["sample_id"]= "data_id"
        data["level"]= 'L2'
        data["question"]= val
        data["section "]= 'reading'
        data["answer"]= text
        data["audio_url"]= audio_url
        data["mistakes_count"]= '0'
        data["no_mistakes"]= no_mistakes
        data["no_mistakes_edited"]= fluency_adjustment
        data["api_process_time"]= process_time
        data["language"]= 'English'
        data["no_del"]= no_del
        data["del_details"]= del_details
        data["no_sub"]= no_sub
        data["sub_details"]= sub_details
        data["test_type"]= status
        data["next_level"]= ans_next_level
        url = 'https://parakh.pradigi.org/v1/saveprogress/'
        files = []
        payload = {'data': json.dumps(data)}
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        if fluency_adjustment == '0':
            return redirect('bl_mcq_next')  # redirect to bl_mcq function
        else:
            return redirect('bl_next') 
    # except TypeError:
    #   return HttpResponse("Invalid adjustment value")


def bl_next_store(request):
  if request.method == 'POST':
    try:
            fluency_adjustment = request.POST.get('fluency_adjustment')
            print("fluency_adjustment", fluency_adjustment)
            # adjustment_from_storage = request.POST.get('adjustment')
            # print('adjustment_from_storage',adjustment_from_storage)
            # # Store the value in the session
            # request.session['adjustment'] = adjustment_from_storage
            # nomistake_list = []
            # nomistake_list.append(str(request.session['adjustment']))
            # nomistake = nomistake_list[0]
            # print("nomistake", nomistake)
            
            if fluency_adjustment == '0':
                request.session['ans_next_level'] = 'L2'
            else:
                request.session['ans_next_level'] = 'L1'
            
            enrollment_id = request.session.get('enrollment_id')
            status = request.session.get('status')
            filepath = request.session.get('filepath')
            bl_rec = request.session.get('transcript')
            print('BL_res:', bl_rec)
            transcript_dict = json.loads(bl_rec)
            no_mistakes = transcript_dict.get('no_mistakes')
            no_del = transcript_dict.get('no_del')
            del_details = transcript_dict.get('del_details')
            sub_details = transcript_dict.get('sub_details')
            text = transcript_dict.get('text')
            audio_url = transcript_dict.get('audio_url')
            no_sub = transcript_dict.get('no_sub')
            process_time = transcript_dict.get('process_time')
            id_value = request.session.get('id_value')
            # print("#################################################################################")
            print("student_id",id_value)
            data_id = request.session.get('data_id')
            print("sample_id",data_id)
            with open(json_l1, 'r', encoding='utf-8') as f:
                data = json.load(f)
                paragraph = None
                for d in data['Paragraph']:
                    if d['id'] == data_id:
                        val = d['data']
                        break

            if val:
                print("question",val)

            # selected_option = request.session.get('selected_option')
    
            print(status)
            ans_next_level = request.session.get('ans_next_level')


            data={}
            data["student_id"]=id_value
            data["sample_id"]= "data_id"
            data["level"]= 'L2'
            data["question"]= val
            data["section "]= 'reading'
            data["answer"]= text
            data["audio_url"]= audio_url
            data["mistakes_count"]= '0'
            data["no_mistakes"]= no_mistakes
            data["no_mistakes_edited"]= fluency_adjustment
            data["api_process_time"]= process_time
            data["language"]= 'English'
            data["no_del"]= no_del
            data["del_details"]= del_details
            data["no_sub"]= no_sub
            data["sub_details"]= sub_details
            data["test_type"]= status
            data["next_level"]= ans_next_level

            print(data)
            url = 'https://parakh.pradigi.org/v1/saveprogress/'
            files = []
            payload = {'data': json.dumps(data)}
            headers = {}
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            response_data = json.loads(response.text)
            print(fluency_adjustment)
            if fluency_adjustment == '0':
                return redirect('bl_mcq_next') 
            else:
                phone_number = request.session.get('phone_number')
                print("ph", phone_number)
                enrollment_id = request.session.get('enrollment_id')
                print("enrollment_id",enrollment_id)
            
                context = {
                    'mobile_number': phone_number,
                    'level' : "Beginer"
                }
                return render(request, "AOP_PRO/ans_page_aop.html", context=context)
            # print(response.text)

            # if response.status_code == 200:
            #     return HttpResponse(str(nomistake))
    except TypeError:
        return HttpResponse("Invalid adjustment value")


    
def get_random_sentence(request):
    selected_option = request.session.get('selected_option')
    print("get_random_sentence",selected_option)
    if selected_option == 'BL':
        with open(json_l1, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Sentence'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            languages = data1['language']
            return {
                'data': data1['data'],
                'data_id': data_id,
                'languages': languages,
            }
    else:
        with open(json_l1, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Sentence'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            languages = data1['language']
            return {
                'data': data1['data'],
                'data_id': data_id,
                'languages': languages,
            }
       
def bl_mcq_api(request):
    selected_option = request.session.get('selected_option')
    selected_level = request.session.get('selected_level')
    # print("@",selected_level)

    if request.method == 'POST':
        selected_lan = request.POST.get('selected_language_input')
        selecteddiv = request.session.get('selected-div')
        status = request.session.get('status')
        selected_language = request.POST.get('selected_language')
        selected_div = request.POST.get('selected-div')
        data_id = request.session.get('data_id')
        id_value = request.session.get('id_value')
        transcript = request.session.get('transcript')
        transcript_dict = json.loads(transcript)
        no_mistakes = transcript_dict.get('no_mistakes')
        no_del = transcript_dict.get('no_del')
        del_details = transcript_dict.get('del_details')
        sub_details = transcript_dict.get('sub_details')
        text = transcript_dict.get('text')
        audio_url = transcript_dict.get('audio_url')
        process_time = transcript_dict.get('process_time')
        ans_next_level = request.session.get('ans_next_level')
        print('text:', text)
        print('audio_url:', audio_url)
        print('process_time:', process_time)
        with open(json_l1, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Sentence = None
            for d in data['Sentence']:
                if d['id'] == data_id:
                    val = d['data']
                    break
        print("@",selected_option)
        if selected_language == 'hindi':
                print("selected",'hindi')
                request.session['lan'] = selected_language

        elif selected_language == 'marathi':
            print('selected','marathi')
            request.session['lan'] = selected_language

        if selected_language == 'hindi':
            with open(json_l1, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # find the data with matching data_id
                selected_data = next((item for item in data['Sentence'] if item['id'] == data_id), None)
                if selected_data:
                    
                    languages = selected_data['language']
                    selected_language = languages.get(selected_language)
                    options = selected_language.get('options')
                    answer = selected_language.get('answers')
                else:
                    print("Data not found for the given data_id")
        elif selected_language == 'marathi':
            with open(json_l1, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # find the data with matching data_id
                selected_data = next((item for item in data['Sentence'] if item['id'] == data_id), None)
                if selected_data:
                    
                    languages = selected_data['language']
                    selected_language = languages.get(selected_language)
                    options = selected_language.get('options')
                    answer = selected_language.get('answers')
                else:
                    print("Data not found for the given data_id")
           
        print("student_id",id_value)
        print("sample_id",data_id)
        print("level")
        print("section")
        print("question",val)
        print("answer",selected_div) 
        print('audio_url:', audio_url)
        print('mistakes_count', audio_url)
        print('no_mistakes:', no_mistakes)
        print('no_mistakes_edited', no_mistakes)
        print('process_time:', process_time)
        print('language:', 'English')
        print('no_del:', no_del)
        print('del_details:', del_details)
        print('no_sub:', "no_sub")
        print('sub_details:', sub_details)
        print("test_type",status)
        print("next level",ans_next_level)
        print("correct_answer:", answer)
        
        print("answer_check_status:", "answer")
        lan = request.session.get('lan')
        print("lan",lan)
        data={}


        
        data["student_id"]=id_value
        data["sample_id"]= "data_id"
        data["level"]= 'L1'
        data["question"]= val
        data["section "]= 'MCQ'
        data["answer"]= selected_div
        data["audio_url"]= ''
        data["mistakes_count"]= '0'
        data["no_mistakes"]= '0'
        data["no_mistakes_edited"]= '0'
        data["api_process_time"]= '0'
        data["language"]= 'English'
        data["no_del"]= '0'
        data["del_details"]= '0'
        data["no_sub"]= '0'
        data["sub_details"]= '0'
        data["test_type"]= status
        data["next_level"]= ans_next_level
        data["correct_answer"]= answer
        data["answer_check_status"]= 'true'
        data["mcq_language"]= lan



        
        print(data)
        url = 'https://parakh.pradigi.org/v1/saveprogress/'
        files = []
        payload = {'data': json.dumps(data)}
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        print('student_id', response.text)
        response_data = json.loads(response.text)
        print(response.text)
        del request.session['data_id']






        return redirect('ml1')
       


def bl_final_mcq(request):
    context = request.session.get('my_context', {})
    print("context", context)
    if request.method == 'POST':
        selected_div = request.POST.get('selected-div')
        selected_divid = request.POST.get('selected-div_id')
        context['selected_divid'] = selected_divid
        print('selected-div', selected_divid)
        context['selected_div'] = selected_div
        print('selected-div', selected_div)
        selected_language = request.POST.get('selected_language')
        context['selected_language'] = selected_language
        print('selected_language', selected_language)
        return render(request, "AOP_PRO/bl_mcq.html", context)
    context['selected_div'] = context.get('selected_div')  # Add selected_div to context
    return render(request, "AOP_PRO/bl_mcq.html", context)



def bl_mcq(request):
    # selected_option = request.session.get('selected_option')
    # print("@",selected_option)
    # selected_level = request.session.get('selected_level')
    # print("@",selected_level)
    phone_number = request.session.get('phone_number')
    print("ph", phone_number)
    enrollment_id = request.session.get('enrollment_id')
    print("enrollment_id",enrollment_id)
    data = get_random_sentence(request)
    context = {"val": data['data'], "recording": True, "data_id": data['data_id'], "languages": data['languages'], 'mobile_number': phone_number}
    if request.method == 'POST':
        selecteddiv = request.session.get('selected-div')
        print('selected-div',selecteddiv)

        data_id = request.session.get('data_id')
        print("data_id",data_id)
        transcript = request.session.get('transcript')
        print("transcript",transcript)
        return redirect('ml1')
    return render(request, "AOP_PRO/bl_mcq.html", context)

def bl_mcq_next(request):
    # selected_option = request.session.get('selected_option')
    # print("@",selected_option)
    # selected_level = request.session.get('selected_level')
    # print("@",selected_level)
    data = get_random_sentence(request)
    context = {"val": data['data'], "recording": True, "data_id": data['data_id'], "languages": data['languages']}
    request.session['my_context'] = context
    phone_number = request.session.get('phone_number')
    print("ph", phone_number)
    enrollment_id = request.session.get('enrollment_id')
    print("enrollment_id",enrollment_id)
    
    if request.method == 'POST':
        
        return redirect('ml1')
    return render(request, "AOP_PRO/bl_mcq_next.html", context)

def bl_answer_page(request):
    phone_number = request.session.get('phone_number')
    print("ph", phone_number)
    enrollment_id = request.session.get('enrollment_id')
    print("enrollment_id",enrollment_id)

   
    context = {
        'mobile_number': phone_number,
    }
    return render(request, "AOP_PRO/bl_cong.html", context=context)


# def error_recording(request):
#     data_id = request.GET.get('data_id')
#     print(data_id)
#     return render(request, "AOP_PRO/bl_recording.html")
import json
from django.http import HttpResponse

def error_recording(request):
    if request.method == 'GET':
        # dataid = request.GET.get('data_id')
        # request.session['dataid'] = dataid
        data_id = request.session.get('data_id')


        
        print("data_id", data_id)
        with open(json_l1, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    paragraph = d['data']
                    print("data_id", data_id)
            
                    break
            if paragraph:
                print("hello ",paragraph)
            request.session['paragraph'] = paragraph

    return redirect(start)

def start(request):
    # abc= request.session.get(paragraph)
    paragraph = request.session.get('paragraph')
    print("######",paragraph)
    return render(request, "AOP_PRO/bl_recording.html",{'val': paragraph})


#############################################################################################

def get_random_ml1(request):
    with open(json_l2, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Paragraph'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
            
   

def nextpage(request):
    if request.method == 'POST':

        selected_option = request.POST.get('selected_option')
        nomistake_list = []
        nomistake_list.append(selected_option)
        nomistake = nomistake_list[0]
        return HttpResponse(str(nomistake))
    
def ml1(request):
    # selected_option = request.session.get('selected_option')
    # print("@",selected_option)
    # selected_level = request.session.get('selected_level')
    # print("@",selected_level)
    phone_number = request.session.get('phone_number')
    print("ph", phone_number)
    enrollment_id = request.session.get('enrollment_id')
    print("enrollment_id",enrollment_id)
    if request.method == 'POST':
        del request.session['filename']
        del request.session['filepath']


        
        return redirect('start_recording_ml1')
    return render(request, 'AOP_PRO/ml1_startrecording.html',{'mobile_number': phone_number})

def start_recording_ml1(request):
    paragraph, data_id = get_random_ml1(request)
    phone_number = request.session.get('phone_number')
    print("ph", phone_number)
    enrollment_id = request.session.get('enrollment_id')
    print("enrollment_id",enrollment_id)
    context = {"val": paragraph, "recording": True, "data_id": data_id, 'mobile_number': phone_number}
    return render(request, "AOP_PRO/ml1_recording.html", context)

def ml1_next(request):
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    selected_level = request.session.get('selected_level')
    print("@",selected_level)
    filepath = request.session.get('filepath')
    phone_number = request.session.get('phone_number')
    print("ph", phone_number)
    enrollment_id = request.session.get('enrollment_id')
    print("enrollment_id",enrollment_id)
    if request.method == 'POST':
        
        return redirect('start_recording_next_ml1')
    return render(request, 'AOP_PRO/ml1_startrecording_next.html', {'mobile_number': phone_number})

def get_random_ml1_sentence(request):
    selected_option = request.session.get('selected_option')
    print("get_random_sentence",selected_option)
    if selected_option == 'ML1':
        with open(json_l2, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Sentence'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            languages = data1['language']
            return {
                'data': data1['data'],
                'data_id': data_id,
                'languages': languages,
            }
    else:
        with open(json_l2, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Sentence'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            languages = data1['language']
            return {
                'data': data1['data'],
                'data_id': data_id,
                'languages': languages,
            }


def start_recording_next_ml1(request):
    paragraph, data_id = get_random_paragraph(request)
    phone_number = request.session.get('phone_number')
    print("ph", phone_number)
    enrollment_id = request.session.get('enrollment_id')
    print("enrollment_id",enrollment_id)
    context = {"val": paragraph, "recording": True, "data_id": data_id,'mobile_number': phone_number}
    return render(request, "AOP_PRO/ml1_recording_next.html", context)


def ml1_answer_final(request):
    filepath = request.session.get('filepath')
    filename = request.session.get('filename')


    print(filename)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    
    if selected_option == 'English':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_eng) as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'BL':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_l2, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    
    # with open(json_eng) as f:
    #     data = json.load(f)
    #     paragraph = None
    #     for d in data['Paragraph']:
    #         if d['id'] == data_id:
    #             val = d['data']
    #             break
    data_id = request.session.get('data_id')
    print("data_id",data_id)
    with open(json_l2, 'r', encoding='utf-8') as f:
        data = json.load(f)
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break
    if val:
        print("the val",val)
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': 'English' ,'question':val}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    print('***', response.text)
    request.session['ml1_res'] = response.text
    phone_number = request.session.get('phone_number')
    print("ph", phone_number)
    enrollment_id = request.session.get('enrollment_id')
    print("enrollment_id",enrollment_id)
    if response.status_code == 200:

        print("text",val)
        data_string = response.json().get('text')
        mistake = response.json().get('no_mistakes')
        fluency = response.json().get('wcpm') 
        index = response.json().get('sub_details') 
        deld = response.json().get('del_details') 


    # Format wcpm to have only two decimal places
        wcpm_formatted = '{:.2f}'.format(float(fluency)) if fluency else None              
        filepath = request.session.get('filepath')
        audio_url = None
        if filepath:
            # Check if the file exists
            if os.path.exists(filepath):
                # Get the file name from the file path
                filename = os.path.basename(filepath)
                audio_url = request.build_absolute_uri(settings.MEDIA_URL + filename)
            else:
                filepath = None  
        return render(request, 'AOP_PRO/ml1_answer_final.html', {'transcript': data_string, 'text':data_string, 'originaltext':val , 'sub_details':index,'del_details':deld, 'audio_url': audio_url, 'no_mistakes': mistake, 'wcpm': wcpm_formatted, 'mobile_number': phone_number})



@csrf_exempt
def save_file_ml1(request):
    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        print(val)
        filename = f'{data_id}.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        print(filename)
        phone_number = request.session.get('phone_number')
        print("ph", phone_number)
        enrollment_id = request.session.get('enrollment_id')
        print("enrollment_id",enrollment_id)
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
            print(filepath)
            request.session['filepath'] = filepath
            request.session['filename'] = filename

            return render(request, 'AOP_PRO/ml1_answer.html', { 'filepath': filepath, 'mobile_number': phone_number})


def ml1_answer(request):
    filepath = request.session.get('filepath')
    filename = request.session.get('filename')



    print(filename)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    
    # if selected_option == 'English':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_eng) as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # elif selected_option == 'ML1':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_l2, 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    
    data_id = request.session.get('data_id')
    print("data_id",data_id)
    with open(json_l2, 'r', encoding='utf-8') as f:
        data = json.load(f)
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break

    if val:
        print("the val",val)
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': 'English' ,'question':val}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    print('***', response.text)
    request.session['ml1_res'] = response.text
    phone_number = request.session.get('phone_number')
    print("ph", phone_number)
    enrollment_id = request.session.get('enrollment_id')
    print("enrollment_id",enrollment_id)
    if response.status_code == 200:

        print("text",val)
        data_string = response.json().get('text')
        mistake = response.json().get('no_mistakes')
        fluency = response.json().get('wcpm') 
        index = response.json().get('sub_details') 
        deld = response.json().get('del_details') 


    # Format wcpm to have only two decimal places
        wcpm_formatted = '{:.2f}'.format(float(fluency)) if fluency else None              
        filepath = request.session.get('filepath')
        audio_url = None
        if filepath:
            # Check if the file exists
            if os.path.exists(filepath):
                # Get the file name from the file path
                filename = os.path.basename(filepath)
                audio_url = request.build_absolute_uri(settings.MEDIA_URL + filename)
            else:
                filepath = None  
        return render(request, 'AOP_PRO/ml1_answer.html', {'transcript': data_string, 'text':data_string, 'originaltext':val , 'sub_details':index,'del_details':deld, 'audio_url': audio_url, 'no_mistakes': mistake, 'wcpm': wcpm_formatted,'mobile_number': phone_number})


def ml1_retake(request):

    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    media_folder = os.path.join(settings.MEDIA_ROOT)
    for file in os.listdir(media_folder):
        file_path = os.path.join(media_folder, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)
    
    # if selected_option == 'English':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     request.session['audio_recorded'] = True
    #     with open(json_eng) as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # elif selected_option == 'BL':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     request.session['audio_recorded'] = True
    #     with open(json_l1, 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    

    data_id = request.session.get('data_id')
    print("data_id",data_id)
    request.session['audio_recorded'] = True
    with open(json_l2, 'r', encoding='utf-8') as f:
        data = json.load(f)
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break

    if val:
        print("the val",val)
    phone_number = request.session.get('phone_number')
    print("ph", phone_number)
    enrollment_id = request.session.get('enrollment_id')
    print("enrollment_id",enrollment_id)
    return render(request, "AOP_PRO/ml1_retake.html", {"recording": True,"val":val, 'mobile_number': phone_number })
   
def ml1_skip(request):
  
        selected_option = request.session.get('selected_option')
        print("@",selected_option)
    
    # if selected_option == 'English':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_eng) as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # elif selected_option == 'ML1':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_l2, 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # else:
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_l2, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

        words = val.split()
        my_list = list(words)

        # for i, word in enumerate(my_list):
        #     print("The index of", word, "in the list is:", i)
        phone_number = request.session.get('phone_number')
        print("ph", phone_number)
        enrollment_id = request.session.get('enrollment_id')
        print("enrollment_id",enrollment_id)
        ml1_res= {}
        last_index = len(my_list)
        ml1_response = {
            "no_mistakes": last_index,
            "no_del": 3,
            "del_details": "1-is,2-a,3-fox",
            "no_sub": 1,
            "sub_details": "0-that:",
            "status": "success",
            "wcpm": 0.0,
            "text": "",
            "audio_url": "",
            "process_time": 0.7457363605499268
        }
        transcript = json.dumps(ml1_response)
        request.session['ml1_res'] = transcript
        # request.session['ml1_res'] = response.text

        return render(request, 'AOP_PRO/ml1_answer.html', {'originaltext':val ,'wcpm': None,'no_mistakes': last_index, 'mobile_number': phone_number})
def ml1_skip_next(request):

    # selected_option = request.session.get('selected_option')
    # print("@",selected_option)
    
    # if selected_option == 'English':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_eng) as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # elif selected_option == 'ML1':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_l2, 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # else:
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_l2, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

        words = val.split()
        my_list = list(words)

        # for i, word in enumerate(my_list):
        #     print("The index of", word, "in the list is:", i)
        phone_number = request.session.get('phone_number')
        print("ph", phone_number)
        enrollment_id = request.session.get('enrollment_id')
        print("enrollment_id",enrollment_id)
        
        last_index = len(my_list) 
        ml1_response = {
            "no_mistakes": last_index,
            "no_del": 3,
            "del_details": "1-is,2-a,3-fox",
            "no_sub": 1,
            "sub_details": "0-that:",
            "status": "success",
            "wcpm": 0.0,
            "text": "",
            "audio_url": "",
            "process_time": 0.7457363605499268
        }
        transcript = json.dumps(ml1_response)
        request.session['ml1_res'] = transcript

        return render(request, 'AOP_PRO/ml1_answer_final.html', {'originaltext':val ,'wcpm': None,'no_mistakes': last_index, 'mobile_number': phone_number})



def ml1_store(request):
  if request.method == 'POST':
    try:
        fluency_adjustment = request.POST.get('fluency_adjustment')
        print("fluency_adjustment", fluency_adjustment)
        # adjustment_from_storage = request.POST.get('adjustment')
        # print('adjustment_from_storage',adjustment_from_storage)
        # Store the value in the session
        # request.session['adjustment'] = adjustment_from_storage
        # nomistake_list = []
        # nomistake_list.append(str(request.session['adjustment']))
        # nomistake = nomistake_list[0]
        # print("nomistake", nomistake)
        
        if fluency_adjustment == '0':
            request.session['ans_next_level'] = 'L3'
        else:
            request.session['ans_next_level'] = 'L2'

        enrollment_id = request.session.get('enrollment_id')
        status = request.session.get('status')
        filepath = request.session.get('filepath')
        ml1_res = request.session.get('ml1_res')
        print('ml1_res:', ml1_res)
        transcript_dict = json.loads(ml1_res)
        no_mistakes = transcript_dict.get('no_mistakes')
        print("no_mistakes",no_mistakes)
        no_del = transcript_dict.get('no_del')
        del_details = transcript_dict.get('del_details')
        sub_details = transcript_dict.get('sub_details')
        text = transcript_dict.get('text')
        audio_url = transcript_dict.get('audio_url')
        no_sub = transcript_dict.get('no_sub')
        process_time = transcript_dict.get('process_time')
        id_value = request.session.get('id_value')
        print("student_id",id_value)
        data_id = request.session.get('data_id')
        print("sample_id",data_id)
        with open(json_l1, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

        if val:
            print("question",val)

        selected_option = request.session.get('selected_option')
        print("test_type",selected_option)
        print(status)
        ans_next_level = request.session.get('ans_next_level')
        data={}
        data["student_id"]=id_value
        data["sample_id"]= "data_id"
        data["level"]= 'L2'
        data["question"]= val
        data["section "]= 'reading'
        data["answer"]= text
        data["audio_url"]= audio_url
        data["mistakes_count"]= '0'
        data["no_mistakes"]= no_mistakes
        data["no_mistakes_edited"]= fluency_adjustment
        data["api_process_time"]= process_time
        data["language"]= 'English'
        data["no_del"]= no_del
        data["del_details"]= del_details
        data["no_sub"]= no_sub
        data["sub_details"]= sub_details
        data["test_type"]= status
        data["next_level"]= ans_next_level



        
        print(data)
        url = 'https://parakh.pradigi.org/v1/saveprogress/'
        files = []
        payload = {'data': json.dumps(data)}
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        # print('student_id', response.text)
        response_data = json.loads(response.text)
        print(response.text)

        # if response.status_code == 200:
        #     return HttpResponse(adjustment_from_storage)
        print(fluency_adjustment)
        if fluency_adjustment == '0':
            return redirect('ml1_mcq_next')  # redirect to bl_mcq function
        else:
            return redirect('ml1_next')
    except TypeError:
        return HttpResponse("Invalid adjustment value")

def ml1_next_store(request):
  if request.method == 'POST':
    try:
        fluency_adjustment = request.POST.get('fluency_adjustment')
        print("fluency_adjustment", fluency_adjustment)
        # adjustment_from_storage = request.POST.get('adjustment')
        # print('adjustment_from_storage',adjustment_from_storage)
        # Store the value in the session
        # request.session['adjustment'] = adjustment_from_storage
        # nomistake_list = []
        # nomistake_list.append(str(request.session['adjustment']))
        # nomistake = nomistake_list[0]
        # print("nomistake", nomistake)
        
        if fluency_adjustment == '0':
            request.session['ans_next_level'] = 'L3'
        else:
            request.session['ans_next_level'] = 'L2'

        enrollment_id = request.session.get('enrollment_id')
        status = request.session.get('status')
        filepath = request.session.get('filepath')
        ml1_res = request.session.get('ml1_res')
        print('ml1_res:', ml1_res)
        transcript_dict = json.loads(ml1_res)
        no_mistakes = transcript_dict.get('no_mistakes')
        print("no_mistakes",no_mistakes)
        no_del = transcript_dict.get('no_del')
        del_details = transcript_dict.get('del_details')
        sub_details = transcript_dict.get('sub_details')
        text = transcript_dict.get('text')
        audio_url = transcript_dict.get('audio_url')
        no_sub = transcript_dict.get('no_sub')
        process_time = transcript_dict.get('process_time')
        id_value = request.session.get('id_value')
        print("student_id",id_value)
        data_id = request.session.get('data_id')
        print("sample_id",data_id)
        with open(json_l1, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

        if val:
            print("question",val)

        selected_option = request.session.get('selected_option')
        print("test_type",selected_option)
        print(status)
        ans_next_level = request.session.get('ans_next_level')
        data={}
        data["student_id"]=id_value
        data["sample_id"]= "data_id"
        data["level"]= 'L2'
        data["question"]= val
        data["section "]= 'reading'
        data["answer"]= text
        data["audio_url"]= audio_url
        data["mistakes_count"]= '0'
        data["no_mistakes"]= no_mistakes
        data["no_mistakes_edited"]= fluency_adjustment
        data["api_process_time"]= process_time
        data["language"]= 'English'
        data["no_del"]= no_del
        data["del_details"]= del_details
        data["no_sub"]= no_sub
        data["sub_details"]= sub_details
        data["test_type"]= status
        data["next_level"]= ans_next_level

        print(data)
        url = 'https://parakh.pradigi.org/v1/saveprogress/'
        files = []
        payload = {'data': json.dumps(data)}
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        # print('student_id', response.text)
        response_data = json.loads(response.text)
        print(response.text)

        # if response.status_code == 200:
        #     return HttpResponse(adjustment_from_storage)
        print(fluency_adjustment)
        if fluency_adjustment == '0':
            return redirect('ml1_mcq_next')  # redirect to bl_mcq function
        else:
            phone_number = request.session.get('phone_number')
            print("ph", phone_number)
            enrollment_id = request.session.get('enrollment_id')
            print("enrollment_id",enrollment_id)
        
            context = {
                'mobile_number': phone_number,
                'level' : "L1"
            }
            return render(request, "AOP_PRO/ans_page_aop.html", context=context)
            # return redirect('ml1_answer_page')
    except TypeError:
        return HttpResponse("Invalid adjustment value")



def ml1_final_mcq(request):
    context = request.session.get('ml1_context', {})
    if request.method == 'POST':
        selected_div = request.POST.get('selected-div')
        selected_divid = request.POST.get('selected-div_id')
        context['selected_divid'] = selected_divid
        print('selected-div',selected_divid)
        context['selected_div'] = selected_div
        print('selected-div',selected_div)
        selected_language = request.POST.get('selected_language')
        context['selected_language'] = selected_language
        print('selected_language',selected_language)
        return render(request, "AOP_PRO/ml1_mcq.html", context)
    return render(request, "AOP_PRO/ml1_mcq.html", context)



def ml1_mcq(request):
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    selected_level = request.session.get('selected_level')
    print("@",selected_level)
    data = get_random_ml1_sentence(request)
    context = {"val": data['data'], "recording": True, "data_id": data['data_id'], "languages": data['languages']}
    if request.method == 'POST':
        transcript = request.session.get('transcript')
        print("transcript",transcript)
        return redirect('ml2')
    return render(request, "AOP_PRO/ml1_mcq.html", context)

def ml1_mcq_next(request):
    # selected_option = request.session.get('selected_option')
    # print("@",selected_option)
    # selected_level = request.session.get('selected_level')f
    # print("@",selected_level)
    data = get_random_ml1_sentence(request)
    context = {"val": data['data'], "recording": True, "data_id": data['data_id'], "languages": data['languages']}
    request.session['ml1_context'] = context

    if request.method == 'POST':
        transcript = request.session.get('transcript')
        print("transcript",transcript)
        return redirect('ml2')
    return render(request, "AOP_PRO/ml1_mcq_next.html", context)

def ml1_mcq_api(request):
    selected_option = request.session.get('selected_option')
    selected_level = request.session.get('selected_level')
    # print("@",selected_level)

    if request.method == 'POST':
        selected_lan = request.POST.get('selected_language_input')

        print("lan",selected_lan)
        status = request.session.get('status')
        selected_language = request.POST.get('selected_language')
        selected_div = request.POST.get('selected-div')
        print("#################################################################")
        data_id = request.session.get('data_id')
        print(data_id)
        id_value = request.session.get('id_value')
        ml1_res = request.session.get('ml1_res')

        # transcript = request.session.get('transcript')
        print('ml1_res:', ml1_res)
        transcript_dict = json.loads(ml1_res)
        no_mistakes = transcript_dict.get('no_mistakes')
        no_del = transcript_dict.get('no_del')
        del_details = transcript_dict.get('del_details')
        sub_details = transcript_dict.get('sub_details')
        text = transcript_dict.get('text')
        audio_url = transcript_dict.get('audio_url')
        process_time = transcript_dict.get('process_time')
        ans_next_level = request.session.get('ans_next_level')


        print('text:', text)
        print('audio_url:', audio_url)
        print('process_time:', process_time)
        with open(json_l2, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Sentence = None
            for d in data['Sentence']:
                if d['id'] == data_id:
                    val = d['data']
                    break
        print("@",selected_option)
        if selected_language == 'hindi':
                print("selected",'hindi')
                request.session['lan'] = selected_language

        elif selected_language == 'marathi':
            print('selected','marathi')
            request.session['lan'] = selected_language

        if selected_language == 'hindi':
            with open(json_l2, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # find the data with matching data_id
                selected_data = next((item for item in data['Sentence'] if item['id'] == data_id), None)
                if selected_data:
                    
                    languages = selected_data['language']
                    selected_language = languages.get(selected_language)
                    options = selected_language.get('options')
                    answer = selected_language.get('answers')
                else:
                    print("Data not found for the given data_id")
        elif selected_language == 'marathi':
            with open(json_l2, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # find the data with matching data_id
                selected_data = next((item for item in data['Sentence'] if item['id'] == data_id), None)
                if selected_data:
                    
                    languages = selected_data['language']
                    selected_language = languages.get(selected_language)
                    options = selected_language.get('options')
                    answer = selected_language.get('answers')
                else:
                    print("Data not found for the given data_id")
           
     
        lan = request.session.get('lan')
        print("lan",lan)
        data={}


        
        data["student_id"]=id_value
        data["sample_id"]= "data_id"
        data["level"]= 'L1'
        data["question"]= val
        data["section "]= 'MCQ'
        data["answer"]= selected_div
        data["audio_url"]= ''
        data["mistakes_count"]= '0'
        data["no_mistakes"]= '0'
        data["no_mistakes_edited"]= '0'
        data["api_process_time"]= '0'
        data["language"]= 'English'
        data["no_del"]= '0'
        data["del_details"]= '0'
        data["no_sub"]= '0'
        data["sub_details"]= '0'
        data["test_type"]= status
        data["next_level"]= ans_next_level
        data["correct_answer"]= answer
        data["answer_check_status"]= 'true'
        data["mcq_language"]= lan



        
        print(data)
        url = 'https://parakh.pradigi.org/v1/saveprogress/'
        files = []
        payload = {'data': json.dumps(data)}
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        print('student_id', response.text)
        response_data = json.loads(response.text)
        print(response.text)







        return redirect('ml2')
  


# def ml1_answer_page(request):
#     phone_number = request.session.get('phone_number')
#     print("ph", phone_number)
   
#     context = {
#         'mobile_number': phone_number,
#     }
#     return render(request, "AOP_PRO/ml1_cong.html", context=context)
    
#############################################################################################

# def ml2(request):
#     return render(request, "AOP_PRO/ml2_startrecording.html")

def get_random_ml2(request):
    with open(json_l3, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Paragraph'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
            
   

def nextpage(request):
    if request.method == 'POST':

        selected_option = request.POST.get('selected_option')
        nomistake_list = []
        nomistake_list.append(selected_option)
        nomistake = nomistake_list[0]
        return HttpResponse(str(nomistake))
    
def ml2(request):
    # selected_option = request.session.get('selected_option')
    # print("@",selected_option)
    # selected_level = request.session.get('selected_level')
    # print("@",selected_level)
    if request.method == 'POST':
        
        return redirect('start_recording_ml2')
    return render(request, 'AOP_PRO/ml2_startrecording.html')

def start_recording_ml2(request):
    paragraph, data_id = get_random_ml2(request)
    context = {"val": paragraph, "recording": True, "data_id": data_id}
    return render(request, "AOP_PRO/ml2_recording.html", context)

def ml2_next(request):
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    selected_level = request.session.get('selected_level')
    print("@",selected_level)
    if request.method == 'POST':
        
        return redirect('start_recording_next_ml2')
    return render(request, 'AOP_PRO/ml2_startrecording_next.html')

def get_random_ml2_sentence(request):
    selected_option = request.session.get('selected_option')
    print("get_random_sentence",selected_option)
    if selected_option == 'Ml2':
        with open(json_l3, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Sentence'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            languages = data1['language']
            return {
                'data': data1['data'],
                'data_id': data_id,
                'languages': languages,
            }
    else:
        with open(json_l3, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Sentence'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            languages = data1['language']
            return {
                'data': data1['data'],
                'data_id': data_id,
                'languages': languages,
            }


def start_recording_next_ml2(request):
    paragraph, data_id = get_random_paragraph(request)
    context = {"val": paragraph, "recording": True, "data_id": data_id}
    return render(request, "AOP_PRO/ml2_recording_next.html", context)


def ml2_answer_final(request):
    filepath = request.session.get('filepath')
    filename = request.session.get('filename')


    print(filename)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    
    # if selected_option == 'English':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_eng) as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # elif selected_option == 'BL':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_l1, 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    
    data_id = request.session.get('data_id')
    print("data_id",data_id)
    with open(json_l2, 'r', encoding='utf-8') as f:
        data = json.load(f)
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break

    if val:
        print("the val",val)
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': 'English' ,'question':val}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    print('***', response.text)
    request.session['ml2_res'] = response.text

    if response.status_code == 200:

        print("text",val)
        data_string = response.json().get('text')
        mistake = response.json().get('no_mistakes')
        fluency = response.json().get('wcpm') 
        index = response.json().get('sub_details') 
        deld = response.json().get('del_details') 


    # Format wcpm to have only two decimal places
        wcpm_formatted = '{:.2f}'.format(float(fluency)) if fluency else None              
        filepath = request.session.get('filepath')
        audio_url = None
        if filepath:
            # Check if the file exists
            if os.path.exists(filepath):
                # Get the file name from the file path
                filename = os.path.basename(filepath)
                audio_url = request.build_absolute_uri(settings.MEDIA_URL + filename)
            else:
                filepath = None  
        return render(request, 'AOP_PRO/ml2_answer_final.html', {'transcript': data_string, 'text':data_string, 'originaltext':val , 'sub_details':index,'del_details':deld, 'audio_url': audio_url, 'no_mistakes': mistake, 'wcpm': wcpm_formatted})



@csrf_exempt
def save_file_ml2(request):
    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        print(val)
        filename = f'{data_id}.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        print(filename)
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
            print(filepath)
            request.session['filepath'] = filepath
            request.session['filename'] = filename

            return render(request, 'AOP_PRO/ml2_answer.html', { 'filepath': filepath})


def ml2_answer(request):
    filepath = request.session.get('filepath')
    filename = request.session.get('filename')


    print(filename)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    
    # if selected_option == 'English':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_eng) as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # elif selected_option == 'Ml2':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_l2, 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    
    data_id = request.session.get('data_id')
    print("data_id",data_id)
    with open(json_l2, 'r', encoding='utf-8') as f:
        data = json.load(f)
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break

    if val:
        print("the val",val)
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': 'English' ,'question':val}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    print('***', response.text)
    request.session['ml2_res'] = response.text

    if response.status_code == 200:

        print("text",val)
        data_string = response.json().get('text')
        mistake = response.json().get('no_mistakes')
        fluency = response.json().get('wcpm') 
        index = response.json().get('sub_details') 
        deld = response.json().get('del_details') 


    # Format wcpm to have only two decimal places
        wcpm_formatted = '{:.2f}'.format(float(fluency)) if fluency else None              
        filepath = request.session.get('filepath')
        audio_url = None
        if filepath:
            # Check if the file exists
            if os.path.exists(filepath):
                # Get the file name from the file path
                filename = os.path.basename(filepath)
                audio_url = request.build_absolute_uri(settings.MEDIA_URL + filename)
            else:
                filepath = None  
        return render(request, 'AOP_PRO/ml2_answer.html', {'transcript': data_string, 'text':data_string, 'originaltext':val , 'sub_details':index,'del_details':deld, 'audio_url': audio_url, 'no_mistakes': mistake, 'wcpm': wcpm_formatted})


def ml2_retake(request):

    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    media_folder = os.path.join(settings.MEDIA_ROOT)
    for file in os.listdir(media_folder):
        file_path = os.path.join(media_folder, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)

    # if selected_option == 'English':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     request.session['audio_recorded'] = True
    #     with open(json_eng) as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # elif selected_option == 'BL':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     request.session['audio_recorded'] = True
    #     with open(json_l1, 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    

    data_id = request.session.get('data_id')
    print("data_id",data_id)
    request.session['audio_recorded'] = True
    with open(json_l2, 'r', encoding='utf-8') as f:
        data = json.load(f)
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break

    if val:
        print("the val",val)
    return render(request, "AOP_PRO/ml2_retake.html", {"recording": True,"val":val })
   
def ml2_skip(request):
    # selected_option = request.session.get('selected_option')
    # print("@",selected_option)
    
    # if selected_option == 'English':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_eng) as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # elif selected_option == 'ML2':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_l3, 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # else:
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_l3, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

        words = val.split()
        my_list = list(words)

        # for i, word in enumerate(my_list):
        #     print("The index of", word, "in the list is:", i)

        
        last_index = len(my_list) 
        ml2_response = {
            "no_mistakes": last_index,
            "no_del": 3,
            "del_details": "1-is,2-a,3-fox",
            "no_sub": 1,
            "sub_details": "0-that:",
            "status": "success",
            "wcpm": 0.0,
            "text": "",
            "audio_url": "",
            "process_time": 0.7457363605499268
        }
        transcript = json.dumps(ml2_response)
        request.session['ml2_res'] = transcript
        return render(request, 'AOP_PRO/ml2_answer.html', {'originaltext':val ,'wcpm': None,'no_mistakes': last_index})
def ml2_skip_next(request):
    # selected_option = request.session.get('selected_option')
    # print("@",selected_option)
    
    # if selected_option == 'English':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_eng) as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # elif selected_option == 'ML2':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_l3, 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # else:
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_l3, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

        words = val.split()
        my_list = list(words)

        # for i, word in enumerate(my_list):
        #     print("The index of", word, "in the list is:", i)

        
        last_index = len(my_list) 
        ml2_response = {
            "no_mistakes": last_index,
            "no_del": 3,
            "del_details": "1-is,2-a,3-fox",
            "no_sub": 1,
            "sub_details": "0-that:",
            "status": "success",
            "wcpm": 0.0,
            "text": "",
            "audio_url": "",
            "process_time": 0.7457363605499268
        }
        transcript = json.dumps(ml2_response)
        request.session['ml2_res'] = transcript
        return render(request, 'AOP_PRO/ml2_answer_final.html', {'originaltext':val ,'wcpm': None,'no_mistakes': last_index})




def ml2_store(request):
  if request.method == 'POST':
    try:
            fluency_adjustment = request.POST.get('fluency_adjustment')
            print("fluency_adjustment", fluency_adjustment)
            # adjustment_from_storage = request.POST.get('adjustment')
            # print('adjustment_from_storage',adjustment_from_storage)
            # # Store the value in the session
            # request.session['adjustment'] = adjustment_from_storage
            # nomistake_list = []
            # nomistake_list.append(str(request.session['adjustment']))
            # nomistake = nomistake_list[0]
            # print("nomistake", nomistake)
            
            if fluency_adjustment == '0':
                request.session['ans_next_level'] = 'L4'
            else:
                request.session['ans_next_level'] = 'L3'

            
    
            enrollment_id = request.session.get('enrollment_id')
            status = request.session.get('status')
            filepath = request.session.get('filepath')
            ml1_res = request.session.get('ml1_res')
            print('ml1_res:', ml1_res)
            transcript_dict = json.loads(ml1_res)
            no_mistakes = transcript_dict.get('no_mistakes')
            no_del = transcript_dict.get('no_del')
            del_details = transcript_dict.get('del_details')
            sub_details = transcript_dict.get('sub_details')
            text = transcript_dict.get('text')
            audio_url = transcript_dict.get('audio_url')
            no_sub = transcript_dict.get('no_sub')
            process_time = transcript_dict.get('process_time')
            id_value = request.session.get('id_value')
            # print("#################################################################################")
            print("student_id",id_value)
            data_id = request.session.get('data_id')
            print("sample_id",data_id)
            with open(json_l1, 'r', encoding='utf-8') as f:
                data = json.load(f)
                paragraph = None
                for d in data['Paragraph']:
                    if d['id'] == data_id:
                        val = d['data']
                        break

            if val:
                print("question",val)
            # print("level","L2")
            # print("section", "reading")
            # print('answer', text)
            # print('audio_url:', audio_url)
            # print('no_mistakes:', no_mistakes)
            # print("no_mistakes_edited",nomistake)
            # print('api_process_time:', process_time)
            # selected_option = request.session.get('selected_option')
            # print("test_type",selected_option)
            # # Print the extracted fields
            # print('no_del:', no_del)
            # print('del_details:', del_details)
            # print('sub_details:', sub_details)
            
            # print("filepath",filepath)
            print(status)
            ans_next_level = request.session.get('ans_next_level')

            # print("next level",ans_next_level)
            # print("student id",enrollment_id)
            # print("#################################################################################")
            data={}
            data["student_id"]=id_value
            data["sample_id"]= "data_id"
            data["level"]= 'L2'
            data["question"]= val
            data["section "]= 'reading'
            data["answer"]= text
            data["audio_url"]= audio_url
            data["mistakes_count"]= '0'
            data["no_mistakes"]= no_mistakes
            data["no_mistakes_edited"]= fluency_adjustment
            data["api_process_time"]= process_time
            data["language"]= 'English'
            data["no_del"]= no_del
            data["del_details"]= del_details
            data["no_sub"]= no_sub
            data["sub_details"]= sub_details
            data["test_type"]= status
            data["next_level"]= ans_next_level



            
            print(data)
            url = 'https://parakh.pradigi.org/v1/saveprogress/'
            files = []
            payload = {'data': json.dumps(data)}
            headers = {}
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            # print('student_id', response.text)
            response_data = json.loads(response.text)
            print(fluency_adjustment)
            if fluency_adjustment == '0':
                return redirect('ml2_mcq_next')  # redirect to bl_mcq function
            else:
                return redirect('ml2_next')
            # print(response.text)

            # if response.status_code == 200:
            #     return HttpResponse(str(nomistake))
    except TypeError:
        return HttpResponse("Invalid adjustment value")

def ml2_next_store(request):
  if request.method == 'POST':
    try:
            fluency_adjustment = request.POST.get('fluency_adjustment')
            print("fluency_adjustment", fluency_adjustment)
            # adjustment_from_storage = request.POST.get('adjustment')
            # print('adjustment_from_storage',adjustment_from_storage)
            # # Store the value in the session
            # request.session['adjustment'] = adjustment_from_storage
            # nomistake_list = []
            # nomistake_list.append(str(request.session['adjustment']))
            # nomistake = nomistake_list[0]
            # print("nomistake", nomistake)
            
            if fluency_adjustment == '0':
                request.session['ans_next_level'] = 'L4'
            else:
                request.session['ans_next_level'] = 'L3'

            
    
            enrollment_id = request.session.get('enrollment_id')
            status = request.session.get('status')
            filepath = request.session.get('filepath')
            ml1_res = request.session.get('ml1_res')
            print('ml1_res:', ml1_res)
            transcript_dict = json.loads(ml1_res)
            no_mistakes = transcript_dict.get('no_mistakes')
            no_del = transcript_dict.get('no_del')
            del_details = transcript_dict.get('del_details')
            sub_details = transcript_dict.get('sub_details')
            text = transcript_dict.get('text')
            audio_url = transcript_dict.get('audio_url')
            no_sub = transcript_dict.get('no_sub')
            process_time = transcript_dict.get('process_time')
            id_value = request.session.get('id_value')
            # print("#################################################################################")
            print("student_id",id_value)
            data_id = request.session.get('data_id')
            print("sample_id",data_id)
            with open(json_l1, 'r', encoding='utf-8') as f:
                data = json.load(f)
                paragraph = None
                for d in data['Paragraph']:
                    if d['id'] == data_id:
                        val = d['data']
                        break

            if val:
                print("question",val)
            # print("level","L2")
            # print("section", "reading")
            # print('answer', text)
            # print('audio_url:', audio_url)
            # print('no_mistakes:', no_mistakes)
            # print("no_mistakes_edited",nomistake)
            # print('api_process_time:', process_time)
            # selected_option = request.session.get('selected_option')
            # print("test_type",selected_option)
            # # Print the extracted fields
            # print('no_del:', no_del)
            # print('del_details:', del_details)
            # print('sub_details:', sub_details)
            
            # print("filepath",filepath)
            print(status)
            ans_next_level = request.session.get('ans_next_level')

            # print("next level",ans_next_level)
            # print("student id",enrollment_id)
            # print("#################################################################################")
            data={}
            data["student_id"]=id_value
            data["sample_id"]= "data_id"
            data["level"]= 'L2'
            data["question"]= val
            data["section "]= 'reading'
            data["answer"]= text
            data["audio_url"]= audio_url
            data["mistakes_count"]= '0'
            data["no_mistakes"]= no_mistakes
            data["no_mistakes_edited"]= fluency_adjustment
            data["api_process_time"]= process_time
            data["language"]= 'English'
            data["no_del"]= no_del
            data["del_details"]= del_details
            data["no_sub"]= no_sub
            data["sub_details"]= sub_details
            data["test_type"]= status
            data["next_level"]= ans_next_level



            
            print(data)
            url = 'https://parakh.pradigi.org/v1/saveprogress/'
            files = []
            payload = {'data': json.dumps(data)}
            headers = {}
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            # print('student_id', response.text)
            response_data = json.loads(response.text)
            print(fluency_adjustment)
            if fluency_adjustment == '0':
                return redirect('ml2_mcq_next')  # redirect to bl_mcq function
            else:
                phone_number = request.session.get('phone_number')
                print("ph", phone_number)
                enrollment_id = request.session.get('enrollment_id')
                print("enrollment_id",enrollment_id)
            
                context = {
                    'mobile_number': phone_number,
                    'level' : "L2-sentence"
                }
                return render(request, "AOP_PRO/ans_page_aop.html", context=context)
                # return redirect('ml2_answer_page')
            # print(response.text)

            # if response.status_code == 200:
            #     return HttpResponse(str(nomistake))
    except TypeError:
        return HttpResponse("Invalid adjustment value")



def ml2_mcq_api(request):
    selected_option = request.session.get('selected_option')
    selected_level = request.session.get('selected_level')
    # print("@",selected_level)

    if request.method == 'POST':
        selected_lan = request.POST.get('selected_language_input')

        print("lan",selected_lan)
        status = request.session.get('status')
        selected_language = request.POST.get('selected_language')
        selected_div = request.POST.get('selected-div')
        print("#################################################################")
        data_id = request.session.get('data_id')
        id_value = request.session.get('id_value')
        ml2_res = request.session.get('ml2_res')

        # transcript = request.session.get('transcript')
        print('ml2_res:', ml2_res)
        transcript_dict = json.loads(ml2_res)
        no_mistakes = transcript_dict.get('no_mistakes')
        no_del = transcript_dict.get('no_del')
        del_details = transcript_dict.get('del_details')
        sub_details = transcript_dict.get('sub_details')
        text = transcript_dict.get('text')
        audio_url = transcript_dict.get('audio_url')
        process_time = transcript_dict.get('process_time')
        ans_next_level = request.session.get('ans_next_level')


        print('text:', text)
        print('audio_url:', audio_url)
        print('process_time:', process_time)
        with open(json_l3, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Sentence = None
            for d in data['Sentence']:
                if d['id'] == data_id:
                    val = d['data']
                    break
        print("@",selected_option)
        if selected_language == 'hindi':
                print("selected",'hindi')
                request.session['lan'] = selected_language

        elif selected_language == 'marathi':
            print('selected','marathi')
            request.session['lan'] = selected_language

        if selected_language == 'hindi':
            with open(json_l3, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # find the data with matching data_id
                selected_data = next((item for item in data['Sentence'] if item['id'] == data_id), None)
                if selected_data:
                    
                    languages = selected_data['language']
                    selected_language = languages.get(selected_language)
                    options = selected_language.get('options')
                    answer = selected_language.get('answers')
                else:
                    print("Data not found for the given data_id")
        elif selected_language == 'marathi':
            with open(json_l3, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # find the data with matching data_id
                selected_data = next((item for item in data['Sentence'] if item['id'] == data_id), None)
                if selected_data:
                    
                    languages = selected_data['language']
                    selected_language = languages.get(selected_language)
                    options = selected_language.get('options')
                    answer = selected_language.get('answers')
                else:
                    print("Data not found for the given data_id")
           
        print("student_id",id_value)
        print("sample_id",data_id)
        print("level")
        print("section")
        print("question",val)
        print("answer",selected_div) 
        print('audio_url:', audio_url)
        print('mistakes_count', audio_url)
        print('no_mistakes:', no_mistakes)
        print('no_mistakes_edited', no_mistakes)
        print('process_time:', process_time)
        print('language:', 'English')
        print('no_del:', no_del)
        print('del_details:', del_details)
        print('no_sub:', "no_sub")
        print('sub_details:', sub_details)
        print("test_type",status)
        print("next level",ans_next_level)
        print("correct_answer:", answer)
        
        print("answer_check_status:", "answer")
        lan = request.session.get('lan')
        print("lan",lan)
        data={}


        
        data["student_id"]=id_value
        data["sample_id"]= "data_id"
        data["level"]= 'L3'
        data["question"]= val
        data["section "]= 'MCQ'
        data["answer"]= selected_div
        data["audio_url"]= ''
        data["mistakes_count"]= '0'
        data["no_mistakes"]= '0'
        data["no_mistakes_edited"]= '0'
        data["api_process_time"]= '0'
        data["language"]= 'English'
        data["no_del"]= '0'
        data["del_details"]= '0'
        data["no_sub"]= '0'
        data["sub_details"]= '0'
        data["test_type"]= status
        data["next_level"]= ans_next_level
        data["correct_answer"]= answer
        data["answer_check_status"]= 'true'
        data["mcq_language"]= lan



        
        print(data)
        url = 'https://parakh.pradigi.org/v1/saveprogress/'
        files = []
        payload = {'data': json.dumps(data)}
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        print('student_id', response.text)
        response_data = json.loads(response.text)
        print(response.text)







        return redirect('ml3')

def ml2_final_mcq(request):
    context = request.session.get('ml2_context', {})
    if request.method == 'POST':
        selected_div = request.POST.get('selected-div')
        selected_divid = request.POST.get('selected-div_id')
        context['selected_divid'] = selected_divid
        print('selected-div',selected_divid)
        context['selected_div'] = selected_div
        print('selected-div',selected_div)
        selected_language = request.POST.get('selected_language')
        context['selected_language'] = selected_language
        print('selected_language',selected_language)
        return render(request, "AOP_PRO/ml2_mcq.html", context)
    return render(request, "AOP_PRO/ml2_mcq.html", context)

            
def ml2_mcq(request):
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    selected_level = request.session.get('selected_level')
    print("@",selected_level)
    data = get_random_ml2_sentence(request)
    context = {"val": data['data'], "recording": True, "data_id": data['data_id'], "languages": data['languages']}
    if request.method == 'POST':
        return redirect('ml3')
    return render(request, "AOP_PRO/ml2_mcq.html", context)

def ml2_mcq_next(request):
    # selected_option = request.session.get('selected_option')
    # print("@",selected_option)
    # selected_level = request.session.get('selected_level')
    # print("@",selected_level)
    data = get_random_ml2_sentence(request)
    context = {"val": data['data'], "recording": True, "data_id": data['data_id'], "languages": data['languages']}
    request.session['ml2_context'] = context

    if request.method == 'POST':
        
        return redirect('ml2')
    return render(request, "AOP_PRO/ml2_mcq_next.html", context)


#############################################################################################

def get_random_ml3(request):
    with open(json_l4, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Paragraph'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
            
   

def nextpage(request):
    if request.method == 'POST':

        selected_option = request.POST.get('selected_option')
        nomistake_list = []
        nomistake_list.append(selected_option)
        nomistake = nomistake_list[0]
        return HttpResponse(str(nomistake))
    
def ml3(request):
    if request.method == 'POST':
        
        return redirect('start_recording_ml3')
    return render(request, 'AOP_PRO/ml3_startrecording.html')

def start_recording_ml3(request):
    paragraph, data_id = get_random_ml3(request)
    context = {"val": paragraph, "recording": True, "data_id": data_id}
    return render(request, "AOP_PRO/ml3_recording.html", context)

def ml3_next(request):
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    selected_level = request.session.get('selected_level')
    print("@",selected_level)
    if request.method == 'POST':
        
        return redirect('start_recording_next_ml3')
    return render(request, 'AOP_PRO/ml3_startrecording_next.html')

def get_random_ml3_sentence(request):
    selected_option = request.session.get('selected_option')
    print("get_random_sentence",selected_option)
    if selected_option == 'EL':
        with open(json_l4, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Sentence'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            languages = data1['language']
            return {
                'data': data1['data'],
                'data_id': data_id,
                'languages': languages,
            }
    else:
        with open(json_l4, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Sentence'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            languages = data1['language']
            return {
                'data': data1['data'],
                'data_id': data_id,
                'languages': languages,
            }


def start_recording_next_ml3(request):
    paragraph, data_id = get_random_paragraph(request)
    context = {"val": paragraph, "recording": True, "data_id": data_id}
    return render(request, "AOP_PRO/ml3_recording_next.html", context)


def ml3_answer_final(request):
    filepath = request.session.get('filepath')
    filename = request.session.get('filename')


    print(filename)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    
    # if selected_option == 'English':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_eng) as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # elif selected_option == 'BL':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_l1, 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    
    data_id = request.session.get('data_id')
    print("data_id",data_id)
    with open(json_l4, 'r', encoding='utf-8') as f:
        data = json.load(f)
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break

    if val:
        print("the val",val)
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': 'English' ,'question':val}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    print('***', response.text)
    request.session['ml3_res'] = response.text

    if response.status_code == 200:

        print("text",val)
        data_string = response.json().get('text')
        mistake = response.json().get('no_mistakes')
        fluency = response.json().get('wcpm') 
        index = response.json().get('sub_details') 
        deld = response.json().get('del_details') 


    # Format wcpm to have only two decimal places
        wcpm_formatted = '{:.2f}'.format(float(fluency)) if fluency else None              
        filepath = request.session.get('filepath')
        audio_url = None
        if filepath:
            # Check if the file exists
            if os.path.exists(filepath):
                # Get the file name from the file path
                filename = os.path.basename(filepath)
                audio_url = request.build_absolute_uri(settings.MEDIA_URL + filename)
            else:
                filepath = None  
        return render(request, 'AOP_PRO/ml3_answer_final.html', {'transcript': data_string, 'text':data_string, 'originaltext':val , 'sub_details':index,'del_details':deld, 'audio_url': audio_url, 'no_mistakes': mistake, 'wcpm': wcpm_formatted})



@csrf_exempt
def save_file_ml3(request):
    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        print(val)
        filename = f'{data_id}.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        print(filename)
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
            print(filepath)
            request.session['filepath'] = filepath
            request.session['filename'] = filename

            return render(request, 'AOP_PRO/ml3_answer.html', { 'filepath': filepath})


def ml3_answer(request):
    filepath = request.session.get('filepath')
    filename = request.session.get('filename')


    print(filename)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    
    # if selected_option == 'English':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_eng) as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # elif selected_option == 'Ml3':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_l2, 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    
    data_id = request.session.get('data_id')
    print("data_id",data_id)
    with open(json_l4, 'r', encoding='utf-8') as f:
        data = json.load(f)
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break

    if val:
        print("the val",val)
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': 'English' ,'question':val}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    print('***', response.text)
    request.session['ml3_res'] = response.text

    if response.status_code == 200:

        print("text",val)
        data_string = response.json().get('text')
        mistake = response.json().get('no_mistakes')
        fluency = response.json().get('wcpm') 
        index = response.json().get('sub_details') 
        deld = response.json().get('del_details') 


    # Format wcpm to have only two decimal places
        wcpm_formatted = '{:.2f}'.format(float(fluency)) if fluency else None              
        filepath = request.session.get('filepath')
        audio_url = None
        if filepath:
            # Check if the file exists
            if os.path.exists(filepath):
                # Get the file name from the file path
                filename = os.path.basename(filepath)
                audio_url = request.build_absolute_uri(settings.MEDIA_URL + filename)
            else:
                filepath = None  
        return render(request, 'AOP_PRO/ml3_answer.html', {'transcript': data_string, 'text':data_string, 'originaltext':val , 'sub_details':index,'del_details':deld, 'audio_url': audio_url, 'no_mistakes': mistake, 'wcpm': wcpm_formatted})


def ml3_retake(request):

    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    media_folder = os.path.join(settings.MEDIA_ROOT)
    for file in os.listdir(media_folder):
        file_path = os.path.join(media_folder, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)

    # if selected_option == 'English':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     request.session['audio_recorded'] = True
    #     with open(json_eng) as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # elif selected_option == 'BL':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     request.session['audio_recorded'] = True
    #     with open(json_l1, 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    

    data_id = request.session.get('data_id')
    print("data_id",data_id)
    request.session['audio_recorded'] = True
    with open(json_l4, 'r', encoding='utf-8') as f:
        data = json.load(f)
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break

    if val:
        print("the val",val)
    return render(request, "AOP_PRO/ml3_retake.html", {"recording": True,"val":val })
   
def ml3_skip(request):
    # selected_option = request.session.get('selected_option')
    # print("@",selected_option)
    
    # if selected_option == 'English':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_eng) as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # elif selected_option == 'EL':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_l4, 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # else:
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_l4, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

        words = val.split()
        my_list = list(words)

        # for i, word in enumerate(my_list):
        #     print("The index of", word, "in the list is:", i)

        
        last_index = len(my_list) 
        ml3_response = {
            "no_mistakes": last_index,
            "no_del": 3,
            "del_details": "1-is,2-a,3-fox",
            "no_sub": 1,
            "sub_details": "0-that:",
            "status": "success",
            "wcpm": 0.0,
            "text": "",
            "audio_url": "",
            "process_time": 0.7457363605499268
        }
        transcript = json.dumps(ml3_response)
        request.session['ml3_res'] = transcript
        return render(request, 'AOP_PRO/ml3_answer.html', {'originaltext':val ,'wcpm': None,'no_mistakes': last_index})
def ml3_skip_next(request):
    # selected_option = request.session.get('selected_option')
    # print("@",selected_option)
    
    # if selected_option == 'English':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_eng) as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # elif selected_option == 'EL':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     with open(json_l4, 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    #         paragraph = None
    #         for d in data['Paragraph']:
    #             if d['id'] == data_id:
    #                 val = d['data']
    #                 break
    # else:
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_l4, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

        words = val.split()
        my_list = list(words)
        
        last_index = len(my_list) 
        ml3_response = {
            "no_mistakes": last_index,
            "no_del": 3,
            "del_details": "1-is,2-a,3-fox",
            "no_sub": 1,
            "sub_details": "0-that:",
            "status": "success",
            "wcpm": 0.0,
            "text": "",
            "audio_url": "",
            "process_time": 0.7457363605499268
        }
        transcript = json.dumps(ml3_response)
        request.session['ml3_res'] = transcript
        return render(request, 'AOP_PRO/ml3_answer_final.html', {'originaltext':val ,'wcpm': None,'no_mistakes': last_index})



def ml3_store(request):
   if request.method == 'POST':
    try:
        fluency_adjustment = request.POST.get('fluency_adjustment')
        print("fluency_adjustment", fluency_adjustment)
        # adjustment_from_storage = request.POST.get('adjustment')
        # print('adjustment_from_storage',adjustment_from_storage)
        # Store the value in the session
        # request.session['adjustment'] = adjustment_from_storage
        # nomistake_list = []
        # nomistake_list.append(str(request.session['adjustment']))
        # nomistake = nomistake_list[0]
        # print("nomistake", nomistake)
        
        if fluency_adjustment == '0':
            request.session['ans_next_level'] = 'L4'
        else:
            request.session['ans_next_level'] = 'L4'

        
 
        enrollment_id = request.session.get('enrollment_id')
        status = request.session.get('status')
        filepath = request.session.get('filepath')
        ml3_res = request.session.get('ml3_res')
        print('ml3_res:', ml3_res)
        transcript_dict = json.loads(ml3_res)
        no_mistakes = transcript_dict.get('no_mistakes')
        no_del = transcript_dict.get('no_del')
        del_details = transcript_dict.get('del_details')
        no_sub = transcript_dict.get('no_sub')

        sub_details = transcript_dict.get('sub_details')
        text = transcript_dict.get('text')
        audio_url = transcript_dict.get('audio_url')
        process_time = transcript_dict.get('process_time')
        id_value = request.session.get('id_value')
        print("#################################################################################")
        print("student_id",id_value)
        data_id = request.session.get('data_id')
        print("sample_id",data_id)
        with open(json_l4, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

        if val:
            print("question",val)
        selected_option = request.session.get('selected_option')
        print("test_type",selected_option)
        ans_next_level = request.session.get('ans_next_level')
        print("next level",ans_next_level)

        data={}
        data["student_id"]=id_value
        data["sample_id"]= "data_id"
        data["level"]= 'L2'
        data["question"]= val
        data["section "]= 'reading'
        data["answer"]= text
        data["audio_url"]= audio_url
        data["mistakes_count"]= '0'
        data["no_mistakes"]= no_mistakes
        data["no_mistakes_edited"]= fluency_adjustment
        data["api_process_time"]= process_time
        data["language"]= 'English'
        data["no_del"]= no_del
        data["del_details"]= del_details
        data["no_sub"]= no_sub
        data["sub_details"]= sub_details
        data["test_type"]= status
        data["next_level"]= ans_next_level
        print(data)
        url = 'https://parakh.pradigi.org/v1/saveprogress/'
        files = []
        payload = {'data': json.dumps(data)}
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        print('student_id', response.text)
        response_data = json.loads(response.text)
        print(fluency_adjustment)
        if fluency_adjustment == '0':
            return redirect('ml3_mcq_next')  # redirect to bl_mcq function
        else:
            return redirect('ml3_next')
    except TypeError:
      return HttpResponse("Invalid adjustment value")
    

def ml3_next_store(request):
   if request.method == 'POST':
    try:
        fluency_adjustment = request.POST.get('fluency_adjustment')
        print("fluency_adjustment", fluency_adjustment)
        # adjustment_from_storage = request.POST.get('adjustment')
        # print('adjustment_from_storage',adjustment_from_storage)
        # Store the value in the session
        # request.session['adjustment'] = adjustment_from_storage
        # nomistake_list = []
        # nomistake_list.append(str(request.session['adjustment']))
        # nomistake = nomistake_list[0]
        # print("nomistake", nomistake)
        
        if fluency_adjustment == '0':
            request.session['ans_next_level'] = 'L4'
        else:
            request.session['ans_next_level'] = 'L4'

        
 
        enrollment_id = request.session.get('enrollment_id')
        status = request.session.get('status')
        filepath = request.session.get('filepath')
        ml3_res = request.session.get('ml3_res')
        print('ml3_res:', ml3_res)
        transcript_dict = json.loads(ml3_res)
        no_mistakes = transcript_dict.get('no_mistakes')
        no_del = transcript_dict.get('no_del')
        del_details = transcript_dict.get('del_details')
        no_sub = transcript_dict.get('no_sub')

        sub_details = transcript_dict.get('sub_details')
        text = transcript_dict.get('text')
        audio_url = transcript_dict.get('audio_url')
        process_time = transcript_dict.get('process_time')
        id_value = request.session.get('id_value')
        print("#################################################################################")
        print("student_id",id_value)
        data_id = request.session.get('data_id')
        print("sample_id",data_id)
        with open(json_l4, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

        if val:
            print("question",val)
        selected_option = request.session.get('selected_option')
        print("test_type",selected_option)
        ans_next_level = request.session.get('ans_next_level')
        print("next level",ans_next_level)

        data={}
        data["student_id"]=id_value
        data["sample_id"]= "data_id"
        data["level"]= 'L2'
        data["question"]= val
        data["section "]= 'reading'
        data["answer"]= text
        data["audio_url"]= audio_url
        data["mistakes_count"]= '0'
        data["no_mistakes"]= no_mistakes
        data["no_mistakes_edited"]= fluency_adjustment
        data["api_process_time"]= process_time
        data["language"]= 'English'
        data["no_del"]= no_del
        data["del_details"]= del_details
        data["no_sub"]= no_sub
        data["sub_details"]= sub_details
        data["test_type"]= status
        data["next_level"]= ans_next_level
        print(data)
        url = 'https://parakh.pradigi.org/v1/saveprogress/'
        files = []
        payload = {'data': json.dumps(data)}
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        print('student_id', response.text)
        response_data = json.loads(response.text)
        print(fluency_adjustment)
        if fluency_adjustment == '0':
            return redirect('ml3_mcq_next')  # redirect to bl_mcq function
        else:
            phone_number = request.session.get('phone_number')
            print("ph", phone_number)
            enrollment_id = request.session.get('enrollment_id')
            print("enrollment_id",enrollment_id)
        
            context = {
                'mobile_number': phone_number,
                'level' : "L2-sentence"
            }
            return render(request, "AOP_PRO/ans_page_aop.html", context=context)
            # return redirect('ml3_answer_page')
    except TypeError:
      return HttpResponse("Invalid adjustment value")
    

def ml3_mcq_api(request):
    selected_option = request.session.get('selected_option')
    selected_level = request.session.get('selected_level')
    # print("@",selected_level)

    if request.method == 'POST':
        selected_lan = request.POST.get('selected_language_input')

        print("lan",selected_lan)
        status = request.session.get('status')
        selected_language = request.POST.get('selected_language')
        selected_div = request.POST.get('selected-div')
        print("#################################################################")
        data_id = request.session.get('data_id')
        id_value = request.session.get('id_value')
        ml3_res = request.session.get('ml3_res')

        # transcript = request.session.get('transcript')
        print('ml3_res:', ml3_res)
        transcript_dict = json.loads(ml3_res)
        no_mistakes = transcript_dict.get('no_mistakes')
        no_del = transcript_dict.get('no_del')
        del_details = transcript_dict.get('del_details')
        sub_details = transcript_dict.get('sub_details')
        text = transcript_dict.get('text')
        audio_url = transcript_dict.get('audio_url')
        process_time = transcript_dict.get('process_time')
        ans_next_level = request.session.get('ans_next_level')


        print('text:', text)
        print('audio_url:', audio_url)
        print('process_time:', process_time)
        with open(json_l4, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Sentence = None
            for d in data['Sentence']:
                if d['id'] == data_id:
                    val = d['data']
                    break
        print("@",selected_option)
        if selected_language == 'hindi':
                print("selected",'hindi')
                request.session['lan'] = selected_language

        elif selected_language == 'marathi':
            print('selected','marathi')
            request.session['lan'] = selected_language

        if selected_language == 'hindi':
            with open(json_l4, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # find the data with matching data_id
                selected_data = next((item for item in data['Sentence'] if item['id'] == data_id), None)
                if selected_data:
                    
                    languages = selected_data['language']
                    selected_language = languages.get(selected_language)
                    options = selected_language.get('options')
                    answer = selected_language.get('answers')
                else:
                    print("Data not found for the given data_id")
        elif selected_language == 'marathi':
            with open(json_l4, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # find the data with matching data_id
                selected_data = next((item for item in data['Sentence'] if item['id'] == data_id), None)
                if selected_data:
                    
                    languages = selected_data['language']
                    selected_language = languages.get(selected_language)
                    options = selected_language.get('options')
                    answer = selected_language.get('answers')
                else:
                    print("Data not found for the given data_id")
           
        print("student_id",id_value)
        print("sample_id",data_id)
        print("level")
        print("section")
        print("question",val)
        print("answer",selected_div) 
        print('audio_url:', audio_url)
        print('mistakes_count', audio_url)
        print('no_mistakes:', no_mistakes)
        print('no_mistakes_edited', no_mistakes)
        print('process_time:', process_time)
        print('language:', 'English')
        print('no_del:', no_del)
        print('del_details:', del_details)
        print('no_sub:', "no_sub")
        print('sub_details:', sub_details)
        print("test_type",status)
        print("next level",ans_next_level)
        print("correct_answer:", answer)
        
        print("answer_check_status:", "answer")
        lan = request.session.get('lan')
        print("lan",lan)
        data={}


        
        data["student_id"]=id_value
        data["sample_id"]= "data_id"
        data["level"]= 'L3'
        data["question"]= val
        data["section "]= 'MCQ'
        data["answer"]= selected_div
        data["audio_url"]= ''
        data["mistakes_count"]= '0'
        data["no_mistakes"]= '0'
        data["no_mistakes_edited"]= '0'
        data["api_process_time"]= '0'
        data["language"]= 'English'
        data["no_del"]= '0'
        data["del_details"]= '0'
        data["no_sub"]= '0'
        data["sub_details"]= '0'
        data["test_type"]= status
        data["next_level"]= ans_next_level
        data["correct_answer"]= answer
        data["answer_check_status"]= 'true'
        data["mcq_language"]= lan



        
        print(data)
        url = 'https://parakh.pradigi.org/v1/saveprogress/'
        files = []
        payload = {'data': json.dumps(data)}
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        print('student_id', response.text)
        response_data = json.loads(response.text)
        print(response.text)
        phone_number = request.session.get('phone_number')
        print("ph", phone_number)
        enrollment_id = request.session.get('enrollment_id')
        print("enrollment_id",enrollment_id)
    
        context = {
            'mobile_number': phone_number,
            'level' : "L2-sentence"
        }
        return render(request, "AOP_PRO/ans_page_aop.html", context=context)
        # return redirect('ml3_answer_page')
def ml3_ans(request):
    return render(request, "AOP_PRO/ml3_cong.html")
    
def ml3_final_mcq(request):
    context = request.session.get('ml3_context', {})
    if request.method == 'POST':
        selected_div = request.POST.get('selected-div')
        selected_divid = request.POST.get('selected-div_id')
        context['selected_divid'] = selected_divid
        print('selected-div',selected_divid)
        context['selected_div'] = selected_div
        print('selected-div',selected_div)
        selected_language = request.POST.get('selected_language')
        context['selected_language'] = selected_language
        print('selected_language',selected_language)
        return render(request, "AOP_PRO/ml3_mcq.html", context)
    return render(request, "AOP_PRO/ml3_mcq.html", context)
    



def ml3_mcq(request):
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    selected_level = request.session.get('selected_level')
    print("@",selected_level)
    data = get_random_ml3_sentence(request)
    context = {"val": data['data'], "recording": True, "data_id": data['data_id'], "languages": data['languages']}
    # if request.method == 'POST':
    #     return redirect('ml3')
    return render(request, "AOP_PRO/ml3_mcq.html", context)

def ml3_mcq_next(request):
    # selected_option = request.session.get('selected_option')
    # print("@",selected_option)
    # selected_level = request.session.get('selected_level')
    # print("@",selected_level)
    data = get_random_ml3_sentence(request)
    context = {"val": data['data'], "recording": True, "data_id": data['data_id'], "languages": data['languages']}
    request.session['ml3_context'] = context
    
    if request.method == 'POST':
        
        return redirect('ml3')
    return render(request, "AOP_PRO/ml3_mcq_next.html", context)
    

#############################################################################################


def start_recording(request):
    paragraph, data_id = get_random_paragraph(request)
    context = {"val": paragraph, "recording": True, "data_id": data_id}
    return render(request, "para_rec.html", context)


#                   Paragraph Recording

def paragraph(request):
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    # selected_level = request.session.get('selected_level')
    # print("@",selected_level)
    if request.method == 'POST':
        return redirect('start_recording')
    return render(request, 'para_start.html')



def get_random_paragraph(request):
    selected_option = request.session.get('selected_option')
    print("get_random_paragraph",selected_option)
    if selected_option == 'English':
        with open(json_eng, 'r') as f:
            data = json.load(f)
            data1 = random.choice(data['Paragraph'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'BL':
        with open(json_l1, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Paragraph'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'ML1':
        with open(json_l2, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Paragraph'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'ML2':
        with open(json_l3, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Paragraph'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'EL':
        with open(json_l4, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Paragraph'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Hindi':
        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Paragraph'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Assamese':
        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Paragraph'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Bengali':
        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Paragraph'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Gujarati':
        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Paragraph'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Kannada':
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Paragraph'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Malayalam':
        with open(json_mal, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Paragraph'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Marathi':
        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Paragraph'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Odiya':
        with open(json_odi, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Paragraph'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Punjabi':
        with open(json_pun, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Paragraph'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Tamil':
        with open(json_tami, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Paragraph'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Telugu':
        with open(json_tel, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Paragraph'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Urdu':
        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Paragraph'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    
@csrf_exempt
def save_file(request):
    print("the file is saved")
    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('question')
        print("value",val)
        
        filename = f'{data_id}.wav'
        # filename = f'{data_id}'+'abc.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        print("filename",filename)
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
            print("filepath",filepath)
            request.session['filepath'] = filepath
            request.session['filename'] = filename

            return render(request, 'para_ans.html', { 'filepath': filepath})


def answer(request):
    filepath = request.session.get('filepath')
    filename = request.session.get('filename')
    print(filename)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    if selected_option == 'English':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_eng) as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'BL':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_l1, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Hindi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    print("hindi", val)
                    break
    elif selected_option == 'Assamese':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Bengali':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Gujarati':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Marathi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Kannada':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Malayalam':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_mal, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Odiya':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_odi, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Punjabi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_pun, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Tamil':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_tami, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Telugu':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_tel, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Urdu':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    # with open(json_eng) as f:
    #     data = json.load(f)
    #     paragraph = None
    #     for d in data['Paragraph']:
    #         if d['id'] == data_id:
    #             val = d['data']
    #             break

    if val:
        print("the val",val)
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': selected_option ,'question':val}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    print('***', response.text)

    if response.status_code == 200:
        print("text",val)
        request.session['val'] = val
        data_string = response.json().get('text')
        mistake = response.json().get('no_mistakes')
        fluency = response.json().get('wcpm') 
        index = response.json().get('sub_details') 
        deld = response.json().get('del_details') 

    # Format wcpm to have only two decimal places
        wcpm_formatted = '{:.2f}'.format(float(fluency)) if fluency else None              
        filepath = request.session.get('filepath')
        audio_url = None
        if filepath:
            # Check if the file exists
            if os.path.exists(filepath):
                # Get the file name from the file path
                filename = os.path.basename(filepath)
                audio_url = request.build_absolute_uri(settings.MEDIA_URL + filename + '?v=' + str(datetime.now()))
            else:
                filepath = None  
        return render(request, 'para_ans.html', {'transcript': data_string, 'text':data_string, 'originaltext':val , 'sub_details':index,'del_details':deld, 'audio_url': audio_url, 'no_mistakes': mistake, 'wcpm': wcpm_formatted})


def skip_answer(request):

    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    if selected_option == 'English':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_eng) as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'BL':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_l1, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Hindi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Assamese':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Bengali':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Gujarati':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Marathi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Kannada':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Malayalam':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_mal, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Odiya':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_odi, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Punjabi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_pun, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Tamil':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_tami, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Telugu':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_tel, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Urdu':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

    # with open(json_eng) as f:
    #     data = json.load(f)
    #     paragraph = None
    #     for d in data['Paragraph']:
    #         if d['id'] == data_id:
    #             val = d['data']
    #             break

    if val:
        print("the val",val)

    words = val.split()
    my_list = list(words)


    
    last_index = len(my_list) 
    return render(request, 'para_ans.html', {'originaltext': val, 'wcpm': None, 'no_mistakes': last_index})




def next_page(request):
    if request.method == 'POST':
        total_mis = request.POST.get('total_mis')
        print("total_mis",total_mis)
        media_folder = os.path.join(settings.MEDIA_ROOT)
        for file in os.listdir(media_folder):
            file_path = os.path.join(media_folder, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)
        audio_file_name = request.session.setdefault('audio_file_name', [])
        audio_file_name.clear()

     
        if total_mis <= '1':
            child_name = request.session.get('child_name')
            level = "Word"
            return render(request,'answer_page_gen.html',{'child_name': child_name, 'level': level})
            # return redirect("word_msg")
        else:
            return redirect("letter")

def next_page_para(request):
    if request.method == 'POST':
        word_mistakes = request.POST.get('no_mistakes')
        print("no_mistakes",word_mistakes)
        media_folder = os.path.join(settings.MEDIA_ROOT)
        for file in os.listdir(media_folder):
            file_path = os.path.join(media_folder, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)
        audio_file_name = request.session.setdefault('audio_file_name', [])
        audio_file_name.clear()

        if word_mistakes > '3':
            return redirect("story")
        else:
            return redirect("word")

def next_page_story(request):
    if request.method == 'POST':
        word_mistakes = request.POST.get('no_mistakes')
        print("no_mistakes",word_mistakes)
        media_folder = os.path.join(settings.MEDIA_ROOT)
        for file in os.listdir(media_folder):
            file_path = os.path.join(media_folder, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)
        audio_file_name = request.session.setdefault('audio_file_name', [])
        audio_file_name.clear()

        
        if word_mistakes > '3':
            child_name = request.session.get('child_name')
            level = "Story"
            return render(request,'answer_page_gen.html',{'child_name': child_name, 'level': level})
            # return redirect("next_answer")
        else:
            child_name = request.session.get('child_name')
            level = "Word"
            return render(request,'answer_page_gen.html',{'child_name': child_name, 'level': level})
            # return redirect("word_msg")

def next_page_letter(request):
    if request.method == 'POST':
        total_mis = request.POST.get('total_mis')
        print("total_mis",total_mis)
        media_folder = os.path.join(settings.MEDIA_ROOT)
        for file in os.listdir(media_folder):
            file_path = os.path.join(media_folder, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)
        audio_file_name = request.session.setdefault('audio_file_name', [])
        audio_file_name.clear()

        if total_mis <= '1':
            child_name = request.session.get('child_name')
            level = "Letter"
            return render(request,'answer_page_gen.html',{'child_name': child_name, 'level': level})
        else:
            child_name = request.session.get('child_name')
            level = "Begineer"
            return render(request,'answer_page_gen.html',{'child_name': child_name, 'level': level})

        
def next_para(request):
    t.sleep(2)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    media_folder = os.path.join(settings.MEDIA_ROOT)

    for file in os.listdir(media_folder):
            file_path = os.path.join(media_folder, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)
    
    if selected_option == 'English':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        request.session['audio_recorded'] = True
        with open(json_eng) as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'BL':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        request.session['audio_recorded'] = True
        with open(json_l1, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Hindi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        request.session['audio_recorded'] = True

        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Assamese':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        request.session['audio_recorded'] = True

        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Bengali':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        request.session['audio_recorded'] = True

        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Gujarati':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        request.session['audio_recorded'] = True

        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Marathi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        request.session['audio_recorded'] = True

        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Kannada':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        request.session['audio_recorded'] = True

        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Malayalam':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        request.session['audio_recorded'] = True

        with open(json_mal, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Odiya':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        request.session['audio_recorded'] = True

        with open(json_odi, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Punjabi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        request.session['audio_recorded'] = True

        with open(json_pun, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Tamil':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        request.session['audio_recorded'] = True

        with open(json_tami, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Telugu':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        request.session['audio_recorded'] = True

        with open(json_tel, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Urdu':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        request.session['audio_recorded'] = True

        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

    # with open(json_eng) as f:
    #     data = json.load(f)
    #     paragraph = None
    #     for d in data['Paragraph']:
    #         if d['id'] == data_id:
    #             val = d['data']
    #             break

    if val:
        print("the val",val)
    return render(request, "para_rec_next.html", {"recording": True,"val":val })
   

#                   Story Recording


def story(request):
    if request.method == 'POST':
        return redirect('story_recording')
    return render(request, 'story_start.html')


def get_random_story(request):
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    if selected_option == 'English':
        with open(json_eng, 'r') as f:
            data = json.load(f)
            data1 = random.choice(data['Story'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Hindi':
        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Story'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Assamese':
        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Story'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Bengali':
        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Story'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Gujarati':
        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Story'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Marathi':
        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Story'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Kannada':
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Story'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Malayalam':
        with open(json_mal, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Story'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Odiya':
        with open(json_odi, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Story'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Punjabi':
        with open(json_pun, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Story'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Tamil':
        with open(json_tami, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Story'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Telugu':
        with open(json_tel, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Story'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    elif selected_option == 'Urdu':
        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Story'])
            print("the value ",data1['id'])
            data_id = data1['id']
            request.session['data_id'] = data_id
            print(data_id)
            print("dta",data1['data'])
            return data1['data'], data_id
    # with open(json_eng, 'r') as f:
    #     data = json.load(f)
    #     data1 = random.choice(data['Story'])
    #     print("the value ",data1['id'])
    #     data_id = data1['id']
    #     request.session['data_id'] = data_id
    #     print(data_id)
    #     print("dta",data1['data'])
    #     return data1['data'], data_id




def story_recording(request):
    Story, data_id = get_random_story(request)
    context = {"val": Story, "recording": True, "data_id": data_id}
    return render(request, "story_rec.html", context)

@csrf_exempt
def save_story(request):
    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        print(val)
        filename = f'{data_id}.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
            print(filepath)
            request.session['filepath'] = filepath
            return render(request, 'story_ans.html', { 'audio_url': filepath})
# def story_skip(request):
#     if "stop" in request.POST:
#         return redirect('story_recording')
    
def story_answer(request):
    filepath = request.session.get('filepath')
    print(filepath)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    
    if selected_option == 'English':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_eng) as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Hindi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Assamese':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Bengali':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Gujarati':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Marathi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Kannada':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Malayalam':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_mal, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Odiya':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_odi, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Punjabi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_pun, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Tamil':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_tami, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Telugu':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_tel, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Urdu':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
                

    if val:
        print("the val",val)
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': selected_option,'question':val}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    print('***', response.text)

    if response.status_code == 200: 
        filepath = request.session.get('filepath')
        print("filepath",filepath)
        data_string = response.json().get('text')
        mistake = response.json().get('no_mistakes')
        fluency = response.json().get('wcpm') 
        index = response.json().get('sub_details') 
        deld = response.json().get('del_details')
        wcpm_formatted = '{:.2f}'.format(float(fluency)) if fluency else None  
        audio_url = None
        if filepath:
            # Check if the file exists
            if os.path.exists(filepath):
                # Get the file name from the file path
                filename = os.path.basename(filepath)
                audio_url = request.build_absolute_uri(settings.MEDIA_URL + filename)
            else:
                filepath = None                

        return render(request, 'story_ans.html', {'transcript': data_string, 'text':data_string , 'originaltext':val ,'sub_details':index,'del_details':deld,'audio_url': audio_url, 'no_mistakes': mistake, 'wcpm': wcpm_formatted})

   
def skip_story_answer(request):
    # filepath = os.path.join(settings.MEDIA_ROOT, 'skip_story.wav')
    # if not os.path.exists(filepath):
    #     return HttpResponseBadRequest('Audio file not found')


    # print(filepath)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    
    if selected_option == 'English':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_eng) as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Hindi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break

    elif selected_option == 'Assamese':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Bengali':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Gujarati':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Marathi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Kannada':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Malayalam':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_mal, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Odiya':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_odi, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Punjabi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_pun, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Tamil':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_tami, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Telugu':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_tel, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Urdu':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break

    if val:
        print("the val",val)




    words = val.split()
    my_list = list(words)

    # for i, word in enumerate(my_list):
    #     print("The index of", word, "in the list is:", i)

    
    last_index = len(my_list) 
    return render(request, 'story_ans.html', {'originaltext': val, 'wcpm': None, 'no_mistakes': last_index})


def next_story(request):
    t.sleep(2)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    media_folder = os.path.join(settings.MEDIA_ROOT)

    for file in os.listdir(media_folder):
            file_path = os.path.join(media_folder, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)
    if selected_option == 'English':
        data_id = request.session.get('data_id')
        request.session['audio_recorded'] = True
        with open(json_eng) as f:
            data = json.load(f)
            Story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Hindi':
        data_id = request.session.get('data_id')
        request.session['audio_recorded'] = True
        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Assamese':
        data_id = request.session.get('data_id')
        request.session['audio_recorded'] = True
        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Bengali':
        data_id = request.session.get('data_id')
        request.session['audio_recorded'] = True
        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Gujarati':
        data_id = request.session.get('data_id')
        request.session['audio_recorded'] = True
        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Marathi':
        data_id = request.session.get('data_id')
        request.session['audio_recorded'] = True
        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Kannada':
        data_id = request.session.get('data_id')
        request.session['audio_recorded'] = True
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Malayalam':
        data_id = request.session.get('data_id')
        request.session['audio_recorded'] = True
        with open(json_mal, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Odiya':
        data_id = request.session.get('data_id')
        request.session['audio_recorded'] = True
        with open(json_odi, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Punjabi':
        data_id = request.session.get('data_id')
        request.session['audio_recorded'] = True
        with open(json_pun, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Tamil':
        data_id = request.session.get('data_id')
        request.session['audio_recorded'] = True
        with open(json_tami, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Telugu':
        data_id = request.session.get('data_id')
        request.session['audio_recorded'] = True
        with open(json_tel, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Urdu':
        data_id = request.session.get('data_id')
        request.session['audio_recorded'] = True
        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Story = None
            for d in data['Story']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    if val:
        print("the val",val)
    return render(request, "story_rec_next.html", {"recording": True,"val":val })
   

def thirteen(request):
    return render(request, 'thirteen.html')
def fourteen(request):
    return render(request, 'fourteen.html')


#                   Word Recording

def word(request):
    d_audio_files = request.session.setdefault('d_audio_files', [])
    d_audio_files_name = request.session.setdefault('d_audio_files_name', [])
    qword = request.session.setdefault('qword', [])
    skip_val = request.session.setdefault('skip_val', [])

    d_dataid = request.session.setdefault('d_dataid', [])
    audio_file = request.session.setdefault('audio_file', [])
    file = request.session.setdefault('file', [])
    word_ids = request.session.setdefault('word_ids', [])
    dc_res = request.session.setdefault('dc_res', [])

    print(dc_res)
    del request.session['skip_val']
    del request.session['dc_res']
    del request.session['word_ids']
    del request.session['file']
    del request.session['audio_file']
    del request.session['d_dataid']
    del request.session['qword']
    del request.session['d_audio_files_name']
    del request.session['d_audio_files']


    
    
    if request.method == 'POST':
        print("qword",qword)
        
        if len(dc_res) == 5:
            dc_res.clear()
            d_dataid.clear()
            skip_val.clear()
            # qword.clear()
            # print("qword",qword)
            print(dc_res)
            print(d_dataid)
            print(d_dataid)

            qword.clear()
            word_ids.clear()
            d_audio_files.clear()
            d_audio_files_name.clear()
            dc_res.clear()
            d_dataid.clear()
            print(audio_file)
            audio_file.clear()  # clear the audio_file list
            print(audio_file)
            file.clear()
            if len(d_audio_files)>5:
                d_audio_files.clear()
                d_audio_files_name.clear() 
        elif len(dc_res)==4:
            dc_res.clear()
            d_dataid.clear()
            # qword.clear()
            # print("qword",qword)
            print(dc_res)
            print(d_dataid)
            qword.clear()
            word_ids.clear()
            d_audio_files.clear()
            d_audio_files_name.clear()
            dc_res.clear()
            d_dataid.clear()
            print(audio_file)
            audio_file.clear()  # clear the audio_file list
            print(audio_file)
            file.clear()
            if len(d_audio_files)>5:
                d_audio_files.clear()
                d_audio_files_name.clear() 
        elif len(dc_res)==3:
            dc_res.clear()
            d_dataid.clear()
            # qword.clear()
            # print("qword",qword)
            print(dc_res)
            print(d_dataid)
            qword.clear()
            word_ids.clear()
            d_audio_files.clear()
            d_audio_files_name.clear()
            dc_res.clear()
            d_dataid.clear()
            print(audio_file)
            audio_file.clear()  # clear the audio_file list
            print(audio_file)
            file.clear()
            if len(d_audio_files)>5:
                d_audio_files.clear()
                d_audio_files_name.clear() 
        elif len(dc_res)==2:
            dc_res.clear()
            d_dataid.clear()
            # qword.clear()
            # print("qword",qword)
            print(dc_res)
            print(d_dataid)
            qword.clear()
            word_ids.clear()
            d_audio_files.clear()
            d_audio_files_name.clear()
            dc_res.clear()
            d_dataid.clear()
            print(audio_file)
            audio_file.clear()  # clear the audio_file list
            print(audio_file)
            file.clear()
            if len(d_audio_files)>5:
                d_audio_files.clear()
                d_audio_files_name.clear() 
        elif len(dc_res)==1:
            dc_res.clear()
            d_dataid.clear()
            # qword.clear()
            # print("qword",qword)
            print(dc_res)
            print(d_dataid)
            qword.clear()
            word_ids.clear()
            d_audio_files.clear()
            d_audio_files_name.clear()
            dc_res.clear()
            d_dataid.clear()
            print(audio_file)
            audio_file.clear()  # clear the audio_file list
            print(audio_file)
            file.clear()
            if len(d_audio_files)>5:
                d_audio_files.clear()
                d_audio_files_name.clear() 
        elif len(dc_res) ==0:
            dc_res.clear()
            d_dataid.clear()
            # qword.clear()
            # print("qword",qword)
            print(dc_res)
            print(d_dataid)
            qword.clear()
            word_ids.clear()
            d_audio_files.clear()
            d_audio_files_name.clear()
            dc_res.clear()
            d_dataid.clear()
            print(audio_file)
            audio_file.clear()  # clear the audio_file list
            print(audio_file)
            file.clear()
            if len(d_audio_files)>5:
                d_audio_files.clear()
                d_audio_files_name.clear() 
        return redirect('word_recording_next')
    return render(request, 'word_start.html')

def get_random_word(request):
    word_ids = request.session.setdefault('word_ids', [])
    d_dataid = request.session.setdefault('d_dataid', [])
    

    selected_option = request.session.get('selected_option')
    # word_ids.clear()                                                                                     ##Reset
    # d_dataid.clear()                                                                                  

    print("@",selected_option)
    if selected_option == 'English':
        with open(json_eng, 'r') as f:
            data = json.load(f)                               
            data1 = random.choice(data['Word'])                            
            print("the value ",data1['id'])
            data_id = data1['id']
            while data_id in word_ids:
                data1 = random.choice(data['Word'])
                data_id = data1['id']
            
            word_ids.append(data_id)
            # word_ids.clear()

            print("word_ids",word_ids)
             

            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(word_ids) ==5:
                d_dataid = word_ids.copy()
                print(d_dataid)
                request.session['d_dataid'] = d_dataid
                word_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Hindi':
        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Word'])
            print("the value ",data1['id'])
            data_id = data1['id']
            while data_id in word_ids:
                data1 = random.choice(data['Word'])
                data_id = data1['id']
            
            word_ids.append(data_id)
            request.session['word_ids'] = word_ids

            # word_ids.clear()

            print("word_ids",word_ids)
             

            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(word_ids) ==5:
                d_dataid = word_ids.copy()
                print(d_dataid)
                request.session['d_dataid'] = d_dataid

                word_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Assamese':
        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Word'])
            print("the value ",data1['id'])
            data_id = data1['id']
            while data_id in word_ids:
                data1 = random.choice(data['Word'])
                data_id = data1['id']
            
            word_ids.append(data_id)
            # word_ids.clear()

            print("word_ids",word_ids)
             
                
            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(word_ids) ==5:
                d_dataid = word_ids.copy()
                print(d_dataid)
                request.session['d_dataid'] = d_dataid

                word_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Bengali':
        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Word'])
            print("the value ",data1['id'])
            data_id = data1['id']
            while data_id in word_ids:
                data1 = random.choice(data['Word'])
                data_id = data1['id']
            
            word_ids.append(data_id)
            # word_ids.clear()

            print("word_ids",word_ids)
             

            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(word_ids) ==5:
                d_dataid = word_ids.copy()
                print(d_dataid)
                request.session['d_dataid'] = d_dataid

                word_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Gujarati':
        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Word'])
            print("the value ",data1['id'])
            data_id = data1['id']
            while data_id in word_ids:
                data1 = random.choice(data['Word'])
                data_id = data1['id']
            
            word_ids.append(data_id)
            # word_ids.clear()

            print("word_ids",word_ids)
             

            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(word_ids) ==5:
                d_dataid = word_ids.copy()
                print(d_dataid)
                request.session['d_dataid'] = d_dataid

                word_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Marathi':
        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Word'])
            print("the value ",data1['id'])
            data_id = data1['id']
            while data_id in word_ids:
                data1 = random.choice(data['Word'])
                data_id = data1['id']
            
            word_ids.append(data_id)
            # word_ids.clear()

            print("word_ids",word_ids)
             

            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(word_ids) ==5:
                d_dataid = word_ids.copy()
                print(d_dataid)
                request.session['d_dataid'] = d_dataid

                word_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Kannada':
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Word'])
            print("the value ",data1['id'])
            data_id = data1['id']
            while data_id in word_ids:
                data1 = random.choice(data['Word'])
                data_id = data1['id']
            
            word_ids.append(data_id)
            # word_ids.clear()

            print("word_ids",word_ids)
             

            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(word_ids) ==5:
                d_dataid = word_ids.copy()
                print(d_dataid)
                request.session['d_dataid'] = d_dataid

                word_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Malayalam':
        with open(json_mal, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Word'])
            print("the value ",data1['id'])
            data_id = data1['id']
            while data_id in word_ids:
                data1 = random.choice(data['Word'])
                data_id = data1['id']
            
            word_ids.append(data_id)
            # word_ids.clear()

            print("word_ids",word_ids)
             

            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(word_ids) ==5:
                d_dataid = word_ids.copy()
                print(d_dataid)
                request.session['d_dataid'] = d_dataid

                word_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Odiya':
        with open(json_odi, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Word'])
            print("the value ",data1['id'])
            data_id = data1['id']
            while data_id in word_ids:
                data1 = random.choice(data['Word'])
                data_id = data1['id']
            
            word_ids.append(data_id)
            # word_ids.clear()

            print("word_ids",word_ids)
             

            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(word_ids) ==5:
                d_dataid = word_ids.copy()
                print(d_dataid)
                request.session['d_dataid'] = d_dataid

                word_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Punjabi':
        with open(json_pun, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Word'])
            print("the value ",data1['id'])
            data_id = data1['id']
            while data_id in word_ids:
                data1 = random.choice(data['Word'])
                data_id = data1['id']
            
            word_ids.append(data_id)
            # word_ids.clear()

            print("word_ids",word_ids)
             

            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(word_ids) ==5:
                d_dataid = word_ids.copy()
                print(d_dataid)
                request.session['d_dataid'] = d_dataid

                word_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Tamil':
        with open(json_tami, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Word'])
            print("the value ",data1['id'])
            data_id = data1['id']
            while data_id in word_ids:
                data1 = random.choice(data['Word'])
                data_id = data1['id']
            
            word_ids.append(data_id)
            # word_ids.clear()

            print("word_ids",word_ids)
             

            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(word_ids) ==5:
                d_dataid = word_ids.copy()
                print(d_dataid)
                request.session['d_dataid'] = d_dataid

                word_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Telugu':
        with open(json_tel, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Word'])
            print("the value ",data1['id'])
            data_id = data1['id']
            while data_id in word_ids:
                data1 = random.choice(data['Word'])
                data_id = data1['id']
            
            word_ids.append(data_id)
            # word_ids.clear()

            print("word_ids",word_ids)
             

            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(word_ids) ==5:
                d_dataid = word_ids.copy()
                print(d_dataid)
                request.session['d_dataid'] = d_dataid

                word_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Urdu':
        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Word'])
            print("the value ",data1['id'])
            data_id = data1['id']
            while data_id in word_ids:
                data1 = random.choice(data['Word'])
                data_id = data1['id']
            
            word_ids.append(data_id)
            # word_ids.clear()

            print("word_ids",word_ids)
             

            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(word_ids) ==5:
                d_dataid = word_ids.copy()
                print(d_dataid)
                request.session['d_dataid'] = d_dataid

                word_ids.clear()
            return data1['data'], data_id


def word_recording(request):
    d_dataid = request.session.setdefault('d_dataid', [])
    dc_res = request.session.setdefault('dc_res', [])
    # qword = request.session.setdefault('qword', [])
    # print("qword",qword)
    if len(dc_res) == 5:
        dc_res.clear()
        d_dataid.clear()
        # qword.clear()
        # print("qword",qword)


    print(d_dataid)
   
    Word, data_id = get_random_word(request)
    context = {"val": Word, "recording": True, "data_id": data_id}
    request.session['submit_id'] = context
    return render(request, "word_rec.html", context)

def word_recording_next(request):
    word_ids = request.session.setdefault('word_ids', [])

    d_dataid = request.session.setdefault('d_dataid', [])
    dc_res = request.session.setdefault('dc_res', [])
    qword = request.session.setdefault('qword', [])
    print("qword",qword)


    if len(qword)==5:
        qword.clear()
        dc_res.clear()

        print("qword",qword) 
    # if len(qword)<5:
    #     qword.clear()
    #     print("qword",qword)                                                                                                        ### Reset 
    #     word_ids.clear() 


    if len(dc_res) == 4:
        dc_res.clear()
        d_dataid.clear()
        # qword.clear()
        # print("qword",qword)
        print(d_dataid)
   
    Word, data_id = get_random_word(request)
    context = {"val": Word, "recording": True, "data_id": data_id}
    return render(request, "fifteen_one_next.html", context)



def word_skip(request):
    if request.method == 'POST':
        val = request.POST.get('val')
        skip_val = request.session.setdefault('skip_val', [])

        d_audio_files = request.session.get('d_audio_files', [])
        d_audio_files_name = request.session.get('d_audio_files_name', [])
        word_ids = request.session.get('word_ids', [])
        qword = request.session.setdefault('qword', [])

        print("d_audio_files_name",d_audio_files_name)
        print("word_ids",word_ids)
        word_ids = request.session.get('word_ids', [])
        d_audio_files_name = request.session.get('d_audio_files_name', [])

        missing_indices = [i for i, id in enumerate(word_ids) if id not in d_audio_files_name]

        # Print the missing indices
        print("The missing indices are:", missing_indices)
        for word_id in word_ids:
            audio_file = word_id + '.wav'
            if audio_file not in d_audio_files_name:
                d_audio_files_name.append(audio_file)

        # update the session variable with the new list
        for word_id in word_ids:
            wav_file = f"D:\\Parakh Final Project\\Parakh\\media\\{word_id}.wav"
            if wav_file not in d_audio_files:
                d_audio_files.append(wav_file)
                skip_val.append(wav_file)


        request.session['d_audio_files'] = d_audio_files
        request.session['skip_val'] = skip_val

        request.session['d_audio_files_name'] = d_audio_files_name
    


        print("skip_val  word_answer",skip_val)

        print("d_audio_files  word_answer",d_audio_files)


        # filepath = os.path.join(settings.MEDIA_ROOT, 'skip_word.wav')
        # if not os.path.exists(filepath):
        #     return HttpResponseBadRequest('Audio file not found')

        # print(filepath)
        selected_option = request.session.get('selected_option')
        print("@",selected_option)
        
        if selected_option == 'English':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_eng) as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        elif selected_option == 'Hindi':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_hin, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        elif selected_option == 'Assamese':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_ass, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        elif selected_option == 'Bengali':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_ben, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        elif selected_option == 'Gujarati':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_guj, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        elif selected_option == 'Marathi':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_mar, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        elif selected_option == 'Kannada':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_kan, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break

        elif selected_option == 'Malayalam':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_mal, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        elif selected_option == 'Odiya':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_odi, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        elif selected_option == 'Punjabi':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_pun, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        elif selected_option == 'Tamil':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_tami, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        elif selected_option == 'Telugu':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_tel, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        elif selected_option == 'Urdu':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_urdu, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        # data_id = request.session.get('data_id')
        # print("data_id",data_id)
        # with open(json_eng) as f:
        #     data = json.load(f)
        #     Word = None
        #     for d in data['Word']:
        #         if d['id'] == data_id:
        #             val = d['data']
        #             break
        qword = request.session.setdefault('qword', [])
        d_copy_audio_files = request.session.get('d_copy_audio_files', [])
        d_audio_files = request.session.get('d_audio_files', [])
        d_audio_files_name = request.session.setdefault('d_audio_files_name', [])
        copy_word_name = request.session.setdefault('copy_word_name', [])

        print("d_audio_files_name",d_audio_files_name)
        if len(d_audio_files)==5:
            d_copy_audio_files= d_audio_files.copy()
        if len(d_audio_files_name)==5:
            copy_word_name= d_audio_files_name.copy()
        
        print("copy_word_name",copy_word_name)
        request.session['copy_word_name'] = copy_word_name
        
        if val:
            print("the val",val)
            qword = request.session.get("qword")
            qword.append(val)
            request.session["qword"] = qword

            print("qword",qword)
            dc_res = request.session.setdefault('dc_res', [])
            if request.session.get("dc_res",None) is None:
                dc_res = []
            else:
                dc_res = request.session.get("dc_res")
        

                request.session["dc_res"] = dc_res
                dc_res.append('{"no_mistakes": 1, "no_del": 0, "del_details": "", "no_sub": 1, "sub_details": "0-\\u092a\\u0948\\u0938\\u093e:", "status": "success", "wcpm": 0.0, "text": "", "audio_url": "", "process_time": 0.47053098678588867}')

                print("testing the data", dc_res)
                if len(dc_res)==5:
                        request.session['dc_rec'] = dc_res
                        context = {'l_res': dc_res}
                        url = reverse('wans_page')
                        return redirect(url,context)
            if len(d_audio_files) == 4:
                return redirect('word_recording')
            # if len(d_audio_files)==5:
            #     return render(request, 'word_answer.html',{'qword': qword})
                
        return redirect('word_recording_next')
    # url = 'http://3.7.133.80:8000/gettranscript/'
    # files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    # payload = {'language': selected_option ,'question':val}
    # headers = {}
    # response = requests.request("POST", url, headers=headers, data=payload, files=files)

    # # lc_res=[]
    # if response.status_code == 200:

    #     dc_res = request.session.setdefault('dc_res', [])
    #     if request.session.get("dc_res",None) is None:
    #         dc_res = []
    #     else:
    #         dc_res = request.session.get("dc_res")
    #         dc_res.append(response.text)
    

    #         request.session["dc_res"] = dc_res
    #         print("testing the data", dc_res)
    #         if len(dc_res)==5:
    #                 request.session['dc_rec'] = dc_res
    #                 context = {'l_res': dc_res}
    #                 url = reverse('wans_page')
    #                 if len(dc_res)==5:           
    #                     return redirect(url,context)
    #     if len(d_audio_files) == 4:
    #         return redirect('word_recording')
            
    # return redirect('word_recording_next')

  



# def submit_word_skip(request):
#     if request.method == 'POST':
#         submit_id = request.session.get('submit_id')
#         data_id = submit_id.get('data_id')
#         word_ids = request.session.get('word_ids')
#         val = request.POST.get('val')
#         skip_val = request.session.setdefault('skip_val', [])
#         d_audio_files = request.session.get('d_audio_files', [])
#         d_audio_files_name = request.session.get('d_audio_files_name', [])

#         missing_indices = [i for i, id in enumerate(word_ids) if id not in d_audio_files_name]

#         audio_file = data_id + '.wav'
#         if audio_file not in d_audio_files_name:
#             d_audio_files_name.append(audio_file)
#             wav_file = os.path.join(base_path, f"{data_id}.wav")  # Added this line
#             d_audio_files.append(wav_file)
#             skip_val.append(wav_file)

#         request.session['d_audio_files'] = d_audio_files
#         request.session['skip_val'] = skip_val
#         request.session['d_audio_files_name'] = d_audio_files_name
#         selected_option = request.session.get('selected_option')
#         json_file = request.session.get('json_file')

#         with open(json_file, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#             Word = None
#             for d in data['Word']:
#                 if d['id'] == data_id:
#                     val = d['data']
#                     break

#         qword = request.session.setdefault('qword', [])
#         qword.append(val)
#         request.session['qword'] = qword

#         dc_res = request.session.setdefault('dc_res', [])
#         dc_res.append('{"no_mistakes": 1, "no_del": 0, "del_details": "", "no_sub": 1, "sub_details": "0-\\u092a\\u0948\\u0938\\u093e:", "status": "success", "wcpm": 0.0, "text": "", "audio_url": "", "process_time": 0.47053098678588867}')
#         request.session['dc_res'] = dc_res

#         if len(dc_res) == 5:
#             request.session['dc_rec'] = dc_res
#             context = {'l_res': dc_res}
#             url = reverse('wans_page')
#             return redirect(url, context)

#         if len(d_audio_files) == 4:
#             return redirect('word_recording')

#     return redirect('word_recording_next')

  
def submit_word_skip(request):
     if request.method == 'POST':
        submit_id = request.session.get('submit_id')
        print(submit_id)
        data_id = submit_id.get('data_id')
        print('data_id:', data_id)
        word_ids = request.session.get('word_ids')
        print("word_ids_on skip submit", word_ids)
        val = request.POST.get('val')
        skip_val = request.session.setdefault('skip_val', [])

        d_audio_files = request.session.get('d_audio_files', [])
        d_audio_files_name = request.session.get('d_audio_files_name', [])
        word_ids = request.session.get('word_ids', [])
        qword = request.session.setdefault('qword', [])

        print("d_audio_files_name",d_audio_files_name)
        print("word_ids next",word_ids)

        # word_ids = request.session.get('word_ids', [])
        d_audio_files_name = request.session.get('d_audio_files_name', [])

        missing_indices = [i for i, id in enumerate(word_ids) if id not in d_audio_files_name]

        # Print the missing indices
        print("The missing indices are:", missing_indices)
        # for word_id in word_ids:
        audio_file = data_id + '.wav'
        if audio_file not in d_audio_files_name:
            d_audio_files_name.append(audio_file)

        # update the session variable with the new list
        # for data_id in data_ids:
        # wav_file = f"D:\\Parakh Final Project\\Parakh\\media\\{data_id}.wav"
        wav_file = os.path.join(base_path, f"{data_id}.wav")

        if wav_file not in d_audio_files:
            d_audio_files.append(wav_file)
            skip_val.append(wav_file)


        request.session['d_audio_files'] = d_audio_files
        request.session['skip_val'] = skip_val

        request.session['d_audio_files_name'] = d_audio_files_name
    


        print("skip_val  word_answer",skip_val)

        print("d_audio_files  word_answer",d_audio_files)


        # filepath = os.path.join(settings.MEDIA_ROOT, 'skip_word.wav')
        # if not os.path.exists(filepath):
        #     return HttpResponseBadRequest('Audio file not found')

        # print(filepath)
        selected_option = request.session.get('selected_option')
        print("@",selected_option)
        
        if selected_option == 'English':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_eng) as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        elif selected_option == 'Hindi':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_hin, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        elif selected_option == 'Assamese':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_ass, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        elif selected_option == 'Bengali':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_ben, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        elif selected_option == 'Gujarati':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_guj, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        elif selected_option == 'Marathi':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_mar, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        elif selected_option == 'Kannada':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_kan, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break

        elif selected_option == 'Malayalam':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_mal, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        elif selected_option == 'Odiya':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_odi, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        elif selected_option == 'Punjabi':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_pun, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        elif selected_option == 'Tamil':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_tami, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        elif selected_option == 'Telugu':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_tel, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        elif selected_option == 'Urdu':
            data_id = request.session.get('data_id')
            print("data_id",data_id)
            with open(json_urdu, 'r', encoding='utf-8') as f:
                data = json.load(f)
                Word = None
                for d in data['Word']:
                    if d['id'] == data_id:
                        val = d['data']
                        break
        # data_id = request.session.get('data_id')
        # print("data_id",data_id)
        # with open(json_eng) as f:
        #     data = json.load(f)
        #     Word = None
        #     for d in data['Word']:
        #         if d['id'] == data_id:
        #             val = d['data']
        #             break
        qword = request.session.setdefault('qword', [])
        d_copy_audio_files = request.session.get('d_copy_audio_files', [])
        d_audio_files = request.session.get('d_audio_files', [])

        d_audio_files_name = request.session.setdefault('d_audio_files_name', [])
        copy_word_name = request.session.setdefault('copy_word_name', [])

        print("d_audio_files_name",d_audio_files_name)
        if len(d_audio_files)==5:
            d_copy_audio_files= d_audio_files.copy()
        if len(d_audio_files_name)==5:
            copy_word_name= d_audio_files_name.copy()
        
        print("copy_word_name",copy_word_name)
        request.session['copy_word_name'] = copy_word_name
        
        if val:
            print("the val",val)
            qword = request.session.get("qword")
            qword.append(val)
            request.session["qword"] = qword

            print("qword",qword)
            dc_res = request.session.setdefault('dc_res', [])
            if request.session.get("dc_res",None) is None:
                dc_res = []
            else:
                dc_res = request.session.get("dc_res")
        

                request.session["dc_res"] = dc_res
                dc_res.append('{"no_mistakes": 1, "no_del": 0, "del_details": "", "no_sub": 1, "sub_details": "0-\\u092a\\u0948\\u0938\\u093e:", "status": "success", "wcpm": 0.0, "text": "", "audio_url": "", "process_time": 0.47053098678588867}')

                print("testing the data", dc_res)
                if len(dc_res)==5:
                        request.session['dc_rec'] = dc_res
                        context = {'l_res': dc_res}
                        url = reverse('wans_page')
                        return redirect(url,context)
            if len(d_audio_files) == 4:
                return redirect('word_recording')
            # if len(d_audio_files)==5:
            #     return render(request, 'word_answer.html',{'qword': qword})
                
        return redirect('word_recording_next')
   

@csrf_exempt
def save_word(request):
    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        filename = f'{data_id}.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
        
        request.session['filepath'] = filepath
        return render(request, 'word_rec.html', {'audio_url': filepath})

def word_answer(request):
   
    d_audio_files = request.session.setdefault('d_audio_files', [])
    print("d_audio_files  word_answer",d_audio_files)


    filepath = request.session.get('filepath')
    print(filepath)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    
    if selected_option == 'English':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_eng) as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Hindi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Assamese':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Bengali':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Gujarati':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Marathi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Kannada':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == data_id:
                    val = d['data']
                    break

    elif selected_option == 'Malayalam':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_mal, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Odiya':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_odi, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Punjabi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_pun, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Tamil':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_tami, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Telugu':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_tel, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Urdu':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    # data_id = request.session.get('data_id')
    # print("data_id",data_id)
    # with open(json_eng) as f:
    #     data = json.load(f)
    #     Word = None
    #     for d in data['Word']:
    #         if d['id'] == data_id:
    #             val = d['data']
    #             break
    qword = request.session.setdefault('qword', [])
    word_ids = request.session.setdefault('word_ids', [])
    
    if val:
        print("the val",val)
        qword = request.session.get("qword")
        qword.append(val)
        request.session["qword"] = qword

        print("qword",qword)
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': selected_option ,'question':val}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    # lc_res=[]
    if response.status_code == 200:
        word_ids = request.session.get('word_ids', [])


        dc_res = request.session.setdefault('dc_res', [])
        if request.session.get("dc_res",None) is None:
            dc_res = []
        else:
            dc_res = request.session.get("dc_res")
            dc_res.append(response.text)
            # dc_res.clear()                                                                                           ##   Reset 

            request.session["dc_res"] = dc_res
            print("testing the data", dc_res)
            word_ids = request.session.get('word_ids', [])

            print("word/-ids",word_ids )
            if len(qword)==5:
                    request.session['dc_rec'] = dc_res
                    context = {'l_res': dc_res}
                    url = reverse('wans_page')
                    if len(qword)==5:           
                        return redirect(url,context)
        if len(qword) == 4:
            return redirect('word_recording')
            
    return redirect('word_recording_next')

# @csrf_exempt
# def save_word(request):
#     d_audio_files = request.session.setdefault('d_audio_files', [])
#     d_audio_files_name = request.session.setdefault('d_audio_files_name', [])
    
#     if request.method == 'POST' and request.FILES.get('audio_blob'):
  
#         if len(d_audio_files)>5:
#             d_audio_files.clear()
#             d_audio_files_name.clear()  
#         data_id = request.session.get('data_id')
#         val = request.POST.get('val')
#         print(val)
#         filename = f'{data_id}.wav'
#         media_folder = os.path.join(settings.MEDIA_ROOT)
#         os.makedirs(media_folder, exist_ok=True)
#         filepath = os.path.join(media_folder, filename)
#         with open(os.path.join(media_folder, filename), 'wb') as audio_file:
#             audio_file.write(request.FILES['audio_blob'].read())
#         d_audio_files.append(filepath)
#         d_audio_files_name.append(filename)
#         print("###",d_audio_files)
#         # if len(d_audio_files)<5:
#         #     d_audio_files.clear()
#         #     d_audio_files_name.clear()                                                                                                  ### Reset

#         request.session['filepath'] = filepath
#         return render(request, 'word_rec.html', { 'audio_url': filepath})

    
# def word_answer(request):
   
#     d_audio_files = request.session.setdefault('d_audio_files', [])
#     print("d_audio_files  word_answer",d_audio_files)

#     filepath = request.session.get('filepath')
#     print(filepath)
#     selected_option = request.session.get('selected_option')
#     print("@",selected_option)
    
#     if selected_option == 'English':
#         data_id = request.session.get('data_id')
#         print("data_id",data_id)
#         with open(json_eng) as f:
#             data = json.load(f)
#             Word = None
#             for d in data['Word']:
#                 if d['id'] == data_id:
#                     val = d['data']
#                     break
#     elif selected_option == 'Hindi':
#         data_id = request.session.get('data_id')
#         print("data_id",data_id)
#         with open(json_hin, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#             Word = None
#             for d in data['Word']:
#                 if d['id'] == data_id:
#                     val = d['data']
#                     break
#     elif selected_option == 'Assamese':
#         data_id = request.session.get('data_id')
#         print("data_id",data_id)
#         with open(json_ass, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#             Word = None
#             for d in data['Word']:
#                 if d['id'] == data_id:
#                     val = d['data']
#                     break
#     elif selected_option == 'Bengali':
#         data_id = request.session.get('data_id')
#         print("data_id",data_id)
#         with open(json_ben, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#             Word = None
#             for d in data['Word']:
#                 if d['id'] == data_id:
#                     val = d['data']
#                     break
#     elif selected_option == 'Gujarati':
#         data_id = request.session.get('data_id')
#         print("data_id",data_id)
#         with open(json_guj, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#             Word = None
#             for d in data['Word']:
#                 if d['id'] == data_id:
#                     val = d['data']
#                     break
#     elif selected_option == 'Marathi':
#         data_id = request.session.get('data_id')
#         print("data_id",data_id)
#         with open(json_mar, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#             Word = None
#             for d in data['Word']:
#                 if d['id'] == data_id:
#                     val = d['data']
#                     break
#     elif selected_option == 'Kannada':
#         data_id = request.session.get('data_id')
#         print("data_id",data_id)
#         with open(json_kan, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#             Word = None
#             for d in data['Word']:
#                 if d['id'] == data_id:
#                     val = d['data']
#                     break

#     elif selected_option == 'Malayalam':
#         data_id = request.session.get('data_id')
#         print("data_id",data_id)
#         with open(json_mal, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#             Word = None
#             for d in data['Word']:
#                 if d['id'] == data_id:
#                     val = d['data']
#                     break
#     elif selected_option == 'Odiya':
#         data_id = request.session.get('data_id')
#         print("data_id",data_id)
#         with open(json_odi, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#             Word = None
#             for d in data['Word']:
#                 if d['id'] == data_id:
#                     val = d['data']
#                     break
#     elif selected_option == 'Punjabi':
#         data_id = request.session.get('data_id')
#         print("data_id",data_id)
#         with open(json_pun, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#             Word = None
#             for d in data['Word']:
#                 if d['id'] == data_id:
#                     val = d['data']
#                     break
#     elif selected_option == 'Tamil':
#         data_id = request.session.get('data_id')
#         print("data_id",data_id)
#         with open(json_tami, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#             Word = None
#             for d in data['Word']:
#                 if d['id'] == data_id:
#                     val = d['data']
#                     break
#     elif selected_option == 'Telugu':
#         data_id = request.session.get('data_id')
#         print("data_id",data_id)
#         with open(json_tel, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#             Word = None
#             for d in data['Word']:
#                 if d['id'] == data_id:
#                     val = d['data']
#                     break
#     elif selected_option == 'Urdu':
#         data_id = request.session.get('data_id')
#         print("data_id",data_id)
#         with open(json_urdu, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#             Word = None
#             for d in data['Word']:
#                 if d['id'] == data_id:
#                     val = d['data']
#                     break
#     # data_id = request.session.get('data_id')
#     # print("data_id",data_id)
#     # with open(json_eng) as f:
#     #     data = json.load(f)
#     #     Word = None
#     #     for d in data['Word']:
#     #         if d['id'] == data_id:
#     #             val = d['data']
#     #             break
#     qword = request.session.setdefault('qword', [])
#     word_ids = request.session.setdefault('word_ids', [])
    
#     if val:
#         print("the val",val)
#         qword = request.session.get("qword")
#         qword.append(val)
#         request.session["qword"] = qword

#         print("qword",qword)
#     url = 'http://3.7.133.80:8000/gettranscript/'
#     files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
#     payload = {'language': selected_option ,'question':val}
#     headers = {}
#     response = requests.request("POST", url, headers=headers, data=payload, files=files)

#     # lc_res=[]
#     if response.status_code == 200:
#         word_ids = request.session.get('word_ids', [])


#         dc_res = request.session.setdefault('dc_res', [])
#         if request.session.get("dc_res",None) is None:
#             dc_res = []
#         else:
#             dc_res = request.session.get("dc_res")
#             dc_res.append(response.text)
#             # dc_res.clear()                                                                                           ##   Reset 

#             request.session["dc_res"] = dc_res
#             print("testing the data", dc_res)
#             word_ids = request.session.get('word_ids', [])

#             print("word/-ids",word_ids )
#             if len(qword)==5:
#                     request.session['dc_rec'] = dc_res
#                     context = {'l_res': dc_res}
#                     url = reverse('wans_page')
#                     if len(qword)==5:           
#                         return redirect(url,context)
#         if len(qword) == 4:
#             return redirect('word_recording')
            
#     return redirect('word_recording_next')

  



def wans_page(request):
    d_copy_audio_files = request.session.get('d_copy_audio_files', [])
    d_audio_files = request.session.get('d_audio_files', [])
    
    print("d_audio_files",d_audio_files)
    d_audio_files_name = request.session.setdefault('d_audio_files_name', [])
    copy_word_name = request.session.setdefault('copy_word_name', [])
    skip_val = request.session.setdefault('skip_val', [])
    print("skip", skip_val)

    print("d_audio_files_name",d_audio_files_name)
    if len(d_audio_files)==5:
        d_copy_audio_files= d_audio_files.copy()
    if len(d_audio_files_name)==5:
        copy_word_name= d_audio_files_name.copy()
    if len(d_audio_files)==4:
        d_copy_audio_files= d_audio_files.copy()
    if len(d_audio_files_name)==4:
        copy_word_name= d_audio_files_name.copy()
    
    print("copy_word_name",copy_word_name)
    request.session['copy_word_name'] = copy_word_name
    # skip_val = request.session['skip_val']
    # print('skip_val',skip_val)
    print('d_copy_audio_files',d_copy_audio_files)
    


    audio_urls = []
    if d_copy_audio_files:
        for filepath in d_copy_audio_files:
            if os.path.exists(filepath):
                filename = os.path.basename(filepath)
                audio_url = request.build_absolute_uri(settings.MEDIA_URL + filename)
                audio_urls.append(audio_url)
            else:
                audio_urls.append('')  # Add a blank entry if filepath doesn't exist

       
                # d_copy_audio_files.remove(file_path)
        request.session['d_copy_audio_files'] = d_copy_audio_files

    
    text = []
    mis=[]
    wcpm=[]
    dc_res=[]

    dc_res = request.session.setdefault('dc_res', [])
    qword = request.session.setdefault('qword', [])


    for item in dc_res:
        # text.append(eval(item)['text'])
        mis.append(eval(item)['no_mistakes'])
        wcpm.append(eval(item)['wcpm'])
    total_wcpm = sum(wcpm) 
    total_mis = sum(mis)
    # print("total",total_wcpm)
    print("qword",qword)
    print('audio_urls', audio_urls)
    context = {
    'qword': qword,
    'mis': mis,
    'flu': wcpm,
    'd_copy_audio_files': d_copy_audio_files,
    'audio_url1': audio_urls[0],
    'audio_url2': audio_urls[1],
    'audio_url3': audio_urls[2],
    'audio_url4': audio_urls[3],
    'audio_url5': audio_urls[4],
    'total_mis': total_mis
}
    # if len(d_audio_files)==5:
    #     d_audio_files.clear()
    #     d_audio_files_name.clear()
    return render(request, 'word_answer.html', context)

#new function
def next_word(request):
    d_dataid = request.session.setdefault('d_dataid', [])
    copy_word_name = request.session.setdefault('copy_word_name', [])

    if request.method == "POST":
        copy_word_name = request.session.get('copy_word_name', [])
        copy_word_name = request.session.setdefault('copy_word_name', [])
        d_dataid = request.session.get('d_dataid', [])
        print("^^^", d_dataid)

        if "record" in request.POST:
            request.session['d_dataid[0]'] = d_dataid[0]
            filename = d_dataid[0] + '.wav'
            media_folder = os.path.join(settings.MEDIA_ROOT)
            file_path = os.path.join(media_folder, filename)

            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"File '{filename}' has been deleted.")
                else:
                    print(f"File '{filename}' does not exist.")
            except Exception as e:
                print(f"An error occurred while deleting the file: {e}")

            selected_option = request.session.get('selected_option')
            print("@", selected_option)

            language_files = {
                'English': json_eng,
                'Hindi': json_hin,
                'Assamese': json_ass,
                'Bengali': json_ben
            }

            if selected_option in language_files:
                json_file = request.session.get('json_file')
                # json_file = language_files[selected_option]
                print("d_dataid0", d_dataid[0])
                request.session['d_dataid[0]'] = d_dataid[0]
                request.session['audio_recorded'] = True


                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Word = None
                    for d in data['Word']:
                        if d['id'] == d_dataid[0]:
                            val = d['data']
                            break
                    if val:
                        print("the val", val)

                return render(request, "retake_word/retake_word1.html", {"recording": True, "val": val})


# def next_word(request):
#     d_dataid = request.session.setdefault('d_dataid', [])
#     copy_word_name = request.session.setdefault('copy_word_name', [])
#     if request.method == "POST":
#         copy_word_name = request.session.get('copy_word_name')

#         copy_word_name = request.session.setdefault('copy_word_name', [])
       

#         # print("copy_word_name",copy_word_name)
#         # for filename in copy_word_name:
#         #     filename_without_extension = filename.split(".")[0]
#         #     d_dataid.append(filename_without_extension)
       
#         d_dataid = request.session.get('d_dataid', [])

#         print("^^^",d_dataid)
#         if "record" in request.POST:
#             request.session['d_dataid[0]'] = d_dataid[0]

#             filename = d_dataid[0] + '.wav'
#             media_folder = os.path.join(settings.MEDIA_ROOT)
#             file_path = os.path.join(media_folder, filename)

#             try:
#                 if os.path.isfile(file_path):
#                     os.remove(file_path)
#                     print(f"File '{filename}' has been deleted.")
#                 else:
#                     print(f"File '{filename}' does not exist.")
#             except Exception as e:
#                 print(f"An error occurred while deleting the file: {e}")

           
#             selected_option = request.session.get('selected_option')
#             print("@",selected_option)
            
#             if selected_option == 'English':
#                 # data_id = request.session.get('data_id')
#                 # print("data_id",data_id)
#                 # with open(json_eng) as f:
#                 #     data = json.load(f)
#                 #     Word = None
#                 #     for d in data['Word']:
#                 #         if d['id'] == data_id:
#                 #             val = d['data']
#                 #             break
#                 print("d_dataid0",d_dataid[0])
#                 request.session['d_dataid[0]'] = d_dataid[0]

#                 request.session['audio_recorded'] = True
                
#                 with open(json_eng) as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[0]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
                    

#                     return render(request, "retake_word/retake_word1.html", {"recording": True,"val":val })
#             elif selected_option == 'Hindi':
#                 # data_id = request.session.get('data_id')
#                 # print("data_id",data_id)
#                 # with open(json_eng) as f:
#                 #     data = json.load(f)
#                 #     Word = None
#                 #     for d in data['Word']:
#                 #         if d['id'] == data_id:
#                 #             val = d['data']
#                 #             break
#                 print("d_dataid0",d_dataid[0])
#                 request.session['d_dataid[0]'] = d_dataid[0]

#                 request.session['audio_recorded'] = True
                
#                 with open(json_hin, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[0]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
                    

#                     return render(request, "retake_word/retake_word1.html", {"recording": True,"val":val })
#             elif selected_option == 'Assamese':
#                 print("d_dataid0",d_dataid[0])
#                 request.session['d_dataid[0]'] = d_dataid[0]
#                 request.session['audio_recorded'] = True               
#                 with open(json_ass, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[0]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word1.html", {"recording": True,"val":val })
#             elif selected_option == 'Bengali':
#                 print("d_dataid0",d_dataid[0])
#                 request.session['d_dataid[0]'] = d_dataid[0]

#                 request.session['audio_recorded'] = True
                
#                 with open(json_ben, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[0]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word1.html", {"recording": True,"val":val })
#             elif selected_option == 'Gujarati':
#                 print("d_dataid0",d_dataid[0])
#                 request.session['d_dataid[0]'] = d_dataid[0]
#                 request.session['audio_recorded'] = True
#                 with open(json_guj, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[0]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word1.html", {"recording": True,"val":val })
#             elif selected_option == 'Marathi':
#                 print("d_dataid0",d_dataid[0])
#                 request.session['d_dataid[0]'] = d_dataid[0]
#                 request.session['audio_recorded'] = True
#                 with open(json_mar, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[0]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word1.html", {"recording": True,"val":val })
#             elif selected_option == 'Kannada':
#                 print("d_dataid0",d_dataid[0])
#                 request.session['d_dataid[0]'] = d_dataid[0]
#                 request.session['audio_recorded'] = True
#                 with open(json_kan, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[0]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word1.html", {"recording": True,"val":val })
#             elif selected_option == 'Malayalam':
#                 print("d_dataid0",d_dataid[0])
#                 request.session['d_dataid[0]'] = d_dataid[0]
#                 request.session['audio_recorded'] = True
#                 with open(json_mal, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[0]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word1.html", {"recording": True,"val":val })
#             elif selected_option == 'Odiya':
#                 print("d_dataid0",d_dataid[0])
#                 request.session['d_dataid[0]'] = d_dataid[0]
#                 request.session['audio_recorded'] = True
#                 with open(json_odi, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[0]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word1.html", {"recording": True,"val":val })
#             elif selected_option == 'Punjabi':
#                 print("d_dataid0",d_dataid[0])
#                 request.session['d_dataid[0]'] = d_dataid[0]
#                 request.session['audio_recorded'] = True
#                 with open(json_pun, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[0]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word1.html", {"recording": True,"val":val })
#             elif selected_option == 'Tamil':
#                 print("d_dataid0",d_dataid[0])
#                 request.session['d_dataid[0]'] = d_dataid[0]
#                 request.session['audio_recorded'] = True
#                 with open(json_tami, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[0]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word1.html", {"recording": True,"val":val })
#             elif selected_option == 'Telugu':
#                 print("d_dataid0",d_dataid[0])
#                 request.session['d_dataid[0]'] = d_dataid[0]
#                 request.session['audio_recorded'] = True
#                 with open(json_tel, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[0]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word1.html", {"recording": True,"val":val })
#             elif selected_option == 'Urdu':
#                 print("d_dataid0",d_dataid[0])
#                 request.session['d_dataid[0]'] = d_dataid[0]
#                 request.session['audio_recorded'] = True
#                 with open(json_urdu, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[0]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word1.html", {"recording": True,"val":val })

#         elif "record2" in request.POST:
           
#             selected_option = request.session.get('selected_option')
#             print("@",selected_option)
#             request.session['d_dataid[1]'] = d_dataid[1]

#             filename = d_dataid[1] + '.wav'
#             media_folder = os.path.join(settings.MEDIA_ROOT)
#             file_path = os.path.join(media_folder, filename)

#             try:
#                 if os.path.isfile(file_path):
#                     os.remove(file_path)
#                     print(f"File '{filename}' has been deleted.")
#                 else:
#                     print(f"File '{filename}' does not exist.")
#             except Exception as e:
#                 print(f"An error occurred while deleting the file: {e}")
            
#             if selected_option == 'English':
#                 print("d_dataid0",d_dataid[1])
#                 request.session['d_dataid[1]'] = d_dataid[1]
#                 request.session['audio_recorded'] = True
#                 with open(json_eng) as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[1]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word2.html", {"recording": True,"val":val })
#             elif selected_option == 'Hindi':
#                 print("d_dataid1",d_dataid[1])
#                 request.session['d_dataid[1]'] = d_dataid[1]
#                 request.session['audio_recorded'] = True
#                 with open(json_hin, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[1]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word2.html", {"recording": True,"val":val })
#             elif selected_option == 'Assamese':
#                 print("d_dataid1",d_dataid[1])
#                 request.session['d_dataid[1]'] = d_dataid[1]
#                 request.session['audio_recorded'] = True
#                 with open(json_ass, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[1]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word2.html", {"recording": True,"val":val })
#             elif selected_option == 'Bengali':
#                 print("d_dataid1",d_dataid[1])
#                 request.session['d_dataid[1]'] = d_dataid[1]
#                 request.session['audio_recorded'] = True
#                 with open(json_ben, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[1]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word2.html", {"recording": True,"val":val })
#             elif selected_option == 'Gujarati':
#                 print("d_dataid1",d_dataid[1])
#                 request.session['d_dataid[1]'] = d_dataid[1]
#                 request.session['audio_recorded'] = True
#                 with open(json_guj, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[1]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word2.html", {"recording": True,"val":val })
#             elif selected_option == 'Marathi':
#                 print("d_dataid1",d_dataid[1])
#                 request.session['d_dataid[1]'] = d_dataid[1]
#                 request.session['audio_recorded'] = True
#                 with open(json_mar, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[1]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word2.html", {"recording": True,"val":val })
#             elif selected_option == 'Kannada':
#                 print("d_dataid1",d_dataid[1])
#                 request.session['d_dataid[1]'] = d_dataid[1]
#                 request.session['audio_recorded'] = True
#                 with open(json_kan, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[1]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word2.html", {"recording": True,"val":val })
#             elif selected_option == 'Malayalam':
#                 print("d_dataid1",d_dataid[1])
#                 request.session['d_dataid[1]'] = d_dataid[1]
#                 request.session['audio_recorded'] = True
#                 with open(json_mal, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[1]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word2.html", {"recording": True,"val":val })
#             elif selected_option == 'Odiya':
#                 print("d_dataid1",d_dataid[1])
#                 request.session['d_dataid[1]'] = d_dataid[1]
#                 request.session['audio_recorded'] = True
#                 with open(json_odi, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[1]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word2.html", {"recording": True,"val":val })
#             elif selected_option == 'Punjabi':
#                 print("d_dataid1",d_dataid[1])
#                 request.session['d_dataid[1]'] = d_dataid[1]
#                 request.session['audio_recorded'] = True
#                 with open(json_pun, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[1]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word2.html", {"recording": True,"val":val })
#             elif selected_option == 'Tamil':
#                 print("d_dataid1",d_dataid[1])
#                 request.session['d_dataid[1]'] = d_dataid[1]
#                 request.session['audio_recorded'] = True
#                 with open(json_tami, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[1]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word2.html", {"recording": True,"val":val })
#             elif selected_option == 'Telugu':
#                 print("d_dataid1",d_dataid[1])
#                 request.session['d_dataid[1]'] = d_dataid[1]
#                 request.session['audio_recorded'] = True
#                 with open(json_tel, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[1]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word2.html", {"recording": True,"val":val })
#             elif selected_option == 'Urdu':
#                 print("d_dataid1",d_dataid[1])
#                 request.session['d_dataid[1]'] = d_dataid[1]
#                 request.session['audio_recorded'] = True
#                 with open(json_urdu, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[1]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word2.html", {"recording": True,"val":val })

#         elif "record3" in request.POST:
#             selected_option = request.session.get('selected_option')
#             print("@",selected_option)
#             request.session['d_dataid[2]'] = d_dataid[2]

#             filename = d_dataid[2] + '.wav'
#             media_folder = os.path.join(settings.MEDIA_ROOT)
#             file_path = os.path.join(media_folder, filename)

#             try:
#                 if os.path.isfile(file_path):
#                     os.remove(file_path)
#                     print(f"File '{filename}' has been deleted.")
#                 else:
#                     print(f"File '{filename}' does not exist.")
#             except Exception as e:
#                 print(f"An error occurred while deleting the file: {e}")
#             if selected_option == 'English':
#                 print("d_dataid0",d_dataid[2])
#                 request.session['d_dataid[2]'] = d_dataid[2]
#                 request.session['audio_recorded'] = True
#                 with open(json_eng) as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[2]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word3.html", {"recording": True,"val":val })
#             elif selected_option == 'Hindi':
#                 print("d_dataid2",d_dataid[2])
#                 request.session['d_dataid[2]'] = d_dataid[2]
#                 request.session['audio_recorded'] = True
#                 with open(json_hin, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[2]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word3.html", {"recording": True,"val":val })
#             elif selected_option == 'Assamese':
#                 print("d_dataid1",d_dataid[2])
#                 request.session['d_dataid[2]'] = d_dataid[2]
#                 request.session['audio_recorded'] = True
#                 with open(json_ass, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[2]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word3.html", {"recording": True,"val":val })
#             elif selected_option == 'Bengali':
#                 print("d_dataid2",d_dataid[2])
#                 request.session['d_dataid[2]'] = d_dataid[2]
#                 request.session['audio_recorded'] = True
#                 with open(json_ben, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[2]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word3.html", {"recording": True,"val":val })
#             elif selected_option == 'Gujarati':
#                 print("d_dataid2",d_dataid[2])
#                 request.session['d_dataid[2]'] = d_dataid[2]
#                 request.session['audio_recorded'] = True
#                 with open(json_guj, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[2]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word3.html", {"recording": True,"val":val })
#             elif selected_option == 'Marathi':
#                 print("d_dataid2",d_dataid[2])
#                 request.session['d_dataid[2]'] = d_dataid[2]
#                 request.session['audio_recorded'] = True
#                 with open(json_mar, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[2]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word3.html", {"recording": True,"val":val })
#             elif selected_option == 'Kannada':
#                 print("d_dataid2",d_dataid[2])
#                 request.session['d_dataid[2]'] = d_dataid[2]
#                 request.session['audio_recorded'] = True
#                 with open(json_kan, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[2]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word3.html", {"recording": True,"val":val })
#             elif selected_option == 'Malayalam':
#                 print("d_dataid2",d_dataid[2])
#                 request.session['d_dataid[2]'] = d_dataid[2]
#                 request.session['audio_recorded'] = True
#                 with open(json_mal, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[2]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word3.html", {"recording": True,"val":val })
#             elif selected_option == 'Odiya':
#                 print("d_dataid2",d_dataid[2])
#                 request.session['d_dataid[2]'] = d_dataid[2]
#                 request.session['audio_recorded'] = True
#                 with open(json_odi, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[2]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word3.html", {"recording": True,"val":val })
#             elif selected_option == 'Punjabi':
#                 print("d_dataid2",d_dataid[2])
#                 request.session['d_dataid[2]'] = d_dataid[2]
#                 request.session['audio_recorded'] = True
#                 with open(json_pun, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[2]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word3.html", {"recording": True,"val":val })
#             elif selected_option == 'Tamil':
#                 print("d_dataid2",d_dataid[2])
#                 request.session['d_dataid[2]'] = d_dataid[2]
#                 request.session['audio_recorded'] = True
#                 with open(json_tami, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[2]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word3.html", {"recording": True,"val":val })
#             elif selected_option == 'Telugu':
#                 print("d_dataid2",d_dataid[2])
#                 request.session['d_dataid[2]'] = d_dataid[2]
#                 request.session['audio_recorded'] = True
#                 with open(json_tel, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[2]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word3.html", {"recording": True,"val":val })
#             elif selected_option == 'Urdu':
#                 print("d_dataid2",d_dataid[2])
#                 request.session['d_dataid[2]'] = d_dataid[2]
#                 request.session['audio_recorded'] = True
#                 with open(json_urdu, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[2]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word3.html", {"recording": True,"val":val })

#         elif "record4" in request.POST:
#             selected_option = request.session.get('selected_option')
#             print("@",selected_option)
#             request.session['d_dataid[3]'] = d_dataid[3]

#             filename = d_dataid[3] + '.wav'
#             media_folder = os.path.join(settings.MEDIA_ROOT)
#             file_path = os.path.join(media_folder, filename)

#             try:
#                 if os.path.isfile(file_path):
#                     os.remove(file_path)
#                     print(f"File '{filename}' has been deleted.")
#                 else:
#                     print(f"File '{filename}' does not exist.")
#             except Exception as e:
#                 print(f"An error occurred while deleting the file: {e}")
            
#             if selected_option == 'English':
#                 print("d_dataid0",d_dataid[3])
#                 request.session['d_dataid[3]'] = d_dataid[3]
#                 request.session['audio_recorded'] = True
#                 with open(json_eng) as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[3]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word4.html", {"recording": True,"val":val })
#             elif selected_option == 'Hindi':
#                 print("d_dataid3",d_dataid[3])
#                 request.session['d_dataid[3]'] = d_dataid[3]
#                 request.session['audio_recorded'] = True
#                 with open(json_hin, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[3]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word4.html", {"recording": True,"val":val })
#             elif selected_option == 'Assamese':
#                 print("d_dataid1",d_dataid[3])
#                 request.session['d_dataid[3]'] = d_dataid[3]
#                 request.session['audio_recorded'] = True
#                 with open(json_ass, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[3]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word4.html", {"recording": True,"val":val })
#             elif selected_option == 'Bengali':
#                 print("d_dataid3",d_dataid[3])
#                 request.session['d_dataid[3]'] = d_dataid[3]
#                 request.session['audio_recorded'] = True
#                 with open(json_ben, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[3]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word4.html", {"recording": True,"val":val })
#             elif selected_option == 'Gujarati':
#                 print("d_dataid3",d_dataid[3])
#                 request.session['d_dataid[3]'] = d_dataid[3]
#                 request.session['audio_recorded'] = True
#                 with open(json_guj, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[3]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word4.html", {"recording": True,"val":val })
#             elif selected_option == 'Marathi':
#                 print("d_dataid3",d_dataid[3])
#                 request.session['d_dataid[3]'] = d_dataid[3]
#                 request.session['audio_recorded'] = True
#                 with open(json_mar, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[3]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word4.html", {"recording": True,"val":val })
#             elif selected_option == 'Kannada':
#                 print("d_dataid3",d_dataid[3])
#                 request.session['d_dataid[3]'] = d_dataid[3]
#                 request.session['audio_recorded'] = True
#                 with open(json_kan, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[3]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word4.html", {"recording": True,"val":val })
#             elif selected_option == 'Malayalam':
#                 print("d_dataid3",d_dataid[3])
#                 request.session['d_dataid[3]'] = d_dataid[3]
#                 request.session['audio_recorded'] = True
#                 with open(json_mal, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[3]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word4.html", {"recording": True,"val":val })
#             elif selected_option == 'Odiya':
#                 print("d_dataid3",d_dataid[3])
#                 request.session['d_dataid[3]'] = d_dataid[3]
#                 request.session['audio_recorded'] = True
#                 with open(json_odi, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[3]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word4.html", {"recording": True,"val":val })
#             elif selected_option == 'Punjabi':
#                 print("d_dataid3",d_dataid[3])
#                 request.session['d_dataid[3]'] = d_dataid[3]
#                 request.session['audio_recorded'] = True
#                 with open(json_pun, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[3]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word4.html", {"recording": True,"val":val })
#             elif selected_option == 'Tamil':
#                 print("d_dataid3",d_dataid[3])
#                 request.session['d_dataid[3]'] = d_dataid[3]
#                 request.session['audio_recorded'] = True
#                 with open(json_tami, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[3]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word4.html", {"recording": True,"val":val })
#             elif selected_option == 'Telugu':
#                 print("d_dataid3",d_dataid[3])
#                 request.session['d_dataid[3]'] = d_dataid[3]
#                 request.session['audio_recorded'] = True
#                 with open(json_tel, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[3]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word4.html", {"recording": True,"val":val })
#             elif selected_option == 'Urdu':
#                 print("d_dataid3",d_dataid[3])
#                 request.session['d_dataid[3]'] = d_dataid[3]
#                 request.session['audio_recorded'] = True
#                 with open(json_urdu, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[3]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word4.html", {"recording": True,"val":val })
        
#         elif "record5" in request.POST:
#             selected_option = request.session.get('selected_option')
#             print("@",selected_option)
#             request.session['d_dataid[4]'] = d_dataid[4]

#             filename = d_dataid[4] + '.wav'
#             media_folder = os.path.join(settings.MEDIA_ROOT)
#             file_path = os.path.join(media_folder, filename)

#             try:
#                 if os.path.isfile(file_path):
#                     os.remove(file_path)
#                     print(f"File '{filename}' has been deleted.")
#                 else:
#                     print(f"File '{filename}' does not exist.")
#             except Exception as e:
#                 print(f"An error occurred while deleting the file: {e}")
            
#             if selected_option == 'English':
#                 print("d_dataid0",d_dataid[4])
#                 request.session['d_dataid[4]'] = d_dataid[4]
#                 request.session['audio_recorded'] = True
#                 with open(json_eng) as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[4]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word5.html", {"recording": True,"val":val })
#             elif selected_option == 'Hindi':
#                 print("d_dataid4",d_dataid[4])
#                 request.session['d_dataid[4]'] = d_dataid[4]
#                 request.session['audio_recorded'] = True
#                 with open(json_hin, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[4]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word5.html", {"recording": True,"val":val })
#             elif selected_option == 'Assamese':
#                 print("d_dataid1",d_dataid[4])
#                 request.session['d_dataid[4]'] = d_dataid[4]
#                 request.session['audio_recorded'] = True
#                 with open(json_ass, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[4]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word5.html", {"recording": True,"val":val })
#             elif selected_option == 'Bengali':
#                 print("d_dataid4",d_dataid[4])
#                 request.session['d_dataid[4]'] = d_dataid[4]
#                 request.session['audio_recorded'] = True
#                 with open(json_ben, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[4]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word5.html", {"recording": True,"val":val })
#             elif selected_option == 'Gujarati':
#                 print("d_dataid4",d_dataid[4])
#                 request.session['d_dataid[4]'] = d_dataid[4]
#                 request.session['audio_recorded'] = True
#                 with open(json_guj, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[4]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word5.html", {"recording": True,"val":val })
#             elif selected_option == 'Marathi':
#                 print("d_dataid4",d_dataid[4])
#                 request.session['d_dataid[4]'] = d_dataid[4]
#                 request.session['audio_recorded'] = True
#                 with open(json_mar, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[4]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word5.html", {"recording": True,"val":val })
#             elif selected_option == 'Kannada':
#                 print("d_dataid4",d_dataid[4])
#                 request.session['d_dataid[4]'] = d_dataid[4]
#                 request.session['audio_recorded'] = True
#                 with open(json_kan, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[4]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word5.html", {"recording": True,"val":val })
#             elif selected_option == 'Malayalam':
#                 print("d_dataid4",d_dataid[4])
#                 request.session['d_dataid[4]'] = d_dataid[4]
#                 request.session['audio_recorded'] = True
#                 with open(json_mal, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[4]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word5.html", {"recording": True,"val":val })
#             elif selected_option == 'Odiya':
#                 print("d_dataid4",d_dataid[4])
#                 request.session['d_dataid[4]'] = d_dataid[4]
#                 request.session['audio_recorded'] = True
#                 with open(json_odi, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[4]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word5.html", {"recording": True,"val":val })
#             elif selected_option == 'Punjabi':
#                 print("d_dataid4",d_dataid[4])
#                 request.session['d_dataid[4]'] = d_dataid[4]
#                 request.session['audio_recorded'] = True
#                 with open(json_pun, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[4]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word5.html", {"recording": True,"val":val })
#             elif selected_option == 'Tamil':
#                 print("d_dataid4",d_dataid[4])
#                 request.session['d_dataid[4]'] = d_dataid[4]
#                 request.session['audio_recorded'] = True
#                 with open(json_tami, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[4]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word5.html", {"recording": True,"val":val })
#             elif selected_option == 'Telugu':
#                 print("d_dataid4",d_dataid[4])
#                 request.session['d_dataid[4]'] = d_dataid[4]
#                 request.session['audio_recorded'] = True
#                 with open(json_tel, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[4]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word5.html", {"recording": True,"val":val })
#             elif selected_option == 'Urdu':
#                 print("d_dataid4",d_dataid[4])
#                 request.session['d_dataid[4]'] = d_dataid[4]
#                 request.session['audio_recorded'] = True
#                 with open(json_urdu, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     Word = None
#                     for d in data['Word']:
#                         if d['id'] == d_dataid[4]:
#                             val = d['data']
#                             break
#                     if val:
#                         print("the val",val)
#                     return render(request, "retake_word/retake_word5.html", {"recording": True,"val":val })
#     return redirect('word_answer')


@csrf_exempt
def retake_word(request):
    d_audio_files = request.session.setdefault('d_audio_files', [])
    d_copy_audio_files = request.session.get('d_copy_audio_files', [])

    d_audio_files_name = request.session.setdefault('d_audio_files_name', [])
    d_dataid = request.session.setdefault('d_dataid', [])


    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        print(val)
        request.session['d_dataid[0]'] = d_dataid[0]

        filename = d_dataid[0]+'.wav'
        

        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        print("$$$$$$$$$$$$$$$$$$$$$$$", filepath)

        try:
            with open(filepath, 'wb') as audio_file:
                audio_file.write(request.FILES['audio_blob'].read())
            print("Audio file created successfully.")
        except Exception as e:
            print(f"An error occurred while creating the audio file: {e}")

        for i, path in enumerate(d_copy_audio_files):

            if path == filepath:
                d_copy_audio_files[i] = filepath
            if len(d_copy_audio_files)<5:
                d_copy_audio_files.insert(0, filepath)

            if len(d_copy_audio_files)==0:
                d_copy_audio_files.insert(0, filepath)

        print("###",d_copy_audio_files)
        # if len(d_audio_files) < 5:
        #     d_audio_files.clear()
        #     d_audio_files_name.clear()

        request.session['filepath'] = filepath
        return render(request, 'word_answer.html', { 'audio_url': filepath})
    
def save_word1(request):
    d_dataid = request.session.setdefault('d_dataid', [])
    
    filepath = request.session.get('filepath')
    print(filepath)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    
    if selected_option == 'English':
        request.session['d_dataid[0]'] = d_dataid[0]

        print("data_id",d_dataid[0])
        with open(json_eng) as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[0]:
                    val = d['data']
                    break
    elif selected_option == 'Hindi':
        request.session['d_dataid[0]'] = d_dataid[0]

        print("data_id",d_dataid[0])
        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[0]:
                    val = d['data']
                    break
    elif selected_option == 'Assamese':
        request.session['d_dataid[0]'] = d_dataid[0]

        print("data_id",d_dataid[0])
        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[0]:
                    val = d['data']
                    break
    elif selected_option == 'Bengali':
        request.session['d_dataid[0]'] = d_dataid[0]

        print("data_id",d_dataid[0])
        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[0]:
                    val = d['data']
                    break
    elif selected_option == 'Gujarati':
        request.session['d_dataid[0]'] = d_dataid[0]

        print("data_id",d_dataid[0])
        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[0]:
                    val = d['data']
                    break
    elif selected_option == 'Marathi':
        request.session['d_dataid[0]'] = d_dataid[0]

        print("data_id",d_dataid[0])
        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[0]:
                    val = d['data']
                    break
    elif selected_option == 'Kannada':
        request.session['d_dataid[0]'] = d_dataid[0]

        print("data_id",d_dataid[0])
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[0]:
                    val = d['data']
                    break

    elif selected_option == 'Malayalam':
        request.session['d_dataid[0]'] = d_dataid[0]

        print("data_id",d_dataid[0])
        with open(json_mal, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[0]:
                    val = d['data']
                    break
    elif selected_option == 'Odiya':
        request.session['d_dataid[0]'] = d_dataid[0]

        print("data_id",d_dataid[0])
        with open(json_odi, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[0]:
                    val = d['data']
                    break
    elif selected_option == 'Punjabi':
        request.session['d_dataid[0]'] = d_dataid[0]

        print("data_id",d_dataid[0])
        with open(json_pun, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[0]:
                    val = d['data']
                    break
    elif selected_option == 'Tamil':
        request.session['d_dataid[0]'] = d_dataid[0]

        print("data_id",d_dataid[0])
        with open(json_tami, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[0]:
                    val = d['data']
                    break
    elif selected_option == 'Telugu':
        request.session['d_dataid[0]'] = d_dataid[0]

        print("data_id",d_dataid[0])
        with open(json_tel, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[0]:
                    val = d['data']
                    break
    elif selected_option == 'Urdu':
        request.session['d_dataid[0]'] = d_dataid[0]

        print("data_id",d_dataid[0])
        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[0]:
                    val = d['data']
                    break
    if val:
        print("the val",val)
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': selected_option,'question':val}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    # dc_res=[]
    if response.status_code == 200:

        dc_res = request.session.setdefault('dc_res', [])
        if request.session.get("dc_res",None) is None:
            dc_res = []
        else:
            dc_res = request.session.get("dc_res")
            if len(dc_res) ==5:
                dc_res[0] = response.text
            else:
                dc_res.insert(0, response.text)
            # dc_res.clear()

            request.session["dc_res"] = dc_res
            print("testing the data", dc_res)
            if len(dc_res)==5:
                    request.session['dc_rec'] = dc_res
                    context = {'l_res': dc_res}
                    url = reverse('wans_page')
                    if len(dc_res)==5:
                        
                        return redirect(url,context)
            if len(dc_res)==4:
                    request.session['dc_rec'] = dc_res
                    context = {'l_res': dc_res}
                    url = reverse('wans_page')
                    if len(dc_res)==4:
                        
                        return redirect(url,context)
        

@csrf_exempt
def retake_word2(request):
    d_audio_files = request.session.setdefault('d_audio_files', [])
    d_copy_audio_files = request.session.get('d_copy_audio_files', [])

    d_audio_files_name = request.session.setdefault('d_audio_files_name', [])
    d_dataid = request.session.setdefault('d_dataid', [])


    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        print(val)
        request.session['d_dataid[1]'] = d_dataid[1]

        filename = d_dataid[1]+'.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
        for i, path in enumerate(d_copy_audio_files):
            if path == filepath:
                d_copy_audio_files[i] = filepath
            if len(d_copy_audio_files)<5:
                d_copy_audio_files.append(filepath)
        print("###",d_copy_audio_files)
        # if len(d_audio_files) < 5:
        #     d_audio_files.clear()
        #     d_audio_files_name.clear()

        request.session['filepath'] = filepath
        return render(request, 'word_answer.html', { 'audio_url': filepath})
    
def save_word2(request):
    d_dataid = request.session.setdefault('d_dataid', [])
    
    filepath = request.session.get('filepath')
    print(filepath)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    
    if selected_option == 'English':
        request.session['d_dataid[1]'] = d_dataid[1]

        print("data_id",d_dataid[1])
        with open(json_eng) as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[1]:
                    val = d['data']
                    break
    elif selected_option == 'Hindi':
        request.session['d_dataid[1]'] = d_dataid[1]

        print("data_id",d_dataid[1])
        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[1]:
                    val = d['data']
                    break
    elif selected_option == 'Assamese':
        request.session['d_dataid[1]'] = d_dataid[1]

        print("data_id",d_dataid[1])
        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[1]:
                    val = d['data']
                    break
    elif selected_option == 'Bengali':
        request.session['d_dataid[1]'] = d_dataid[1]

        print("data_id",d_dataid[1])
        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[1]:
                    val = d['data']
                    break
    elif selected_option == 'Gujarati':
        request.session['d_dataid[1]'] = d_dataid[1]

        print("data_id",d_dataid[1])
        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[1]:
                    val = d['data']
                    break
    elif selected_option == 'Marathi':
        request.session['d_dataid[1]'] = d_dataid[1]

        print("data_id",d_dataid[1])
        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[1]:
                    val = d['data']
                    break
    elif selected_option == 'Kannada':
        request.session['d_dataid[1]'] = d_dataid[1]

        print("data_id",d_dataid[1])
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[1]:
                    val = d['data']
                    break

    elif selected_option == 'Malayalam':
        request.session['d_dataid[1]'] = d_dataid[1]

        print("data_id",d_dataid[1])
        with open(json_mal, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[1]:
                    val = d['data']
                    break
    elif selected_option == 'Odiya':
        request.session['d_dataid[1]'] = d_dataid[1]

        print("data_id",d_dataid[1])
        with open(json_odi, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[1]:
                    val = d['data']
                    break
    elif selected_option == 'Punjabi':
        request.session['d_dataid[1]'] = d_dataid[1]

        print("data_id",d_dataid[1])
        with open(json_pun, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[1]:
                    val = d['data']
                    break
    elif selected_option == 'Tamil':
        request.session['d_dataid[1]'] = d_dataid[1]

        print("data_id",d_dataid[1])
        with open(json_tami, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[1]:
                    val = d['data']
                    break
    elif selected_option == 'Telugu':
        request.session['d_dataid[1]'] = d_dataid[1]

        print("data_id",d_dataid[1])
        with open(json_tel, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[1]:
                    val = d['data']
                    break
    elif selected_option == 'Urdu':
        request.session['d_dataid[1]'] = d_dataid[1]

        print("data_id",d_dataid[1])
        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[1]:
                    val = d['data']
                    break
    if val:
        print("the val",val)
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': selected_option,'question':val}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    # dc_res=[]
    if response.status_code == 200:

        dc_res = request.session.setdefault('dc_res', [])
        if request.session.get("dc_res",None) is None:
            dc_res = []
        else:
            dc_res = request.session.get("dc_res")
            if len(dc_res) ==5:
                dc_res[1] = response.text
            else:
                dc_res.insert(1, response.text)
            # dc_res.clear()

            request.session["dc_res"] = dc_res
            print("testing the data", dc_res)
            if len(dc_res)==5:
                    request.session['dc_rec'] = dc_res
                    context = {'l_res': dc_res}
                    url = reverse('wans_page')
                    if len(dc_res)==5:
                        
                        return redirect(url,context)



@csrf_exempt
def retake_word3(request):
    d_audio_files = request.session.setdefault('d_audio_files', [])
    d_copy_audio_files = request.session.get('d_copy_audio_files', [])

    d_audio_files_name = request.session.setdefault('d_audio_files_name', [])
    d_dataid = request.session.setdefault('d_dataid', [])


    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        print(val)
        request.session['d_dataid[2]'] = d_dataid[2]

        filename = d_dataid[2]+'.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
        for i, path in enumerate(d_copy_audio_files):
            if path == filepath:
                d_copy_audio_files[i] = filepath
            if len(d_copy_audio_files)<5:
                d_copy_audio_files.append(filepath)
        print("###",d_copy_audio_files)
        # if len(d_audio_files) < 5:
        #     d_audio_files.clear()
        #     d_audio_files_name.clear()

        request.session['filepath'] = filepath
        return render(request, 'word_answer.html', { 'audio_url': filepath})
    
def save_word3(request):
    d_dataid = request.session.setdefault('d_dataid', [])
    
    filepath = request.session.get('filepath')
    print(filepath)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    
    if selected_option == 'English':
        request.session['d_dataid[2]'] = d_dataid[2]

        print("data_id",d_dataid[2])
        with open(json_eng) as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[2]:
                    val = d['data']
                    break
    elif selected_option == 'Hindi':
        request.session['d_dataid[2]'] = d_dataid[2]

        print("data_id",d_dataid[2])
        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[2]:
                    val = d['data']
                    break
    elif selected_option == 'Assamese':
        request.session['d_dataid[2]'] = d_dataid[2]

        print("data_id",d_dataid[2])
        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[2]:
                    val = d['data']
                    break
    elif selected_option == 'Bengali':
        request.session['d_dataid[2]'] = d_dataid[2]

        print("data_id",d_dataid[2])
        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[2]:
                    val = d['data']
                    break
    elif selected_option == 'Gujarati':
        request.session['d_dataid[2]'] = d_dataid[2]

        print("data_id",d_dataid[2])
        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[2]:
                    val = d['data']
                    break
    elif selected_option == 'Marathi':
        request.session['d_dataid[2]'] = d_dataid[2]

        print("data_id",d_dataid[2])
        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[2]:
                    val = d['data']
                    break
    elif selected_option == 'Kannada':
        request.session['d_dataid[2]'] = d_dataid[2]

        print("data_id",d_dataid[2])
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[2]:
                    val = d['data']
                    break

    elif selected_option == 'Malayalam':
        request.session['d_dataid[2]'] = d_dataid[2]

        print("data_id",d_dataid[2])
        with open(json_mal, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[2]:
                    val = d['data']
                    break
    elif selected_option == 'Odiya':
        request.session['d_dataid[2]'] = d_dataid[2]

        print("data_id",d_dataid[2])
        with open(json_odi, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[2]:
                    val = d['data']
                    break
    elif selected_option == 'Punjabi':
        request.session['d_dataid[2]'] = d_dataid[2]

        print("data_id",d_dataid[2])
        with open(json_pun, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[2]:
                    val = d['data']
                    break
    elif selected_option == 'Tamil':
        request.session['d_dataid[2]'] = d_dataid[2]

        print("data_id",d_dataid[2])
        with open(json_tami, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[2]:
                    val = d['data']
                    break
    elif selected_option == 'Telugu':
        request.session['d_dataid[2]'] = d_dataid[2]

        print("data_id",d_dataid[2])
        with open(json_tel, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[2]:
                    val = d['data']
                    break
    elif selected_option == 'Urdu':
        request.session['d_dataid[2]'] = d_dataid[2]

        print("data_id",d_dataid[2])
        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[2]:
                    val = d['data']
                    break

    if val:
        print("the val",val)
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': selected_option,'question':val}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    # dc_res=[]
    if response.status_code == 200:

        dc_res = request.session.setdefault('dc_res', [])
        if request.session.get("dc_res",None) is None:
            dc_res = []
        else:
            dc_res = request.session.get("dc_res")
            if len(dc_res) ==5:
                dc_res[2] = response.text
            else:
                dc_res.insert(2, response.text)
            # dc_res.clear()

            request.session["dc_res"] = dc_res
            print("testing the data", dc_res)
            if len(dc_res)==5:
                    request.session['dc_rec'] = dc_res
                    context = {'l_res': dc_res}
                    url = reverse('wans_page')
                    if len(dc_res)==5:
                        
                        return redirect(url,context)



@csrf_exempt
def retake_word4(request):
    d_audio_files = request.session.setdefault('d_audio_files', [])
    d_copy_audio_files = request.session.get('d_copy_audio_files', [])

    d_audio_files_name = request.session.setdefault('d_audio_files_name', [])
    d_dataid = request.session.setdefault('d_dataid', [])


    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        print(val)
        request.session['d_dataid[3]'] = d_dataid[3]

        filename = d_dataid[3]+'.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
        for i, path in enumerate(d_copy_audio_files):
            if path == filepath:
                d_copy_audio_files[i] = filepath
            if len(d_copy_audio_files)<5:
                d_copy_audio_files.append(filepath)
        print("###",d_copy_audio_files)
        # if len(d_audio_files) < 5:
        #     d_audio_files.clear()
        #     d_audio_files_name.clear()

        request.session['filepath'] = filepath
        return render(request, 'word_answer.html', { 'audio_url': filepath})
    
def save_word4(request):
    d_dataid = request.session.setdefault('d_dataid', [])
    
    filepath = request.session.get('filepath')
    print(filepath)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    
    if selected_option == 'English':
        request.session['d_dataid[3]'] = d_dataid[3]

        print("data_id",d_dataid[3])
        with open(json_eng) as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[3]:
                    val = d['data']
                    break
    elif selected_option == 'Hindi':
        request.session['d_dataid[3]'] = d_dataid[3]

        print("data_id",d_dataid[3])
        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[3]:
                    val = d['data']
                    break
    elif selected_option == 'Assamese':
        request.session['d_dataid[3]'] = d_dataid[3]

        print("data_id",d_dataid[3])
        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[3]:
                    val = d['data']
                    break
    elif selected_option == 'Bengali':
        request.session['d_dataid[3]'] = d_dataid[3]

        print("data_id",d_dataid[3])
        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[3]:
                    val = d['data']
                    break
    elif selected_option == 'Gujarati':
        request.session['d_dataid[3]'] = d_dataid[3]

        print("data_id",d_dataid[3])
        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[3]:
                    val = d['data']
                    break
    elif selected_option == 'Marathi':
        request.session['d_dataid[3]'] = d_dataid[3]

        print("data_id",d_dataid[3])
        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[3]:
                    val = d['data']
                    break
    elif selected_option == 'Kannada':
        request.session['d_dataid[3]'] = d_dataid[3]

        print("data_id",d_dataid[3])
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[3]:
                    val = d['data']
                    break

    elif selected_option == 'Malayalam':
        request.session['d_dataid[3]'] = d_dataid[3]

        print("data_id",d_dataid[3])
        with open(json_mal, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[3]:
                    val = d['data']
                    break
    elif selected_option == 'Odiya':
        request.session['d_dataid[3]'] = d_dataid[3]

        print("data_id",d_dataid[3])
        with open(json_odi, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[3]:
                    val = d['data']
                    break
    elif selected_option == 'Punjabi':
        request.session['d_dataid[3]'] = d_dataid[3]

        print("data_id",d_dataid[3])
        with open(json_pun, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[3]:
                    val = d['data']
                    break
    elif selected_option == 'Tamil':
        request.session['d_dataid[3]'] = d_dataid[3]

        print("data_id",d_dataid[3])
        with open(json_tami, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[3]:
                    val = d['data']
                    break
    elif selected_option == 'Telugu':
        request.session['d_dataid[3]'] = d_dataid[3]

        print("data_id",d_dataid[3])
        with open(json_tel, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[3]:
                    val = d['data']
                    break
    elif selected_option == 'Urdu':
        request.session['d_dataid[3]'] = d_dataid[3]

        print("data_id",d_dataid[3])
        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[3]:
                    val = d['data']
                    break

    if val:
        print("the val",val)
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': selected_option,'question':val}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    # dc_res=[]
    if response.status_code == 200:

        dc_res = request.session.setdefault('dc_res', [])
        if request.session.get("dc_res",None) is None:
            dc_res = []
        else:
            dc_res = request.session.get("dc_res")
            if len(dc_res) ==5:
                dc_res[3] = response.text
            else:
                dc_res.insert(3, response.text)
            # dc_res.clear()

            request.session["dc_res"] = dc_res
            print("testing the data", dc_res)
            if len(dc_res)==5:
                    request.session['dc_rec'] = dc_res
                    context = {'l_res': dc_res}
                    url = reverse('wans_page')
                    if len(dc_res)==5:
                        
                        return redirect(url,context)


@csrf_exempt
def retake_word5(request):
    d_audio_files = request.session.setdefault('d_audio_files', [])
    d_copy_audio_files = request.session.get('d_copy_audio_files', [])

    d_audio_files_name = request.session.setdefault('d_audio_files_name', [])
    d_dataid = request.session.setdefault('d_dataid', [])


    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        print(val)
        request.session['d_dataid[4]'] = d_dataid[4]

        filename = d_dataid[4]+'.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
        for i, path in enumerate(d_copy_audio_files):
            if path == filepath:
                d_copy_audio_files[i] = filepath
           

            if len(d_copy_audio_files)<5:
                d_copy_audio_files.append(filepath)
            if len(d_copy_audio_files)<4:
                d_copy_audio_files.append(filepath)
        print("###",d_copy_audio_files)
        # if len(d_audio_files) < 5:
        #     d_audio_files.clear()
        #     d_audio_files_name.clear()

        request.session['filepath'] = filepath
        return render(request, 'word_answer.html', { 'audio_url': filepath})
    
def save_word5(request):
    d_dataid = request.session.setdefault('d_dataid', [])
    
    filepath = request.session.get('filepath')
    print(filepath)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    
    if selected_option == 'English':
        request.session['d_dataid[4]'] = d_dataid[4]

        print("data_id",d_dataid[4])
        with open(json_eng) as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[4]:
                    val = d['data']
                    break
    elif selected_option == 'Hindi':
        request.session['d_dataid[4]'] = d_dataid[4]

        print("data_id",d_dataid[4])
        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[4]:
                    val = d['data']
                    break
    elif selected_option == 'Assamese':
        request.session['d_dataid[4]'] = d_dataid[4]

        print("data_id",d_dataid[4])
        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[4]:
                    val = d['data']
                    break
    elif selected_option == 'Bengali':
        request.session['d_dataid[4]'] = d_dataid[4]

        print("data_id",d_dataid[4])
        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[4]:
                    val = d['data']
                    break
    elif selected_option == 'Gujarati':
        request.session['d_dataid[4]'] = d_dataid[4]

        print("data_id",d_dataid[4])
        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[4]:
                    val = d['data']
                    break
    elif selected_option == 'Marathi':
        request.session['d_dataid[4]'] = d_dataid[4]

        print("data_id",d_dataid[4])
        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[4]:
                    val = d['data']
                    break
    elif selected_option == 'Kannada':
        request.session['d_dataid[4]'] = d_dataid[4]

        print("data_id",d_dataid[4])
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[4]:
                    val = d['data']
                    break

    elif selected_option == 'Malayalam':
        request.session['d_dataid[4]'] = d_dataid[4]

        print("data_id",d_dataid[4])
        with open(json_mal, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[4]:
                    val = d['data']
                    break
    elif selected_option == 'Odiya':
        request.session['d_dataid[4]'] = d_dataid[4]

        print("data_id",d_dataid[4])
        with open(json_odi, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[4]:
                    val = d['data']
                    break
    elif selected_option == 'Punjabi':
        request.session['d_dataid[4]'] = d_dataid[4]

        print("data_id",d_dataid[4])
        with open(json_pun, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[4]:
                    val = d['data']
                    break
    elif selected_option == 'Tamil':
        request.session['d_dataid[4]'] = d_dataid[4]

        print("data_id",d_dataid[4])
        with open(json_tami, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[4]:
                    val = d['data']
                    break
    elif selected_option == 'Telugu':
        request.session['d_dataid[4]'] = d_dataid[4]

        print("data_id",d_dataid[4])
        with open(json_tel, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[4]:
                    val = d['data']
                    break
    elif selected_option == 'Urdu':
        request.session['d_dataid[4]'] = d_dataid[4]

        print("data_id",d_dataid[4])
        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[4]:
                    val = d['data']
                    break

    if val:
        print("the val",val)
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': selected_option,'question':val}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    # dc_res=[]
    if response.status_code == 200:

        dc_res = request.session.setdefault('dc_res', [])
        if request.session.get("dc_res",None) is None:
            dc_res = []
        else:
            dc_res = request.session.get("dc_res")
            if len(dc_res) ==5:
                dc_res[4] = response.text
            else:
                dc_res.insert(4, response.text)
            # dc_res.clear()

            request.session["dc_res"] = dc_res
            print("testing the data", dc_res)
            if len(dc_res)==5:
                    request.session['dc_rec'] = dc_res
                    context = {'l_res': dc_res}
                    url = reverse('wans_page')
                    if len(dc_res)==5:
                        
                        return redirect(url,context)

    
#                   Letter Recording

def letter(request):
    l_dataid = request.session.setdefault('l_dataid', [])
    lc_res = request.session.setdefault('lc_res', [])
    qletter = request.session.setdefault('qletter', [])
    l_audio_files = request.session.setdefault('l_audio_files', [])
    l_audio_files_name = request.session.setdefault('l_audio_files_name', [])
    data_ids = request.session.setdefault('data_ids', [])
    skip_val_letter = request.session.setdefault('skip_val_letter', [])

    del request.session['l_dataid']
    del request.session['lc_res']
    del request.session['qletter']
    del request.session['l_audio_files']
    del request.session['l_audio_files_name']
    del request.session['data_ids']
    del request.session['skip_val_letter']

    
 


    
    if request.method == 'POST':
        print("qword",qletter)
        
        if len(lc_res) == 5:
            lc_res.clear()
            l_dataid.clear()
            # qword.clear()
            # print("qword",qword)
            qletter.clear()
            data_ids.clear()
            l_audio_files.clear()
            l_audio_files_name.clear()
          
            if len(l_audio_files)>5:
                l_audio_files.clear()
                l_audio_files_name.clear() 
        elif len(lc_res) == 4:
            lc_res.clear()
            l_dataid.clear()
            # qword.clear()
            # print("qword",qword)
            qletter.clear()
            data_ids.clear()
            l_audio_files.clear()
            l_audio_files_name.clear()
          
            if len(l_audio_files)>4:
                l_audio_files.clear()
                l_audio_files_name.clear() 
        elif len(lc_res) == 3:
            lc_res.clear()
            l_dataid.clear()
            # qword.clear()
            # print("qword",qword)
            qletter.clear()
            data_ids.clear()
            l_audio_files.clear()
            l_audio_files_name.clear()
          
            if len(l_audio_files)>3:
                l_audio_files.clear()
                l_audio_files_name.clear() 
        elif len(lc_res) == 2:
            lc_res.clear()
            l_dataid.clear()
            # qword.clear()
            # print("qword",qword)
            qletter.clear()
            data_ids.clear()
            l_audio_files.clear()
            l_audio_files_name.clear()
          
            if len(l_audio_files)>2:
                l_audio_files.clear()
                l_audio_files_name.clear() 
        elif len(lc_res) == 1:
            lc_res.clear()
            l_dataid.clear()
            # qword.clear()
            # print("qword",qword)
            qletter.clear()
            data_ids.clear()
            l_audio_files.clear()
            l_audio_files_name.clear()
          
            if len(l_audio_files)>1:
                l_audio_files.clear()
                l_audio_files_name.clear() 
        elif len(lc_res) == 0:
            lc_res.clear()
            l_dataid.clear()
            # qword.clear()
            # print("qword",qword)
            qletter.clear()
            data_ids.clear()
            l_audio_files.clear()
            l_audio_files_name.clear()
          
            if len(l_audio_files)>0:
                l_audio_files.clear()
                l_audio_files_name.clear() 
        return redirect('letter_recording_next')
    return render(request, 'letter_start.html')


def get_random_letter(request):
    data_ids = request.session.setdefault('data_ids', [])
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    # data_ids.clear()                                                                                                 ##Reset
    if selected_option == 'English':
        with open(json_eng, 'r') as f:
            data = json.load(f)
            data1 = random.choice(data['Letter'])
            print("the value ",data1['id'])
            data_id = data1['id']
            
            while data_id in data_ids:
                data1 = random.choice(data['Letter'])
                data_id = data1['id']
            
            data_ids.append(data_id)
            print("data_ids",data_ids)
            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(data_ids) ==5:
                l_dataid = data_ids.copy()
                print(l_dataid)
                request.session['l_dataid'] = l_dataid
                data_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Hindi':
        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Letter'])
            print("the value ",data1['id'])
            data_id = data1['id']
            
            while data_id in data_ids:
                data1 = random.choice(data['Letter'])
                data_id = data1['id']
            
            data_ids.append(data_id)
            print("data_ids",data_ids)
            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(data_ids) ==5:
                l_dataid = data_ids.copy()
                print(l_dataid)
                request.session['l_dataid'] = l_dataid
                data_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Assamese':
        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Letter'])
            print("the value ",data1['id'])
            data_id = data1['id']
            
            while data_id in data_ids:
                data1 = random.choice(data['Letter'])
                data_id = data1['id']
            
            data_ids.append(data_id)
            print("data_ids",data_ids)
            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(data_ids) ==5:
                l_dataid = data_ids.copy()
                print(l_dataid)
                request.session['l_dataid'] = l_dataid
                data_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Bengali':
        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Letter'])
            print("the value ",data1['id'])
            data_id = data1['id']
            
            while data_id in data_ids:
                data1 = random.choice(data['Letter'])
                data_id = data1['id']
            
            data_ids.append(data_id)
            print("data_ids",data_ids)
            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(data_ids) ==5:
                l_dataid = data_ids.copy()
                print(l_dataid)
                request.session['l_dataid'] = l_dataid
                data_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Gujarati':
        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Letter'])
            print("the value ",data1['id'])
            data_id = data1['id']
            
            while data_id in data_ids:
                data1 = random.choice(data['Letter'])
                data_id = data1['id']
            
            data_ids.append(data_id)
            print("data_ids",data_ids)
            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(data_ids) ==5:
                l_dataid = data_ids.copy()
                print(l_dataid)
                request.session['l_dataid'] = l_dataid
                data_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Marathi':
        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Letter'])
            print("the value ",data1['id'])
            data_id = data1['id']
            
            while data_id in data_ids:
                data1 = random.choice(data['Letter'])
                data_id = data1['id']
            
            data_ids.append(data_id)
            print("data_ids",data_ids)
            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(data_ids) ==5:
                l_dataid = data_ids.copy()
                print(l_dataid)
                request.session['l_dataid'] = l_dataid
                data_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Kannada':
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Letter'])
            print("the value ",data1['id'])
            data_id = data1['id']
            
            while data_id in data_ids:
                data1 = random.choice(data['Letter'])
                data_id = data1['id']
            
            data_ids.append(data_id)
            print("data_ids",data_ids)
            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(data_ids) ==5:
                l_dataid = data_ids.copy()
                print(l_dataid)
                request.session['l_dataid'] = l_dataid
                data_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Telugu':
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Letter'])
            print("the value ",data1['id'])
            data_id = data1['id']
            
            while data_id in data_ids:
                data1 = random.choice(data['Letter'])
                data_id = data1['id']
            
            data_ids.append(data_id)
            print("data_ids",data_ids)
            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(data_ids) ==5:
                l_dataid = data_ids.copy()
                print(l_dataid)
                request.session['l_dataid'] = l_dataid
                data_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Kannada':
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Letter'])
            print("the value ",data1['id'])
            data_id = data1['id']
            
            while data_id in data_ids:
                data1 = random.choice(data['Letter'])
                data_id = data1['id']
            
            data_ids.append(data_id)
            print("data_ids",data_ids)
            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(data_ids) ==5:
                l_dataid = data_ids.copy()
                print(l_dataid)
                request.session['l_dataid'] = l_dataid
                data_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Kannada':
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Letter'])
            print("the value ",data1['id'])
            data_id = data1['id']
            
            while data_id in data_ids:
                data1 = random.choice(data['Letter'])
                data_id = data1['id']
            
            data_ids.append(data_id)
            print("data_ids",data_ids)
            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(data_ids) ==5:
                l_dataid = data_ids.copy()
                print(l_dataid)
                request.session['l_dataid'] = l_dataid
                data_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Kannada':
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Letter'])
            print("the value ",data1['id'])
            data_id = data1['id']
            
            while data_id in data_ids:
                data1 = random.choice(data['Letter'])
                data_id = data1['id']
            
            data_ids.append(data_id)
            print("data_ids",data_ids)
            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(data_ids) ==5:
                l_dataid = data_ids.copy()
                print(l_dataid)
                request.session['l_dataid'] = l_dataid
                data_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Kannada':
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Letter'])
            print("the value ",data1['id'])
            data_id = data1['id']
            
            while data_id in data_ids:
                data1 = random.choice(data['Letter'])
                data_id = data1['id']
            
            data_ids.append(data_id)
            print("data_ids",data_ids)
            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(data_ids) ==5:
                l_dataid = data_ids.copy()
                print(l_dataid)
                request.session['l_dataid'] = l_dataid
                data_ids.clear()
            return data1['data'], data_id
    elif selected_option == 'Urdu':
        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data1 = random.choice(data['Letter'])
            print("the value ",data1['id'])
            data_id = data1['id']
            
            while data_id in data_ids:
                data1 = random.choice(data['Letter'])
                data_id = data1['id']
            
            data_ids.append(data_id)
            print("data_ids",data_ids)
            request.session['data_id'] = data_id
            print("dta",data1['data'])
            if len(data_ids) ==5:
                l_dataid = data_ids.copy()
                print(l_dataid)
                request.session['l_dataid'] = l_dataid
                data_ids.clear()
            return data1['data'], data_id


def letter_recording(request):
    l_dataid = request.session.setdefault('l_dataid', [])
    lc_res = request.session.setdefault('lc_res', [])


    if len(lc_res) == 5:
        lc_res.clear()
        l_dataid.clear()
    print(l_dataid)
   
    Letter, data_id = get_random_letter(request)
    context = {"val": Letter, "recording": True, "data_id": data_id}
    request.session['submit_id_letter'] = context
    return render(request, "letter_rec.html", context)

def letter_recording_next(request):
    l_dataid = request.session.setdefault('l_dataid', [])
    lc_res = request.session.setdefault('lc_res', [])
    qletter = request.session.setdefault('qletter', [])
    print("qletter",qletter)
    if len(lc_res) == 5:
        lc_res.clear()
        l_dataid.clear()
        qletter.clear()
        print("qletter",qletter)



    # if len(qletter)<5:
    #     qletter.clear()
    #     print("qword",qletter)                                                                                           ### Reset 
        
        
                                                                                                             
    print(l_dataid)
   
    Letter, data_id = get_random_letter(request)
    context = {"val": Letter, "recording": True, "data_id": data_id}
    return render(request, "letter_rec_next.html", context)

# def letter_skip(request):
#     if "stop" in request.POST:
#         return redirect('letter_recording_next')

def letter_skip(request):
    skip_val_letter = request.session.setdefault('skip_val_letter', [])
    
    l_audio_files = request.session.get('l_audio_files', [])
    l_audio_files_name = request.session.get('l_audio_files_name', [])
    data_ids = request.session.get('data_ids', [])
    qletter = request.session.setdefault('qletter', [])

    print("l_audio_files_name",l_audio_files_name)
    print("data_ids",data_ids)
    data_ids = request.session.get('data_ids', [])
    l_audio_files_name = request.session.get('l_audio_files_name', [])

    missing_indices = [i for i, id in enumerate(data_ids) if id not in l_audio_files_name]

    # Print the missing indices
    print("The missing indices are:", missing_indices)
    for data_id in data_ids:
        audio_file = data_id + '.wav'
        if audio_file not in l_audio_files_name:
            l_audio_files_name.append(audio_file)

    # update the session variable with the new list
    for data_id in data_ids:
        # wav_file = f"D:\\Parakh Final Project\\Parakh\\media\\{data_id}.wav"
        wav_file = os.path.join(base_path, f"{data_id}.wav")

        if wav_file not in l_audio_files:
            l_audio_files.append(wav_file)
            skip_val_letter.append(wav_file)



    request.session['l_audio_files'] = l_audio_files
    request.session['skip_val_letter'] = skip_val_letter


   



    print("l_audio_files  word_answer",l_audio_files)
    request.session['l_audio_files_name'] = l_audio_files_name



    # filepath = os.path.join(settings.MEDIA_ROOT, 'skip_word.wav')
    # if not os.path.exists(filepath):
    #     return HttpResponseBadRequest('Audio file not found')

    # print(filepath)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    
    if selected_option == 'English':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_eng) as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Hindi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Assamese':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Bengali':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Gujarati':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Marathi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Kannada':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break

    elif selected_option == 'Malayalam':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_mal, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Odiya':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_odi, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Punjabi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_pun, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Tamil':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_tami, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Telugu':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_tel, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Urdu':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    # data_id = request.session.get('data_id')
    # print("data_id",data_id)
    # with open(json_eng) as f:
    #     data = json.load(f)
    #     Letter = None
    #     for d in data['Letter']:
    #         if d['id'] == data_id:
    #             val = d['data']
    #             break
    # qletter = request.session.setdefault('qletter', [])
    # d_copy_audio_files = request.session.get('d_copy_audio_files', [])
    # d_audio_files = request.session.get('d_audio_files', [])
    # d_audio_files_name = request.session.setdefault('d_audio_files_name', [])
    # copy_word_name = request.session.setdefault('copy_word_name', [])

    # print("d_audio_files_name",d_audio_files_name)
    # if len(d_audio_files)==5:
    #     d_copy_audio_files= d_audio_files.copy()
    # if len(d_audio_files_name)==5:
    #     copy_word_name= d_audio_files_name.copy()
    
    # print("copy_word_name",copy_word_name)
    # request.session['copy_word_name'] = copy_word_name
    
    if val:
        print("the val",val)
        qletter = request.session.get("qletter")
        qletter.append(val)
        request.session["qletter"] = qletter

        print("qletter",qletter)
        lc_res = request.session.setdefault('lc_res', [])
        if request.session.get("lc_res",None) is None:
            lc_res = []
        else:
            lc_res = request.session.get("lc_res")
     

            request.session["lc_res"] = lc_res
            lc_res.append('{"no_mistakes": 1, "no_del": 0, "del_details": "", "no_sub": 1, "sub_details": "0-\\u092a\\u0948\\u0938\\u093e:", "status": "success", "wcpm": 0.0, "text": "", "audio_url": "", "process_time": 0.47053098678588867}')

            print("testing the data", lc_res)
            if len(lc_res)==5:
                    request.session['dc_rec'] = lc_res
                    context = {'l_res': lc_res}
                    url = reverse('lans_page')
                    return redirect(url,context)
        if len(l_audio_files) == 4:
            return redirect('letter_recording')
        # if len(d_audio_files)==5:
        #     return render(request, 'word_answer.html',{'qletter': qletter})
            
    return redirect('letter_recording_next')



def submit_letter_skip(request):
    skip_val_letter = request.session.setdefault('skip_val_letter', [])
    submit_id_letter = request.session.get('submit_id_letter')
    print(submit_id_letter)
    data_id = submit_id_letter.get('data_id')
    print('data_id:', data_id)
    l_audio_files = request.session.get('l_audio_files', [])
    l_audio_files_name = request.session.get('l_audio_files_name', [])
    data_ids = request.session.get('data_ids', [])
    qletter = request.session.setdefault('qletter', [])

    print("l_audio_files_name",l_audio_files_name)
    print("data_ids",data_ids)
    data_ids = request.session.get('data_ids', [])
    l_audio_files_name = request.session.get('l_audio_files_name', [])

    missing_indices = [i for i, id in enumerate(data_ids) if id not in l_audio_files_name]

    # Print the missing indices
    print("The missing indices are:", missing_indices)
    # for data_id in data_ids:
    audio_file = data_id + '.wav'
    if audio_file not in l_audio_files_name:
        l_audio_files_name.append(audio_file)

    # for data_id in data_ids:
    # wav_file = f"D:\\Parakh Final Project\\Parakh\\media\\{data_id}.wav"
    wav_file = os.path.join(base_path, f"{data_id}.wav")

    if wav_file not in l_audio_files:
        l_audio_files.append(wav_file)
        skip_val_letter.append(wav_file)



    request.session['l_audio_files'] = l_audio_files
    request.session['skip_val_letter'] = skip_val_letter


   



    print("l_audio_files  word_answer",l_audio_files)
    request.session['l_audio_files_name'] = l_audio_files_name



    # filepath = os.path.join(settings.MEDIA_ROOT, 'skip_word.wav')
    # if not os.path.exists(filepath):
    #     return HttpResponseBadRequest('Audio file not found')

    # print(filepath)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    
    if selected_option == 'English':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_eng) as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Hindi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Assamese':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Bengali':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Gujarati':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Marathi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Kannada':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break

    elif selected_option == 'Malayalam':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_mal, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Odiya':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_odi, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Punjabi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_pun, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Tamil':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_tami, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Telugu':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_tel, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Urdu':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break

    
    if val:
        print("the val",val)
        qletter = request.session.get("qletter")
        qletter.append(val)
        request.session["qletter"] = qletter

        print("qletter",qletter)
        lc_res = request.session.setdefault('lc_res', [])
        if request.session.get("lc_res",None) is None:
            lc_res = []
        else:
            lc_res = request.session.get("lc_res")
     

            request.session["lc_res"] = lc_res
            lc_res.append('{"no_mistakes": 1, "no_del": 0, "del_details": "", "no_sub": 1, "sub_details": "0-\\u092a\\u0948\\u0938\\u093e:", "status": "success", "wcpm": 0.0, "text": "", "audio_url": "", "process_time": 0.47053098678588867}')

            print("testing the data", lc_res)
            if len(lc_res)==5:
                    request.session['dc_rec'] = lc_res
                    context = {'l_res': lc_res}
                    url = reverse('lans_page')
                    return redirect(url,context)
        if len(l_audio_files) == 4:
            return redirect('letter_recording')
        # if len(d_audio_files)==5:
        #     return render(request, 'word_answer.html',{'qletter': qletter})
            
    return redirect('letter_recording_next')

  






@csrf_exempt
def save_letter(request):
    l_audio_files = request.session.setdefault('l_audio_files', [])
    l_audio_files_name = request.session.setdefault('l_audio_files_name', [])
    


    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        print(val)
        filename = f'{data_id}.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
        l_audio_files.append(filepath)
        l_audio_files_name.append(filename)
        print("###",l_audio_files)
        # if len(l_audio_files)< 5:
        #     l_audio_files.clear()
        #     l_audio_files_name.clear()                                                          #reset

        request.session['filepath'] = filepath
        return render(request, 'letter_rec.html', { 'audio_url': filepath})

    
def letter_answer(request):
   
    l_audio_files = request.session.setdefault('l_audio_files', [])


    filepath = request.session.get('filepath')
    print(filepath)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    if selected_option == 'English':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_eng) as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Hindi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Assamese':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Bengali':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Gujarati':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Marathi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Kannada':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Malayalam':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_mal, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Odiya':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_odi, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Punjabi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_pun, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Tamil':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_tami, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Telugu':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_tel, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    elif selected_option == 'Urdu':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == data_id:
                    val = d['data']
                    break

    qletter = request.session.setdefault('qletter', [])
    

    if val:
        print("the val",val)
        qletter = request.session.get("qletter")
        qletter.append(val)
        request.session["qletter"] = qletter

        print("qletter",qletter)
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': selected_option ,'question':val}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    # lc_res=[]
    if response.status_code == 200:

        lc_res = request.session.setdefault('lc_res', [])
        if request.session.get("lc_res",None) is None:
            lc_res = []
        else:
            lc_res = request.session.get("lc_res")
            lc_res.append(response.text)
            # lc_res.clear()                                                                              #Reset

            request.session["lc_res"] = lc_res
            print("testing the data", lc_res)
            if len(lc_res)==5:
                    request.session['lc_rec'] = lc_res
                    context = {'l_res': lc_res}
                    url = reverse('lans_page')
                    if len(lc_res)==5:
                        
                        return redirect(url,context)
        if len(l_audio_files) == 4:
                return redirect('letter_recording')
            
    return redirect('letter_recording_next')

def lans_page(request):
    l_copy_audio_files = request.session.get('l_copy_audio_files', [])
    l_audio_files_name = request.session.setdefault('l_audio_files_name', [])
    l_audio_files = request.session.get('l_audio_files', [])
    copy_letter_name = request.session.setdefault('copy_letter_name', [])
    print("l_audio_files_name",l_audio_files_name)
    if len(l_audio_files)==5:
        l_copy_audio_files= l_audio_files.copy()
    if len(l_audio_files_name)==5:
        copy_letter_name= l_audio_files_name.copy()
    if len(l_audio_files)==4:
        l_copy_audio_files= l_audio_files.copy()
    if len(l_audio_files_name)==4:
        copy_letter_name= l_audio_files_name.copy()
    
    print("copy_letter_name",copy_letter_name)
    request.session['copy_letter_name'] = copy_letter_name
    

    audio_urls = []
    if l_copy_audio_files:
        for filepath in l_copy_audio_files:
            if os.path.exists(filepath):
                filename = os.path.basename(filepath)
                audio_url = request.build_absolute_uri(settings.MEDIA_URL + filename)
                audio_urls.append(audio_url)
            else:
                audio_urls.append('') 
       
                # l_copy_audio_files.remove(file_path)
        request.session['l_copy_audio_files'] = l_copy_audio_files

    text = []
    mis=[]
    wcpm=[]
    lc_res=[]

    lc_res = request.session.setdefault('lc_res', [])
    qletter = request.session.setdefault('qletter', [])


    for item in lc_res:
        text.append(eval(item)['text'])
        mis.append(eval(item)['no_mistakes'])
        wcpm.append(eval(item)['wcpm'])
    total_wcpm = sum(wcpm) 
    total_mis = sum(mis)
    print("total",total_wcpm)
    print("qletter",qletter)
    context = {
    'qletter': qletter,
    'mis': mis,
    'flu': wcpm,
    'l_copy_audio_files': l_copy_audio_files,
    'audio_url1': audio_urls[0],
    'audio_url2': audio_urls[1],
    'audio_url3': audio_urls[2],
    'audio_url4': audio_urls[3],
    'audio_url5': audio_urls[4],
    'total_mis': total_mis
}
    
    # context = { 'text': text,'qletter': qletter, 'mis':mis ,'flu':wcpm,'l_copy_audio_files':l_copy_audio_files ,'total_wcpm': total_wcpm,'audio_urls':audio_urls ,'total_mis':total_mis}
    if len(l_audio_files)==5:
        l_audio_files.clear()
        l_audio_files_name.clear()
    return render(request, 'letter_answer.html', context)



def next_letter(request):
    t.sleep(2)    
    l_dataid = request.session.setdefault('l_dataid', [])
    copy_letter_name = request.session.setdefault('copy_letter_name', [])

    if request.method == "POST":
        copy_letter_name = request.session.get('copy_letter_name')

        # copy_letter_name = request.session.setdefault('copy_letter_name', [])
        # for file_name in copy_letter_name:
        #     file_name_without_extension = file_name.split(".")[0]
        #     l_dataid.append(file_name_without_extension)
        l_dataid = request.session.get('l_dataid', [])

        print("^^^",l_dataid)



        if "record" in request.POST:
            selected_option = request.session.get('selected_option')
            print("@",selected_option)
            if selected_option == 'English':
                print("l_dataid0",l_dataid[0])
                request.session['l_dataid[0]'] = l_dataid[0]
                request.session['audio_recorded'] = True
                with open(json_eng) as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[0]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter1.html", {"recording": True,"val":val })
            elif selected_option == 'Hindi':
                print("l_dataid0",l_dataid[0])
                request.session['l_dataid[0]'] = l_dataid[0]

                request.session['audio_recorded'] = True
                with open(json_hin, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[0]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter1.html", {"recording": True,"val":val })
            elif selected_option == 'Assamese':
                print("l_dataid0",l_dataid[0])
                request.session['l_dataid[0]'] = l_dataid[0]

                request.session['audio_recorded'] = True
                with open(json_ass, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[0]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter1.html", {"recording": True,"val":val })
            elif selected_option == 'Bengali':
                print("l_dataid0",l_dataid[0])
                request.session['l_dataid[0]'] = l_dataid[0]

                request.session['audio_recorded'] = True
                with open(json_ben, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[0]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter1.html", {"recording": True,"val":val })
            elif selected_option == 'Gujarati':
                print("l_dataid0",l_dataid[0])
                request.session['l_dataid[0]'] = l_dataid[0]

                request.session['audio_recorded'] = True
                with open(json_guj, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[0]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter1.html", {"recording": True,"val":val })
            elif selected_option == 'Marathi':
                print("l_dataid0",l_dataid[0])
                request.session['l_dataid[0]'] = l_dataid[0]

                request.session['audio_recorded'] = True
                with open(json_mar, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[0]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter1.html", {"recording": True,"val":val })
            elif selected_option == 'Kannada':
                print("l_dataid0",l_dataid[0])
                request.session['l_dataid[0]'] = l_dataid[0]

                request.session['audio_recorded'] = True
                with open(json_kan, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[0]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter1.html", {"recording": True,"val":val })
            elif selected_option == 'Malayalam':
                print("l_dataid0",l_dataid[0])
                request.session['l_dataid[0]'] = l_dataid[0]

                request.session['audio_recorded'] = True
                with open(json_mal, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[0]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter1.html", {"recording": True,"val":val })
            elif selected_option == 'Odiya':
                print("l_dataid0",l_dataid[0])
                request.session['l_dataid[0]'] = l_dataid[0]

                request.session['audio_recorded'] = True
                with open(json_odi, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[0]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter1.html", {"recording": True,"val":val })
            elif selected_option == 'Punjabi':
                print("l_dataid0",l_dataid[0])
                request.session['l_dataid[0]'] = l_dataid[0]

                request.session['audio_recorded'] = True
                with open(json_pun, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[0]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter1.html", {"recording": True,"val":val })
            elif selected_option == 'Tamil':
                print("l_dataid0",l_dataid[0])
                request.session['l_dataid[0]'] = l_dataid[0]

                request.session['audio_recorded'] = True
                with open(json_tami, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[0]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter1.html", {"recording": True,"val":val })
            elif selected_option == 'Telugu':
                print("l_dataid0",l_dataid[0])
                request.session['l_dataid[0]'] = l_dataid[0]

                request.session['audio_recorded'] = True
                with open(json_tel, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[0]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter1.html", {"recording": True,"val":val })
            elif selected_option == 'Urdu':
                print("l_dataid0",l_dataid[0])
                request.session['l_dataid[0]'] = l_dataid[0]

                request.session['audio_recorded'] = True
                with open(json_urdu, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[0]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter1.html", {"recording": True,"val":val })
            
        elif "record2" in request.POST:
            selected_option = request.session.get('selected_option')
            print("@",selected_option)
            if selected_option == 'English':
                print("l_dataid0",l_dataid[1])
                request.session['l_dataid[1]'] = l_dataid[1]

                request.session['audio_recorded'] = True
                with open(json_eng) as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[1]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter2.html", {"recording": True,"val":val })
            elif selected_option == 'Hindi':
                print("l_dataid0",l_dataid[1])
                request.session['l_dataid[1]'] = l_dataid[1]

                request.session['audio_recorded'] = True
                with open(json_hin, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[1]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter2.html", {"recording": True,"val":val })
            elif selected_option == 'Assamese':
                print("l_dataid0",l_dataid[1])
                request.session['l_dataid[1]'] = l_dataid[1]

                request.session['audio_recorded'] = True
                with open(json_ass, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[1]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter2.html", {"recording": True,"val":val })
            elif selected_option == 'Bengali':
                print("l_dataid0",l_dataid[1])
                request.session['l_dataid[1]'] = l_dataid[1]

                request.session['audio_recorded'] = True
                with open(json_ben, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[1]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter2.html", {"recording": True,"val":val })
            elif selected_option == 'Gujarati':
                print("l_dataid0",l_dataid[1])
                request.session['l_dataid[1]'] = l_dataid[1]

                request.session['audio_recorded'] = True
                with open(json_guj, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[1]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter2.html", {"recording": True,"val":val })
            elif selected_option == 'Marathi':
                print("l_dataid0",l_dataid[1])
                request.session['l_dataid[1]'] = l_dataid[1]

                request.session['audio_recorded'] = True
                with open(json_mar, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[1]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter2.html", {"recording": True,"val":val })
            elif selected_option == 'Kannada':
                print("l_dataid0",l_dataid[1])
                request.session['l_dataid[1]'] = l_dataid[1]

                request.session['audio_recorded'] = True
                with open(json_kan, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[1]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter2.html", {"recording": True,"val":val })
            elif selected_option == 'Malayalam':
                print("l_dataid0",l_dataid[1])
                request.session['l_dataid[1]'] = l_dataid[1]

                request.session['audio_recorded'] = True
                with open(json_mal, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[1]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter2.html", {"recording": True,"val":val })
            elif selected_option == 'Odiya':
                print("l_dataid0",l_dataid[1])
                request.session['l_dataid[1]'] = l_dataid[1]

                request.session['audio_recorded'] = True
                with open(json_odi, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[1]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter2.html", {"recording": True,"val":val })
            elif selected_option == 'Punjabi':
                print("l_dataid0",l_dataid[1])
                request.session['l_dataid[1]'] = l_dataid[1]

                request.session['audio_recorded'] = True
                with open(json_pun, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[1]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter2.html", {"recording": True,"val":val })
            elif selected_option == 'Tamil':
                print("l_dataid0",l_dataid[1])
                request.session['l_dataid[1]'] = l_dataid[1]

                request.session['audio_recorded'] = True
                with open(json_tami, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[1]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter2.html", {"recording": True,"val":val })
            elif selected_option == 'Telugu':
                print("l_dataid0",l_dataid[1])
                request.session['l_dataid[1]'] = l_dataid[1]

                request.session['audio_recorded'] = True
                with open(json_tel, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[1]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter2.html", {"recording": True,"val":val })
            elif selected_option == 'Urdu':
                print("l_dataid0",l_dataid[1])
                request.session['l_dataid[1]'] = l_dataid[1]

                request.session['audio_recorded'] = True
                with open(json_urdu, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[1]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter2.html", {"recording": True,"val":val })

        elif "record3" in request.POST:
            selected_option = request.session.get('selected_option')
            print("@",selected_option)
            if selected_option == 'English':
                print("l_dataid0",l_dataid[2])
                request.session['l_dataid[2]'] = l_dataid[2]

                request.session['audio_recorded'] = True
                with open(json_eng) as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[2]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter3.html", {"recording": True,"val":val })
            elif selected_option == 'Hindi':
                print("l_dataid0",l_dataid[2])
                request.session['l_dataid[2]'] = l_dataid[2]

                request.session['audio_recorded'] = True
                with open(json_hin, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[2]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter3.html", {"recording": True,"val":val })
            elif selected_option == 'Assamese':
                print("l_dataid0",l_dataid[2])
                request.session['l_dataid[2]'] = l_dataid[2]

                request.session['audio_recorded'] = True
                with open(json_ass, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[2]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter3.html", {"recording": True,"val":val })
            elif selected_option == 'Bengali':
                print("l_dataid0",l_dataid[2])
                request.session['l_dataid[2]'] = l_dataid[2]

                request.session['audio_recorded'] = True
                with open(json_ben, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[2]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter3.html", {"recording": True,"val":val })
            elif selected_option == 'Gujarati':
                print("l_dataid0",l_dataid[2])
                request.session['l_dataid[2]'] = l_dataid[2]

                request.session['audio_recorded'] = True
                with open(json_guj, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[2]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter3.html", {"recording": True,"val":val })
            elif selected_option == 'Marathi':
                print("l_dataid0",l_dataid[2])
                request.session['l_dataid[2]'] = l_dataid[2]

                request.session['audio_recorded'] = True
                with open(json_mar, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[2]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter3.html", {"recording": True,"val":val })
            elif selected_option == 'Kannada':
                print("l_dataid0",l_dataid[2])
                request.session['l_dataid[2]'] = l_dataid[2]

                request.session['audio_recorded'] = True
                with open(json_kan, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[2]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter3.html", {"recording": True,"val":val })
            elif selected_option == 'Malayalam':
                print("l_dataid0",l_dataid[2])
                request.session['l_dataid[2]'] = l_dataid[2]

                request.session['audio_recorded'] = True
                with open(json_mal, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[2]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter3.html", {"recording": True,"val":val })
            elif selected_option == 'Odiya':
                print("l_dataid0",l_dataid[2])
                request.session['l_dataid[2]'] = l_dataid[2]

                request.session['audio_recorded'] = True
                with open(json_odi, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[2]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter3.html", {"recording": True,"val":val })
            elif selected_option == 'Punjabi':
                print("l_dataid0",l_dataid[2])
                request.session['l_dataid[2]'] = l_dataid[2]

                request.session['audio_recorded'] = True
                with open(json_pun, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[2]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter3.html", {"recording": True,"val":val })
            elif selected_option == 'Tamil':
                print("l_dataid0",l_dataid[2])
                request.session['l_dataid[2]'] = l_dataid[2]

                request.session['audio_recorded'] = True
                with open(json_tami, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[2]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter3.html", {"recording": True,"val":val })
            elif selected_option == 'Telugu':
                print("l_dataid0",l_dataid[2])
                request.session['l_dataid[2]'] = l_dataid[2]

                request.session['audio_recorded'] = True
                with open(json_tel, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[2]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter3.html", {"recording": True,"val":val })
            elif selected_option == 'Urdu':
                print("l_dataid0",l_dataid[2])
                request.session['l_dataid[2]'] = l_dataid[2]

                request.session['audio_recorded'] = True
                with open(json_urdu, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[2]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter3.html", {"recording": True,"val":val })

        elif "record4" in request.POST:
            selected_option = request.session.get('selected_option')
            print("@",selected_option)
            if selected_option == 'English':

                print("l_dataid0",l_dataid[3])
                request.session['l_dataid[3]'] = l_dataid[3]

                request.session['audio_recorded'] = True
                with open(json_eng) as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[3]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter4.html", {"recording": True,"val":val })
            elif selected_option == 'Hindi':
                print("l_dataid0",l_dataid[3])
                request.session['l_dataid[3]'] = l_dataid[3]

                request.session['audio_recorded'] = True
                with open(json_hin, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[3]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter4.html", {"recording": True,"val":val })
            elif selected_option == 'Assamese':
                print("l_dataid0",l_dataid[3])
                request.session['l_dataid[3]'] = l_dataid[3]

                request.session['audio_recorded'] = True
                with open(json_ass, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[3]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter4.html", {"recording": True,"val":val })
            elif selected_option == 'Bengali':
                print("l_dataid0",l_dataid[3])
                request.session['l_dataid[3]'] = l_dataid[3]

                request.session['audio_recorded'] = True
                with open(json_ben, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[3]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter4.html", {"recording": True,"val":val })
            elif selected_option == 'Gujarati':
                print("l_dataid0",l_dataid[3])
                request.session['l_dataid[3]'] = l_dataid[3]

                request.session['audio_recorded'] = True
                with open(json_guj, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[3]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter4.html", {"recording": True,"val":val })
            elif selected_option == 'Marathi':
                print("l_dataid0",l_dataid[3])
                request.session['l_dataid[3]'] = l_dataid[3]

                request.session['audio_recorded'] = True
                with open(json_mar, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[3]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter4.html", {"recording": True,"val":val })
            elif selected_option == 'Kannada':
                print("l_dataid0",l_dataid[3])
                request.session['l_dataid[3]'] = l_dataid[3]

                request.session['audio_recorded'] = True
                with open(json_kan, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[3]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter4.html", {"recording": True,"val":val })
            elif selected_option == 'Malayalam':
                print("l_dataid0",l_dataid[3])
                request.session['l_dataid[3]'] = l_dataid[3]

                request.session['audio_recorded'] = True
                with open(json_mal, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[3]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter4.html", {"recording": True,"val":val })
            elif selected_option == 'Odiya':
                print("l_dataid0",l_dataid[3])
                request.session['l_dataid[3]'] = l_dataid[3]

                request.session['audio_recorded'] = True
                with open(json_odi, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[3]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter4.html", {"recording": True,"val":val })
            elif selected_option == 'Punjabi':
                print("l_dataid0",l_dataid[3])
                request.session['l_dataid[3]'] = l_dataid[3]

                request.session['audio_recorded'] = True
                with open(json_pun, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[3]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter4.html", {"recording": True,"val":val })
            elif selected_option == 'Tamil':
                print("l_dataid0",l_dataid[3])
                request.session['l_dataid[3]'] = l_dataid[3]

                request.session['audio_recorded'] = True
                with open(json_tami, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[3]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter4.html", {"recording": True,"val":val })
            elif selected_option == 'Telugu':
                print("l_dataid0",l_dataid[3])
                request.session['l_dataid[3]'] = l_dataid[3]

                request.session['audio_recorded'] = True
                with open(json_tel, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[3]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter4.html", {"recording": True,"val":val })
            elif selected_option == 'Urdu':
                print("l_dataid0",l_dataid[3])
                request.session['l_dataid[3]'] = l_dataid[3]

                request.session['audio_recorded'] = True
                with open(json_urdu, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[3]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter4.html", {"recording": True,"val":val })
        
        elif "record5" in request.POST:
            selected_option = request.session.get('selected_option')
            print("@",selected_option)
            if selected_option == 'English':
                print("l_dataid0",l_dataid[4])
                request.session['l_dataid[4]'] = l_dataid[4]

                request.session['audio_recorded'] = True
                with open(json_eng) as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[4]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter5.html", {"recording": True,"val":val })
            elif selected_option == 'Hindi':
                print("l_dataid0",l_dataid[4])
                request.session['l_dataid[4]'] = l_dataid[4]

                request.session['audio_recorded'] = True
                with open(json_hin, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[4]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter5.html", {"recording": True,"val":val })
            elif selected_option == 'Assamese':
                print("l_dataid0",l_dataid[4])
                request.session['l_dataid[4]'] = l_dataid[4]

                request.session['audio_recorded'] = True
                with open(json_ass, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[4]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter5.html", {"recording": True,"val":val })
            elif selected_option == 'Bengali':
                print("l_dataid0",l_dataid[4])
                request.session['l_dataid[4]'] = l_dataid[4]

                request.session['audio_recorded'] = True
                with open(json_ben, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[4]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter5.html", {"recording": True,"val":val })
            elif selected_option == 'Gujarati':
                print("l_dataid0",l_dataid[4])
                request.session['l_dataid[4]'] = l_dataid[4]

                request.session['audio_recorded'] = True
                with open(json_guj, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[4]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter5.html", {"recording": True,"val":val })
            elif selected_option == 'Marathi':
                print("l_dataid0",l_dataid[4])
                request.session['l_dataid[4]'] = l_dataid[4]

                request.session['audio_recorded'] = True
                with open(json_mar, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[4]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter5.html", {"recording": True,"val":val })
            elif selected_option == 'Kannada':
                print("l_dataid0",l_dataid[4])
                request.session['l_dataid[4]'] = l_dataid[4]

                request.session['audio_recorded'] = True
                with open(json_kan, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[4]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter5.html", {"recording": True,"val":val })
            elif selected_option == 'Malayalam':
                print("l_dataid0",l_dataid[4])
                request.session['l_dataid[4]'] = l_dataid[4]

                request.session['audio_recorded'] = True
                with open(json_mal, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[4]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter5.html", {"recording": True,"val":val })
            elif selected_option == 'Odiya':
                print("l_dataid0",l_dataid[4])
                request.session['l_dataid[4]'] = l_dataid[4]

                request.session['audio_recorded'] = True
                with open(json_odi, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[4]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter5.html", {"recording": True,"val":val })
            elif selected_option == 'Punjabi':
                print("l_dataid0",l_dataid[4])
                request.session['l_dataid[4]'] = l_dataid[4]

                request.session['audio_recorded'] = True
                with open(json_pun, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[4]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter5.html", {"recording": True,"val":val })
            elif selected_option == 'Tamil':
                print("l_dataid0",l_dataid[4])
                request.session['l_dataid[4]'] = l_dataid[4]

                request.session['audio_recorded'] = True
                with open(json_tami, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[4]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter5.html", {"recording": True,"val":val })
            elif selected_option == 'Telugu':
                print("l_dataid0",l_dataid[4])
                request.session['l_dataid[4]'] = l_dataid[4]

                request.session['audio_recorded'] = True
                with open(json_tel, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[4]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter5.html", {"recording": True,"val":val })
            elif selected_option == 'Urdu':
                print("l_dataid0",l_dataid[4])
                request.session['l_dataid[4]'] = l_dataid[4]

                request.session['audio_recorded'] = True
                with open(json_urdu, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    Letter = None
                    for d in data['Letter']:
                        if d['id'] == l_dataid[4]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_letter/retake_letter5.html", {"recording": True,"val":val })
            
            
    return redirect('letter_answer')

@csrf_exempt
def retake_letter(request):
    l_audio_files = request.session.setdefault('l_audio_files', [])
    l_copy_audio_files = request.session.get('l_copy_audio_files', [])

    l_audio_files_name = request.session.setdefault('l_audio_files_name', [])
    l_dataid = request.session.setdefault('l_dataid', [])


    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        print(val)
        request.session['l_dataid[0]'] = l_dataid[0]

        filename = l_dataid[0]+'.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
        for i, path in enumerate(l_copy_audio_files):
            if path == filepath:
                l_copy_audio_files[i] = filepath
            if len(l_copy_audio_files)<5:
                l_copy_audio_files.append(filepath)
            if len(l_copy_audio_files)==0:
                l_copy_audio_files.append(filepath)
            
        print("###",l_copy_audio_files)
        # if len(l_audio_files) < 5:
        #     l_audio_files.clear()
        #     l_audio_files_name.clear()

        request.session['filepath'] = filepath
        return render(request, 'letter_answer.html', { 'audio_url': filepath})
    
def save_letter1(request):
    l_dataid = request.session.setdefault('l_dataid', [])
    
    filepath = request.session.get('filepath')
    print(filepath)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    if selected_option == 'English':
        request.session['l_dataid[0]'] = l_dataid[0]
        print("data_id",l_dataid[0])
        with open(json_eng) as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[0]:
                    val = d['data']
                    break
    elif selected_option == 'Hindi':
        request.session['l_dataid[0]'] = l_dataid[0]
        print("data_id",l_dataid[0])
        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[0]:
                    val = d['data']
                    break
    elif selected_option == 'Assamese':
        request.session['l_dataid[0]'] = l_dataid[0]
        print("data_id",l_dataid[0])
        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[0]:
                    val = d['data']
                    break
    elif selected_option == 'Bengali':
        request.session['l_dataid[0]'] = l_dataid[0]
        print("data_id",l_dataid[0])
        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[0]:
                    val = d['data']
                    break
    elif selected_option == 'Gujarati':
        request.session['l_dataid[0]'] = l_dataid[0]
        print("data_id",l_dataid[0])
        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[0]:
                    val = d['data']
                    break
    elif selected_option == 'Marathi':
        request.session['l_dataid[0]'] = l_dataid[0]
        print("data_id",l_dataid[0])
        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[0]:
                    val = d['data']
                    break
    elif selected_option == 'Kannada':
        request.session['l_dataid[0]'] = l_dataid[0]
        print("data_id",l_dataid[0])
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[0]:
                    val = d['data']
                    break
    elif selected_option == 'Malayalam':
        request.session['l_dataid[0]'] = l_dataid[0]
        print("data_id",l_dataid[0])
        with open(json_mal, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[0]:
                    val = d['data']
                    break
    elif selected_option == 'Odiya':
        request.session['l_dataid[0]'] = l_dataid[0]
        print("data_id",l_dataid[0])
        with open(json_odi, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[0]:
                    val = d['data']
                    break
    elif selected_option == 'Punjabi':
        request.session['l_dataid[0]'] = l_dataid[0]
        print("data_id",l_dataid[0])
        with open(json_pun, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[0]:
                    val = d['data']
                    break
    elif selected_option == 'Tamil':
        request.session['l_dataid[0]'] = l_dataid[0]
        print("data_id",l_dataid[0])
        with open(json_tami, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[0]:
                    val = d['data']
                    break
    elif selected_option == 'Telugu':
        request.session['l_dataid[0]'] = l_dataid[0]
        print("data_id",l_dataid[0])
        with open(json_tel, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[0]:
                    val = d['data']
                    break
    elif selected_option == 'Urdu':
        request.session['l_dataid[0]'] = l_dataid[0]
        print("data_id",l_dataid[0])
        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[0]:
                    val = d['data']
                    break

    if val:
        print("the val",val)
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': selected_option ,'question':val}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    # lc_res=[]
    if response.status_code == 200:

        lc_res = request.session.setdefault('lc_res', [])
        if request.session.get("lc_res",None) is None:
            lc_res = []
        else:
            lc_res = request.session.get("lc_res")
            lc_res[0] = response.text
            # lc_res.clear()

            request.session["lc_res"] = lc_res
            print("testing the data", lc_res)
            if len(lc_res)==5:
                    request.session['lc_rec'] = lc_res
                    context = {'l_res': lc_res}
                    url = reverse('lans_page')
                    if len(lc_res)==5:
                        
                        return redirect(url,context)
    

@csrf_exempt
def retake_letter2(request):
    l_audio_files = request.session.setdefault('l_audio_files', [])
    l_copy_audio_files = request.session.get('l_copy_audio_files', [])

    l_audio_files_name = request.session.setdefault('l_audio_files_name', [])
    l_dataid = request.session.setdefault('l_dataid', [])


    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        print(val)
        request.session['l_dataid[1]'] = l_dataid[1]

        filename = l_dataid[1]+'.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
        for i, path in enumerate(l_copy_audio_files):
            if path == filepath:
                l_copy_audio_files[i] = filepath
            if len(l_copy_audio_files)<5:
                l_copy_audio_files.append(filepath)
            if len(l_copy_audio_files)==0:
                l_copy_audio_files.append(filepath)
        print("###",l_copy_audio_files)
        # if len(l_audio_files) < 5:
        #     l_audio_files.clear()
        #     l_audio_files_name.clear()

        request.session['filepath'] = filepath
        return render(request, 'letter_answer.html', { 'audio_url': filepath})
    
def save_letter2(request):
    l_dataid = request.session.setdefault('l_dataid', [])
    
    filepath = request.session.get('filepath')
    print(filepath)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    if selected_option == 'English':
        request.session['l_dataid[1]'] = l_dataid[1]
        print("data_id",l_dataid[1])
        with open(json_eng) as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[1]:
                    val = d['data']
                    break
    elif selected_option == 'Hindi':
        request.session['l_dataid[1]'] = l_dataid[1]
        print("data_id",l_dataid[1])
        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[1]:
                    val = d['data']
                    break
    elif selected_option == 'Assamese':
        request.session['l_dataid[1]'] = l_dataid[1]
        print("data_id",l_dataid[1])
        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[1]:
                    val = d['data']
                    break
    elif selected_option == 'Bengali':
        request.session['l_dataid[1]'] = l_dataid[1]
        print("data_id",l_dataid[1])
        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[1]:
                    val = d['data']
                    break
    elif selected_option == 'Gujarati':
        request.session['l_dataid[1]'] = l_dataid[1]
        print("data_id",l_dataid[1])
        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[1]:
                    val = d['data']
                    break
    elif selected_option == 'Marathi':
        request.session['l_dataid[1]'] = l_dataid[1]
        print("data_id",l_dataid[1])
        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[1]:
                    val = d['data']
                    break
    elif selected_option == 'Kannada':
        request.session['l_dataid[1]'] = l_dataid[1]
        print("data_id",l_dataid[1])
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[1]:
                    val = d['data']
                    break
    elif selected_option == 'Malayalam':
        request.session['l_dataid[1]'] = l_dataid[1]
        print("data_id",l_dataid[1])
        with open(json_mal, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[1]:
                    val = d['data']
                    break
    elif selected_option == 'Odiya':
        request.session['l_dataid[1]'] = l_dataid[1]
        print("data_id",l_dataid[1])
        with open(json_odi, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[1]:
                    val = d['data']
                    break
    elif selected_option == 'Punjabi':
        request.session['l_dataid[1]'] = l_dataid[1]
        print("data_id",l_dataid[1])
        with open(json_pun, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[1]:
                    val = d['data']
                    break
    elif selected_option == 'Tamil':
        request.session['l_dataid[1]'] = l_dataid[1]
        print("data_id",l_dataid[1])
        with open(json_tami, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[1]:
                    val = d['data']
                    break
    elif selected_option == 'Telugu':
        request.session['l_dataid[1]'] = l_dataid[1]
        print("data_id",l_dataid[1])
        with open(json_tel, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[1]:
                    val = d['data']
                    break
    elif selected_option == 'Urdu':
        request.session['l_dataid[1]'] = l_dataid[1]
        print("data_id",l_dataid[1])
        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[1]:
                    val = d['data']
                    break

    if val:
        print("the val",val)
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': selected_option,'question':val}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    # lc_res=[]
    if response.status_code == 200:

        lc_res = request.session.setdefault('lc_res', [])
        if request.session.get("lc_res",None) is None:
            lc_res = []
        else:
            lc_res = request.session.get("lc_res")
            lc_res[1] = response.text
            # lc_res.clear()

            request.session["lc_res"] = lc_res
            print("testing the data", lc_res)
            if len(lc_res)==5:
                    request.session['lc_rec'] = lc_res
                    context = {'l_res': lc_res}
                    url = reverse('lans_page')
                    if len(lc_res)==5:
                        
                        return redirect(url,context)


@csrf_exempt
def retake_letter3(request):
    l_audio_files = request.session.setdefault('l_audio_files', [])
    l_copy_audio_files = request.session.get('l_copy_audio_files', [])

    l_audio_files_name = request.session.setdefault('l_audio_files_name', [])
    l_dataid = request.session.setdefault('l_dataid', [])


    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        print(val)
        request.session['l_dataid[2]'] = l_dataid[2]

        filename = l_dataid[2]+'.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
        for i, path in enumerate(l_copy_audio_files):
            if path == filepath:
                l_copy_audio_files[i] = filepath
            if len(l_copy_audio_files)<5:
                l_copy_audio_files.append(filepath)
            if len(l_copy_audio_files)==0:
                l_copy_audio_files.append(filepath)
        print("###",l_copy_audio_files)
        # if len(l_audio_files) < 5:
        #     l_audio_files.clear()
        #     l_audio_files_name.clear()

        request.session['filepath'] = filepath
        return render(request, 'letter_answer.html', { 'audio_url': filepath})
    
def save_letter3(request):
    l_dataid = request.session.setdefault('l_dataid', [])
    
    filepath = request.session.get('filepath')
    print(filepath)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    if selected_option == 'English':
        request.session['l_dataid[2]'] = l_dataid[2]
        print("data_id",l_dataid[2])
        with open(json_eng) as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[2]:
                    val = d['data']
                    break
    elif selected_option == 'Hindi':
        request.session['l_dataid[2]'] = l_dataid[2]
        print("data_id",l_dataid[2])
        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[2]:
                    val = d['data']
                    break
    elif selected_option == 'Assamese':
        request.session['l_dataid[2]'] = l_dataid[2]
        print("data_id",l_dataid[2])
        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[2]:
                    val = d['data']
                    break
    elif selected_option == 'Bengali':
        request.session['l_dataid[2]'] = l_dataid[2]
        print("data_id",l_dataid[2])
        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[2]:
                    val = d['data']
                    break
    elif selected_option == 'Gujarati':
        request.session['l_dataid[2]'] = l_dataid[2]
        print("data_id",l_dataid[2])
        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[2]:
                    val = d['data']
                    break
    elif selected_option == 'Marathi':
        request.session['l_dataid[2]'] = l_dataid[2]
        print("data_id",l_dataid[2])
        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[2]:
                    val = d['data']
                    break
    elif selected_option == 'Kannada':
        request.session['l_dataid[2]'] = l_dataid[2]
        print("data_id",l_dataid[2])
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[2]:
                    val = d['data']
                    break
    elif selected_option == 'Malayalam':
        request.session['l_dataid[2]'] = l_dataid[2]
        print("data_id",l_dataid[2])
        with open(json_mal, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[2]:
                    val = d['data']
                    break
    elif selected_option == 'Odiya':
        request.session['l_dataid[2]'] = l_dataid[2]
        print("data_id",l_dataid[2])
        with open(json_odi, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[2]:
                    val = d['data']
                    break
    elif selected_option == 'Punjabi':
        request.session['l_dataid[2]'] = l_dataid[2]
        print("data_id",l_dataid[2])
        with open(json_pun, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[2]:
                    val = d['data']
                    break
    elif selected_option == 'Tamil':
        request.session['l_dataid[2]'] = l_dataid[2]
        print("data_id",l_dataid[2])
        with open(json_tami, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[2]:
                    val = d['data']
                    break
    elif selected_option == 'Telugu':
        request.session['l_dataid[2]'] = l_dataid[2]
        print("data_id",l_dataid[2])
        with open(json_tel, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[2]:
                    val = d['data']
                    break
    elif selected_option == 'Urdu':
        request.session['l_dataid[2]'] = l_dataid[2]
        print("data_id",l_dataid[2])
        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[2]:
                    val = d['data']
                    break

    if val:
        print("the val",val)
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': selected_option,'question':val}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    # lc_res=[]
    if response.status_code == 200:

        lc_res = request.session.setdefault('lc_res', [])
        if request.session.get("lc_res",None) is None:
            lc_res = []
        else:
            lc_res = request.session.get("lc_res")
            lc_res[2] = response.text
            # lc_res.clear()

            request.session["lc_res"] = lc_res
            print("testing the data", lc_res)
            if len(lc_res)==5:
                    request.session['lc_rec'] = lc_res
                    context = {'l_res': lc_res}
                    url = reverse('lans_page')
                    if len(lc_res)==5:
                        return redirect(url,context)



@csrf_exempt
def retake_letter4(request):
    l_audio_files = request.session.setdefault('l_audio_files', [])
    l_copy_audio_files = request.session.get('l_copy_audio_files', [])

    l_audio_files_name = request.session.setdefault('l_audio_files_name', [])
    l_dataid = request.session.setdefault('l_dataid', [])


    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        print(val)
        request.session['l_dataid[3]'] = l_dataid[3]

        filename = l_dataid[3]+'.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
        for i, path in enumerate(l_copy_audio_files):
            if path == filepath:
                l_copy_audio_files[i] = filepath
            if len(l_copy_audio_files)<5:
                l_copy_audio_files.append(filepath)
            if len(l_copy_audio_files)==0:
                l_copy_audio_files.append(filepath)
        print("###",l_copy_audio_files)
        # if len(l_audio_files) < 5:
        #     l_audio_files.clear()
        #     l_audio_files_name.clear()

        request.session['filepath'] = filepath
        return render(request, 'letter_answer.html', { 'audio_url': filepath})
    
def save_letter4(request):
    l_dataid = request.session.setdefault('l_dataid', [])
    
    filepath = request.session.get('filepath')
    print(filepath)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    if selected_option == 'English':
        request.session['l_dataid[3]'] = l_dataid[3]
        print("data_id",l_dataid[3])
        with open(json_eng) as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[3]:
                    val = d['data']
                    break
    elif selected_option == 'Hindi':
        request.session['l_dataid[3]'] = l_dataid[3]
        print("data_id",l_dataid[3])
        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[3]:
                    val = d['data']
                    break
    elif selected_option == 'Assamese':
        request.session['l_dataid[3]'] = l_dataid[3]
        print("data_id",l_dataid[3])
        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[3]:
                    val = d['data']
                    break
    elif selected_option == 'Bengali':
        request.session['l_dataid[3]'] = l_dataid[3]
        print("data_id",l_dataid[3])
        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[3]:
                    val = d['data']
                    break
    elif selected_option == 'Gujarati':
        request.session['l_dataid[3]'] = l_dataid[3]
        print("data_id",l_dataid[3])
        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[3]:
                    val = d['data']
                    break
    elif selected_option == 'Marathi':
        request.session['l_dataid[3]'] = l_dataid[3]
        print("data_id",l_dataid[3])
        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[3]:
                    val = d['data']
                    break
    elif selected_option == 'Kannada':
        request.session['l_dataid[3]'] = l_dataid[3]
        print("data_id",l_dataid[3])
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[3]:
                    val = d['data']
                    break
    elif selected_option == 'Malayalam':
        request.session['l_dataid[3]'] = l_dataid[3]
        print("data_id",l_dataid[3])
        with open(json_mal, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[3]:
                    val = d['data']
                    break
    elif selected_option == 'Odiya':
        request.session['l_dataid[3]'] = l_dataid[3]
        print("data_id",l_dataid[3])
        with open(json_odi, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[3]:
                    val = d['data']
                    break
    elif selected_option == 'Punjabi':
        request.session['l_dataid[3]'] = l_dataid[3]
        print("data_id",l_dataid[3])
        with open(json_pun, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[3]:
                    val = d['data']
                    break
    elif selected_option == 'Tamil':
        request.session['l_dataid[3]'] = l_dataid[3]
        print("data_id",l_dataid[3])
        with open(json_tami, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[3]:
                    val = d['data']
                    break
    elif selected_option == 'Telugu':
        request.session['l_dataid[3]'] = l_dataid[3]
        print("data_id",l_dataid[3])
        with open(json_tel, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[3]:
                    val = d['data']
                    break
    elif selected_option == 'Urdu':
        request.session['l_dataid[3]'] = l_dataid[3]
        print("data_id",l_dataid[3])
        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[3]:
                    val = d['data']
                    break

    if val:
        print("the val",val)
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': selected_option ,'question':val}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    # lc_res=[]
    if response.status_code == 200:

        lc_res = request.session.setdefault('lc_res', [])
        if request.session.get("lc_res",None) is None:
            lc_res = []
        else:
            lc_res = request.session.get("lc_res")
            lc_res[3] = response.text
            # lc_res.clear()

            request.session["lc_res"] = lc_res
            print("testing the data", lc_res)
            if len(lc_res)==5:
                    request.session['lc_rec'] = lc_res
                    context = {'l_res': lc_res}
                    url = reverse('lans_page')
                    if len(lc_res)==5:
                        return redirect(url,context)



@csrf_exempt
def retake_letter5(request):
    l_audio_files = request.session.setdefault('l_audio_files', [])
    l_copy_audio_files = request.session.get('l_copy_audio_files', [])

    l_audio_files_name = request.session.setdefault('l_audio_files_name', [])
    l_dataid = request.session.setdefault('l_dataid', [])


    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        print(val)
        request.session['l_dataid[4]'] = l_dataid[4]

        filename = l_dataid[4]+'.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
        for i, path in enumerate(l_copy_audio_files):
            if path == filepath:
                l_copy_audio_files[i] = filepath
            if len(l_copy_audio_files)<5:
                l_copy_audio_files.append(filepath)
            if len(l_copy_audio_files)<4:
                l_copy_audio_files.append(filepath)
        print("###",l_copy_audio_files)
        # if len(l_audio_files) < 5:
        #     l_audio_files.clear()
        #     l_audio_files_name.clear()

        request.session['filepath'] = filepath
        return render(request, 'letter_answer.html', { 'audio_url': filepath})
    
def save_letter5(request):
    l_dataid = request.session.setdefault('l_dataid', [])
    
    filepath = request.session.get('filepath')
    print(filepath)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    if selected_option == 'English':
        request.session['l_dataid[4]'] = l_dataid[4]
        print("data_id",l_dataid[4])
        with open(json_eng) as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[4]:
                    val = d['data']
                    break
    elif selected_option == 'Hindi':
        request.session['l_dataid[4]'] = l_dataid[4]
        print("data_id",l_dataid[4])
        with open(json_hin, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[4]:
                    val = d['data']
                    break
    elif selected_option == 'Assamese':
        request.session['l_dataid[4]'] = l_dataid[4]
        print("data_id",l_dataid[4])
        with open(json_ass, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[4]:
                    val = d['data']
                    break
    elif selected_option == 'Bengali':
        request.session['l_dataid[4]'] = l_dataid[4]
        print("data_id",l_dataid[4])
        with open(json_ben, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[4]:
                    val = d['data']
                    break
    elif selected_option == 'Gujarati':
        request.session['l_dataid[4]'] = l_dataid[4]
        print("data_id",l_dataid[4])
        with open(json_guj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[4]:
                    val = d['data']
                    break
    elif selected_option == 'Marathi':
        request.session['l_dataid[4]'] = l_dataid[4]
        print("data_id",l_dataid[4])
        with open(json_mar, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[4]:
                    val = d['data']
                    break
    elif selected_option == 'Kannada':
        request.session['l_dataid[4]'] = l_dataid[4]
        print("data_id",l_dataid[4])
        with open(json_kan, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[4]:
                    val = d['data']
                    break
    elif selected_option == 'Malayalam':
        request.session['l_dataid[4]'] = l_dataid[4]
        print("data_id",l_dataid[4])
        with open(json_mal, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[4]:
                    val = d['data']
                    break
    elif selected_option == 'Odiya':
        request.session['l_dataid[4]'] = l_dataid[4]
        print("data_id",l_dataid[4])
        with open(json_odi, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[4]:
                    val = d['data']
                    break
    elif selected_option == 'Punjabi':
        request.session['l_dataid[4]'] = l_dataid[4]
        print("data_id",l_dataid[4])
        with open(json_pun, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[4]:
                    val = d['data']
                    break
    elif selected_option == 'Tamil':
        request.session['l_dataid[4]'] = l_dataid[4]
        print("data_id",l_dataid[4])
        with open(json_tami, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[4]:
                    val = d['data']
                    break
    elif selected_option == 'Telugu':
        request.session['l_dataid[4]'] = l_dataid[4]
        print("data_id",l_dataid[4])
        with open(json_tel, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[4]:
                    val = d['data']
                    break
    elif selected_option == 'Urdu':
        request.session['l_dataid[4]'] = l_dataid[4]
        print("data_id",l_dataid[4])
        with open(json_urdu, 'r', encoding='utf-8') as f:
            data = json.load(f)
            Letter = None
            for d in data['Letter']:
                if d['id'] == l_dataid[4]:
                    val = d['data']
                    break

    if val:
        print("the val",val)
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': selected_option ,'question':val}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    # lc_res=[]
    if response.status_code == 200:

        lc_res = request.session.setdefault('lc_res', [])
        if request.session.get("lc_res",None) is None:
            lc_res = []
        else:
            lc_res = request.session.get("lc_res")
            # lc_res[4] = response.text
            if len(lc_res) ==5:
                lc_res[4] = response.text
            else:
                lc_res.insert(4, response.text)
            # lc_res.clear()

            request.session["lc_res"] = lc_res
            print("testing the data", lc_res)
            if len(lc_res)==5:
                    request.session['lc_rec'] = lc_res
                    context = {'l_res': lc_res}
                    url = reverse('lans_page')
                    if len(lc_res)==5:
                        return redirect(url,context)


def seventeen(request):     
    return render(request,'seventeen.html')

def word_msg(request):
    child_name = request.session.get('child_name')

    return render(request,'answer_word.html',{'child_name': child_name})

def next_answer(request):
    child_name = request.session.get('child_name')

    return render(request,'answer_story.html',{'child_name': child_name})

def word_ltr(request):
    child_name = request.session.get('child_name')

    return render(request,'answer_letter.html',{'child_name': child_name})

def word_beg(request):
    child_name = request.session.get('child_name')

    return render(request,'answer_beginer.html',{'child_name': child_name})

    
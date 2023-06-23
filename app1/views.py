import re
import os
import json
import time as t
from datetime import datetime
import random
import requests
import firebase_admin
from django.http import HttpResponseBadRequest
from django.urls import reverse
from django.shortcuts import render ,HttpResponse, redirect
from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from firebase_admin import credentials as fb_credentials,firestore
from dotenv import dotenv_values
from .models import Program, Aop_lan, Aop_sub_lan,MyModel,Avatar,MyUser
from django.utils.translation import gettext as _

dotenv_path = "../.env"
env_vars = dotenv_values(dotenv_path)

firebase_path = env_vars.get("Firebase_path")

cred = fb_credentials.Certificate(firebase_path)
firebase_admin.initialize_app(cred)

# Get a Firestore client
db = firestore.client()

doc_names = {
    'json_l1': 'ParakhData_English_L1',
    'json_l2': 'ParakhData_English_L2',
    'json_l3': 'ParakhData_English_L3',
    'json_l4': 'ParakhData_English_L4',
    'json_eng': 'ParakhData_English',
    'json_ben': 'ParakhData_Bengali',
    'json_guj': 'ParakhData_Gujarati',
    'json_hin': 'ParakhData_Hindi',
    'json_pun': 'ParakhData_Punjabi',
    'json_tml': 'ParakhData_Tamil',
    'json_knd': 'ParakhData_kannada',
    'json_mlm': 'ParakhData_malayalam',
    'json_mrt': 'ParakhData_marathi',
    'json_ody': 'ParakhData_odiya',
    'json_tlg': 'ParakhData_telugu',
    'json_urd': 'ParakhData_urdu',
	'json_advance_eng' : 'ParakhData_Advance_English_Program',
}

# Retrieve the document for each JSON file
json_data = {}
for key, doc_name in doc_names.items():
    # Get a reference to the document
    doc_ref = db.collection('ParakhApp').document(doc_name)
    
    # Retrieve the document
    doc = doc_ref.get()
    # Check if the document exists
    if doc.exists:
        # Access the document data
        json_data[key] = doc.to_dict()
    else:
        print(f"Document '{doc_name}' does not exist")

# Access the JSON data for each file
json_l1_data = json_data.get('json_l1')
json_l2_data = json_data.get('json_l2')
json_l3_data = json_data.get('json_l3')
json_l4_data = json_data.get('json_l4')
json_ben_data = json_data.get('json_ben')
json_eng_data = json_data.get('json_eng')
json_guj_data = json_data.get('json_guj')
json_hin_data = json_data.get('json_hin')
print('json hindi', type(json_hin_data))
json_pun_data = json_data.get('json_pun')
json_tml_data = json_data.get('json_tml')
json_knd_data = json_data.get('json_knd')
json_mlm_data = json_data.get('json_mlm')
json_mrt_data = json_data.get('json_mrt')
json_ody_data = json_data.get('json_ody')
json_tlg_data = json_data.get('json_tlg')
json_urd_data = json_data.get('json_urd')
json_advance_eng_data = json_data.get('json_advance_eng')
# print('json Advance english', json_advance_eng_data)

json_l1 = json_l1_data
json_l2 = json_l2_data
json_l3 = json_l3_data
json_l4 = json_l4_data
json_ass = os.path.join(settings.STATICFILES_DIRS[0], 'json/ParakhData_Assamese.json')
json_ben = json_ben_data
json_eng = json_eng_data
json_guj = json_guj_data
json_hin = json_hin_data
json_kan = json_knd_data
json_mal = json_mlm_data
json_mar = json_mrt_data
json_odi = json_ody_data
json_pun = json_pun_data
json_tami = json_tml_data
json_tel = json_tlg_data
json_urdu = json_urd_data
json_advance_eng = json_advance_eng_data

base_path = os.path.join(settings.MEDIA_ROOT, "")

from django.utils.translation import get_language, activate, gettext
def testing(request):
    # trans = _('Paragraph')
    trans = translate(language='hi')
    return render(request, 'testing.html', {'trans' : trans})

def translate(language):
    cur_language = get_language()
    try:
        activate(language)
        text = gettext('START')

    finally:
        activate(cur_language)
    return text

def first(request):
    options = Program.OPTION_CHOICES
    if request.method == 'POST':
        my_program = request.POST.get('option')
        request.session['my_program'] = my_program  # Save selected option in session
        if my_program == 'General Program':
            return redirect('login')
        elif my_program == 'AOP Program':
            return redirect('aop_language')
        elif my_program == 'Advance English Program':
            return redirect('aop_language')
    return render(request, 'home.html', {'options': options})


def aop_language(request):
    my_program = request.session.get('my_program')  # Retrieve selected option from session
    print('my_program is', my_program)
    request.session['my_language'] = 'English'
    if my_program == 'AOP Program':
        options = Aop_sub_lan.OPTION_CHOICES
        eng_option = Aop_lan.OPTION_CHOICES
    else:
        options = [(option, label) for option, label in Aop_sub_lan.OPTION_CHOICES if option in ['BL', 'EL']]
        eng_option = Aop_lan.OPTION_CHOICES

    if request.method == 'POST':
        selected_level = request.POST.get('options')
        print("selected_level", selected_level)

    return render(request, 'AOP_PRO/language.html', {'options': options, 'eng_option': eng_option})

def aop_num(request, selected_option, my_program):
    print("start_assesment", selected_option)
    print("selected_language", my_program)
    request.session['selected_option'] = selected_option
    request.session['my_program'] = my_program
    return render(request, 'AOP_PRO/search_num.html')


def red_start(request):
    selected_option = request.session.get('selected_option')
    print("selected_option", selected_option)
    selected_language = request.session.get('my_program')
    print("selected_language", selected_language)
    if request.method == 'GET':
        enrollment_id = request.GET.get('enrollment_id')
        print(enrollment_id)
        phone_number = request.session.get('phone_number')
        print("ph", phone_number)
        name = request.session.get('name')
        print("name", name)
        data = {}
        data["name"] = name
        data["profile_pic"] = ""
        data["platform"] = 'web'
        data["phone_number"] = phone_number
        data["enrollment_id"] = enrollment_id
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

    if selected_language == 'AOP Program':
        if "search" in request.POST:
            selected_option = request.session.get('selected_option')
            print('selected option', selected_option)
            mobile_number = request.POST['mobile_number']
            request.session['phone_number'] = mobile_number
            url = f'https://prajeevika.org/apis/aop/children-details.php?phone_number={mobile_number}&token=eyNsWgAdBF0KafwGPwOC9h5rWABTBuAKYxDxv8zRgJyuP'
            response = requests.get(url)
            print("####", response)
            print("response@@@@@@@@", response.text)
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

    else:
        if "search" in request.POST:
            selected_option = request.session.get('selected_option')
            print('selected option in red alert', selected_option)
            mobile_number = request.POST['mobile_number']
            request.session['phone_number'] = mobile_number
            url = f'https://prajeevika.org/apis/aop/children-details-dev.php?phone_number={mobile_number}&token=eyNsWgAdBF0KafwGPwOC9h5rWABTBuAKYxDxv8zRgJyuP'
            response = requests.get(url)
            print("####", response)
            print("response", response.text)
            try:
                data = json.loads(response.text)  # Parse the JSON response
                print('@@@@@@@@@@@@@@@@@@data', data)
                result_array = json.loads(data['result'])  # Parse the JSON array from the 'result' key

                if result_array:
                    first_child = result_array[0]
                    name = first_child['name']
                    request.session['name'] = name
                    status = first_child['status']
                    request.session['status'] = status
                    context = {
                        'data': result_array,  # Pass the result array as 'data'
                        'selected_option': selected_option,
                    }
                    return render(request, 'AOP_PRO/search_num.html', context)
                else:
                    context = {'error_message': 'Mobile number not found'}
                    return render(request, 'AOP_PRO/search_num.html', context)
            except (KeyError, IndexError):
                context = {'error_message': 'Mobile number not found'}
                return render(request, 'AOP_PRO/search_num.html', context)

        return render(request, 'AOP_PRO/search_num.html')


def msg_api_for_general_program(request):
    if "search" in request.POST:
        now = datetime.now()
        today_date = now.strftime("%Y-%m-%d")
        selected_option = request.session.get('selected_option')
        print('selected option',selected_option)
        enrollment_id = request.session.get('enrollment_id')
        print('enrollment_id',enrollment_id)
        id_value = request.session.get('id_value')
        print('id_value',id_value)
        my_program = request.session.get('my_program')
        print('my program for general program')
        url = f'https://prajeevika.org/apis/aop/update-result.php?token=eyNsWgAdBF0KafwGPwOC9h5rWABTBuAKYxDxv8zRgJyuP&enrollment_id={enrollment_id}&student_id={id_value}&assessment_type={selected_option}&assessment_date={today_date}&assessment_level=L1&program={my_program}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return redirect('/')
        else:
            return HttpResponse("Error: Invalid API response")


def msg_api(request):
    my_program = request.session.get('my_program')
    if my_program == 'Advance English Program':
        if "search" in request.POST:
            now = datetime.now()
            today_date = now.strftime("%Y-%m-%d")
            selected_option = request.session.get('selected_option')
            enrollment_id = request.session.get('enrollment_id')
            id_value = request.session.get('id_value')
            my_program = request.session.get('my_program')
            print('my program is',my_program)
            url = f'https://prajeevika.org/apis/aop/update-result.php?token=eyNsWgAdBF0KafwGPwOC9h5rWABTBuAKYxDxv8zRgJyuP&enrollment_id={enrollment_id}&student_id={id_value}&assessment_type={selected_option}&assessment_date={today_date}&assessment_level=L1&program={my_program}'
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
            # mobile_number = request.POST['mobile_number']
            # request.session['phone_number'] = mobile_number
            mobile_number = request.session.get('phone_number')
            print('mobile number',mobile_number)
            url = f'https://prajeevika.org/apis/aop/children-details-dev.php?phone_number={mobile_number}&token=eyNsWgAdBF0KafwGPwOC9h5rWABTBuAKYxDxv8zRgJyuP'
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                data_result = json.loads(data['result'])
                name = data_result[0]['name']
                request.session['name'] = name
                status = data_result[0]['status']
                request.session['status'] = status
                # Check if my_result is not empty before deleting the session
                if 'my_result' in request.session and len(request.session['my_result']) > 0:
                    del request.session['my_result']
                
                # Check if my_story_result is not empty before deleting the session
                if 'my_story_result' in request.session and len(request.session['my_story_result']) > 0:
                    del request.session['my_story_result']
                
                context = {
                    'data': data_result,
                    'selected_option': selected_option,
                }
                print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', context)
                return render(request, 'AOP_PRO/search_num.html', context)
            else:
                return render(request, 'Error/pages-500.html' )
    else:
        if "search" in request.POST:
            now = datetime.now()
            today_date = now.strftime("%Y-%m-%d")
            selected_option = request.session.get('selected_option')
            enrollment_id = request.session.get('enrollment_id')
            id_value = request.session.get('id_value')
            my_program = request.session.get('my_program')
            print('my program is',my_program)
            url = f'https://prajeevika.org/apis/aop/update-result.php?token=eyNsWgAdBF0KafwGPwOC9h5rWABTBuAKYxDxv8zRgJyuP&enrollment_id={enrollment_id}&student_id={id_value}&assessment_type={selected_option}&assessment_date={today_date}&assessment_level=L1&program={my_program}'
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
                print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', context)
                return render(request, 'AOP_PRO/search_num.html', context)
            else:
                return render(request, 'Error/pages-500.html' )


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
        my_program = request.session.get('my_program')  # Retrieve 'my_program' from session
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',my_program)
        data = {
            "name": child_name,
            "profile_pic": selected_image,
            "platform": 'web',
            "phone_number": mobile_number,
            "program": my_program  # Pass 'my_program' as 'program'
        }
        url = 'https://parakh.pradigi.org/v1/createprofile/'
        headers = {}
        response = requests.post(url, headers=headers, json=data)  # Use requests.post() with json parameter
        return redirect('select_profile')
    return render(request, 'chooseavtar.html')


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
    my_program = request.session.get('my_program')  # Retrieve selected language from session
    print('my_program is inside the language', my_program)

    if request.method == 'POST':
        selected_option = request.POST.get('option')
        print('@@@@@@@@@@@@@@@@@@@@@@@@', selected_option)
        selected_level = request.POST.get('options')
        print('#########################', selected_level)
        request.session['selected_level'] = selected_level

        choices = ['BL', 'ML1', 'ML2', 'EL']
        if selected_option in choices:
            url = reverse('aop_num', args=[selected_option, my_program])
        else:
            url = reverse('start_assesment', args=[selected_option])

        return redirect(url)

    return render(request, 'select_lan.html', {'child_name': child_name, 'avatar_url': avatar_image, 'options': options, 'eng_level': eng_level})


def aop_start_assesment(request):
    return render(request, 'AOP_PRO/six_one.html')

from django.contrib.sessions.backends.db import SessionStore
session = SessionStore()

def start_assesment(request, selected_option):
    my_program = request.session.get('my_program')  # Retrieve selected program from session
    print('my_program is', my_program)
    enrollment_id = request.session.get('enrollment_id')
    status = request.session.get('status')
    selected_level = request.session.get('selected_level')  # Retrieve selected level from session
    if my_program == 'Advance English Program':
        selected_option = f'{my_program} {selected_option}'  # Combine my_program and selected_option
        # selected_option = 'Advance English Program'
        session['selected_option'] = selected_option 
        print('selected option is in start assesment',selected_option)
        return render(request, 'start_assesment.html', {'selected_option': selected_option, 'selected_level': selected_level, 'status': status})
    else:
        request.session['selected_option'] = selected_option
        selected_option = request.session.get('selected_option')
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@', selected_option)
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@', selected_level)
        return render(request, 'start_assesment.html', {'selected_option': selected_option, 'selected_level': selected_level, 'status': status})


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
        data = json_eng
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break
    elif selected_option == 'BL':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        data = json_l1_data
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break
    else:
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        data = json_l1_data
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
    else:
        return render(request, 'Error/pages-500.html' )


@csrf_exempt
def save_file_bl(request):
    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        filename = f'{data_id}.wav'
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
    my_program = request.session.get('my_program')  # Retrieve selected option from session
    print('my_program is', my_program)
    if my_program == 'Advance English Program' and (selected_option == 'BL' or selected_option == 'EL'):
        json_file = json_advance_eng
        # print(json_file)
        data_id = request.session.get('data_id')
        print("data_id", data_id)
        data = json_file  # Assuming the desired data is directly under the 'json_file' variable
        para = None

        for d in data['Para']:  # Assuming the data is stored under the 'Paragraph' key
            if d['id'] == data_id:
                val = d['data']
                break
    elif selected_option == 'English':
        data_id = request.session.get('data_id')
        data = json_eng
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break
    elif selected_option == 'BL':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        data = json_l1_data
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break
    
    else: 
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        data = json_l1_data
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
    else:
        return render(request, 'Error/pages-500.html' )


def bl_retake(request):
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    media_folder = os.path.join(settings.MEDIA_ROOT)
    for file in os.listdir(media_folder):
        file_path = os.path.join(media_folder, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(e)

    my_program = request.session.get('my_program')
    if my_program == 'Advance English Program' :
        json_file = json_advance_eng
        # print(json_file)
        data_id = request.session.get('data_id')
        print("data_id", data_id)
        data = json_file  # Assuming the desired data is directly under the 'json_file' variable
        para = None

        for d in data['Para']:  # Assuming the data is stored under the 'Paragraph' key
            if d['id'] == data_id:
                val = d['data']
                break
    
    elif selected_option == 'English':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        request.session['audio_recorded'] = True
        data = json_eng
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break
    elif selected_option == 'BL':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        request.session['audio_recorded'] = True
       
        data = json_l1_data
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break

    if val:
        print("the val",val)
        if my_program == 'Advance English Program' :
            return render(request, "para_rec_next.html", {"recording": True,"val":val })
    return render(request, "AOP_PRO/bl_retake.html", {"recording": True,"val":val })
   

def bl_skip(request):
    selected_option = request.session.get('selected_option')
    print("@", selected_option)
    data_id = request.session.get('data_id')
    print("data_id", data_id)
    my_program = request.session.get('my_program')  # Retrieve selected option from session
    print('my_program is', my_program)
    if my_program == 'Advance English Program':
        json_file = json_advance_eng
        data = json_file  # Assuming the desired data is directly under the 'json_file' variable
        para = None

        for d in data['Para']:  # Assuming the data is stored under the 'Paragraph' key
            if d['id'] == data_id:
                request.session['data_id'] = data_id 
                print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',data_id)
                val = d['data']
                break
        
    else:
        data = json_l1_data
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break

    words = val.split()
    my_list = list(words)
    phone_number = request.session.get('phone_number')
    print("ph", phone_number)
    enrollment_id = request.session.get('enrollment_id')
    print("enrollment_id", enrollment_id)
    last_index = len(my_list)

    del_details = ', '.join([f"{i + 1}-{word}" for i, word in enumerate(my_list[1:])])
    print('del_details',del_details)

    sub_details_index = 0
    sub_details = f"{sub_details_index}-{my_list[sub_details_index]}"
    print('sub_details',sub_details)

    bl_response = {
        "no_mistakes": last_index,
        "no_del": last_index - 1,
        "del_details": del_details,
        "no_sub": 1,
        "sub_details": sub_details,
        "status": "success",
        "wcpm": 0.0,
        "text": "",
        "audio_url": "",
        "process_time": 0.7457363605499268
    }

    transcript = json.dumps(bl_response)
    request.session['transcript'] = transcript
    return render(request, 'AOP_PRO/bl_answer.html', {'originaltext': val, 'wcpm': None, 'no_mistakes': last_index, 'mobile_number': phone_number})





def bl_skip_next(request):
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    data_id = request.session.get('data_id')
    print("data_id",data_id)
    data = json_l1_data
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
    del_details = ', '.join([f"{i + 1}-{word}" for i, word in enumerate(my_list[1:])])
    print('del_details',del_details)

    sub_details_index = 0
    sub_details = f"{sub_details_index}-{my_list[sub_details_index]}"
    print('sub_details',sub_details)
    bl_response = {
        "no_mistakes": last_index,
        "no_del": last_index - 1,
        "del_details": del_details,
        "no_sub": 1,
        "sub_details": sub_details,
        "status": "success",
        "wcpm": 0.0,
        "text": "",
        "audio_url": "",
        "process_time": 0.7457363605499268
    }
    transcript = json.dumps(bl_response)
    request.session['transcript'] = transcript
    phone_number = request.session.get('phone_number')
    print("ph", phone_number)
    enrollment_id = request.session.get('enrollment_id')
    print("enrollment_id",enrollment_id)
    return render(request, 'AOP_PRO/bl_answer_final.html', {'originaltext':val ,'wcpm': None,'no_mistakes': last_index, 'mobile_number': phone_number,})
    

def bl_store(request):
    my_program = request.session.get('my_program')  # Retrieve selected program from session
    print('my_program is', my_program)
    if my_program == 'Advance English Program':
        my_language = request.session.get('my_language')  # Retrieve selected language from session
        print('my_language is', my_language)
        fluency_adjustment = request.POST.get('fluency_adjustment')
        number = int(fluency_adjustment)
        print("fluency_adjustment", fluency_adjustment)
        selected_option = my_language
        if selected_option == 'English':
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
            data_id = request.session.get('data_id')
            my_program = request.session.get('my_program')
            print('my program is saveprogress',my_program)
            data = json_advance_eng
            para = None
            for d in data['Para']:
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
            data["program"] = my_program
            url = 'https://parakh.pradigi.org/v1/saveprogress/'
            files = []
            payload = {'data': json.dumps(data)}
            headers = {}
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            
            if number <= 3:
                return redirect('bl_mcq_next')  # redirect to bl_mcq function
            else:
                context = {
                        'level' : "Sentence level"
                    }
                return render(request,"AOP_PRO/ans_page_aop.html", context=context) 
            
    else:
        request.method == 'POST'   
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
        data_id = request.session.get('data_id')
        my_program = request.session.get('my_program')
        print('my program is saveprogress',my_program)
        data = json_l1_data
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
        data["program"] = my_program
        url = 'https://parakh.pradigi.org/v1/saveprogress/'
        files = []
        payload = {'data': json.dumps(data)}
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        if fluency_adjustment == '0':
            return redirect('bl_mcq_next')  # redirect to bl_mcq function
        else:
            return redirect('bl_next') 


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
            print("student_id",id_value)
            data_id = request.session.get('data_id')
            print("sample_id",data_id)
            my_program = request.session.get('my_program')
            print('my program is saveprogress',my_program)
            data = json_l1_data
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
            data["program"] = my_program
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
                    'level' : "beginner"
                }
                return render(request, "AOP_PRO/ans_page_aop.html", context=context)
    except TypeError:
        return HttpResponse("Invalid adjustment value")

    
def get_random_sentence(request):
    
    selected_option = request.session.get('selected_option')
    print("get_random_sentence",selected_option)
    my_program = request.session.get('my_program')  # Retrieve selected program from session
    print('my_program is', my_program)
    if my_program == 'Advance English Program' and (selected_option == 'BL' or selected_option == 'EL'):
        data = json_advance_eng
        data_id = request.session.get('data_id')
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^data id new', data_id)
        selected_para = None  # Variable to store the selected paragraph
        for d in data['Para']:
            if d['id'] == data_id:  # Check if the current data_id matches the desired data_id
                print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^data id new', data_id)
                selected_para = d
                break
        
        if selected_para:
            # Continue with the selected paragraph and its associated data
            data_question = selected_para['questions']
            languages = data_question[0]['language']
            print('languages@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@', languages)
            question = data_question[0]['ques']
            print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@1st question for the para',question)
            # Update the data_id with the new value
            request.session['index'] = 0 
            data_id = selected_para['id']
            request.session['data_id'] = data_id
            print('data id updated', data_id)
            request.session['question'] = question 

            return {
                'data': question,
                'data_id': data_id,
                'languages': languages,
            }
    elif selected_option == 'BL':
        data = json_l1_data
        data1 = random.choice(data['Sentence'])
        print("the value ",data1['id'])
        data_id = data1['id']
        request.session['data_id'] = data_id
        print(data_id)
        print("dta",data1['data'])
        languages = data1['language']
        print('language in aop',languages)
        return {
            'data': data1['data'],
            'data_id': data_id,
            'languages': languages,
        }
    else:
        data = json_l1_data
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
    
    if request.method == 'POST':
        selected_lan = request.POST.get('selected_language_input')
        selecteddiv = request.session.get('selected-div')
        print('selecteddivtesting',selecteddiv)
        status = request.session.get('status')
        selected_language = request.POST.get('selected_language')
        # selected_div = request.POST.get('selected-div')
        selected_div = request.session.get('selected-ans')
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@selected_div',selected_div)
        data_id = request.session.get('data_id')
        # request.session['answer'] = answer
        answer = request.session.get('answer')
        print('###%%%%%%%%%%%%%%%#######################',answer)
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
        my_program = request.session.get('my_program')
        print('my program is saveprogress', my_program)
        print('text:', text)
        print('audio_url:', audio_url)
        print('process_time:', process_time)
        if my_program == 'Advance English Program' and (selected_option == 'BL' or selected_option == 'EL'):
            data = json_advance_eng
            # request.session['question'] = question 
            val = request.session.get('question')
            print('question added new is bhvfghf',val)

     
            selected_data = next((item for item in data['Para'] if item['id'] == data_id), None)
            # print('selected_data#######################################', selected_data)

            if selected_data:
                # question = val
                # question = question[1]

                if selected_language == 'hindi':
                    print("selected", 'hindi')
                    request.session['lan'] = selected_language
                elif selected_language == 'marathi':
                    print('selected', 'marathi')
                    request.session['lan'] = selected_language
                elif selected_language == 'English':
                    print('selected', 'English')
                    request.session['lan'] = selected_language
                else:
                    print("Invalid selected language")

                if selected_language in ['hindi', 'marathi', 'English']:
                    pass
                    # answer = question['language'][selected_language]['answers']
                    # print('answer is $$$$$$$$$$$$$$$$$$$$$$', answer)
                else:
                    print("Invalid selected language")
            else:
                print("Data not found for the given data_id")
            print("student_id", id_value)
            print("sample_id", data_id)
            print("level")
            print("section")
            print("question", val)
            print("answer", selected_div)
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
            print("test_type", status)
            print("next level", ans_next_level)
            print("correct_answer:", answer)
            print("answer_check_status:", "answer")
            lan = request.session.get('lan')
            print("lan", lan)
            data = {}
            data["student_id"] = id_value
            data["sample_id"] = "data_id"
            data["level"] = 'L1'
            data["question"] = val
            data["section "] = 'MCQ'
            data["answer"] = selected_div
            data["audio_url"] = ''
            data["mistakes_count"] = '0'
            data["no_mistakes"] = '0'
            data["no_mistakes_edited"] = '0'
            data["api_process_time"] = '0'
            data["language"] = 'English'
            data["no_del"] = '0'
            data["del_details"] = '0'
            data["no_sub"] = '0'
            data["sub_details"] = '0'
            data["test_type"] = status
            data["next_level"] = ans_next_level
            data["correct_answer"] = answer
            data["answer_check_status"] = 'true'
            data["mcq_language"] = lan
            data["program"] = my_program
            print(data)
            url = 'https://parakh.pradigi.org/v1/saveprogress/'
            files = []
            payload = {'data': json.dumps(data)}
            headers = {}
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            print('student_id', response.text)
            response_data = json.loads(response.text)
            print(response.text)
            index = request.session.get('index')
            indexing = request.session.get('indexing')
            my_result = request.session.get('my_result')
            print('###############myresult',my_result)
            my_result = sum(my_result)
            print('###############myresultsum',my_result)

            if index == 0:
                request.session['index'] = 1
                return redirect('bl_mcq_next_mcq')
            if indexing == 1:
                request.session['indexing'] = 2
                return redirect('bl_mcq_last')
            mcq_complete = request.session.get('mcq_complete')
            # if mcq_complete:
            #     return redirect('story')
            if my_result >= 2:
                return redirect('story')
            else:
                context = {
                        'level' : "Para Level Without Comprehension"
                    }
                return render(request,"AOP_PRO/ans_page_aop.html", context=context) 

            # del request.session['data_id']

            # Check if all three MCQs are completed
            # if response_data.get('status') == 'success' and response_data.get('msg') == 'completed':
            #     # Redirect to the story page
            #     return redirect('story_page')

            # Redirect to the next MCQ
            # return redirect('bl_mcq_next_mcq')


# def bl_mcq_api(request):
#     selected_option = request.session.get('selected_option')
#     selected_level = request.session.get('selected_level')
#     if request.method == 'POST':
#         selected_lan = request.POST.get('selected_language_input')
#         selecteddiv = request.session.get('selected-div')
#         status = request.session.get('status')
#         selected_language = request.POST.get('selected_language')
#         selected_div = request.POST.get('selected-div')
#         data_id = request.session.get('data_id')
#         id_value = request.session.get('id_value')
#         transcript = request.session.get('transcript')
#         transcript_dict = json.loads(transcript)
#         no_mistakes = transcript_dict.get('no_mistakes')
#         no_del = transcript_dict.get('no_del')
#         del_details = transcript_dict.get('del_details')
#         sub_details = transcript_dict.get('sub_details')
#         text = transcript_dict.get('text')
#         audio_url = transcript_dict.get('audio_url')
#         process_time = transcript_dict.get('process_time')
#         ans_next_level = request.session.get('ans_next_level')
#         my_program = request.session.get('my_program')
#         print('my program is saveprogress',my_program)
#         print('text:', text)
#         print('audio_url:', audio_url)
#         print('process_time:', process_time)
#         if my_program == 'Advance English Program' and selected_option == 'BL':
#             data = json_advance_eng
#             val = request.session.get('question')
#             for d in data['Para']:
#                 if d['id'] == data_id:
#                     val = d['data']
#                     break
#             selected_data = next((item for item in data['Para'] if item['id'] == data_id), None)
#             print('selected_data#######################################',selected_data)

#             if selected_data:
#                 question = selected_data['questions']
#                 question = question[0]

#                 if selected_language == 'hindi':
#                     print("selected", 'hindi')
#                     request.session['lan'] = selected_language
#                 elif selected_language == 'marathi':
#                     print('selected', 'marathi')
#                     request.session['lan'] = selected_language
#                 elif selected_language == 'English':
#                     print('selected', 'english')
#                     request.session['lan'] = selected_language
#                 else:
#                     print("Invalid selected language")

#                 if selected_language in ['hindi', 'marathi', 'English']:
#                     answer = question['language'][selected_language]['answers']
#                     print('answer is $$$$$$$$$$$$$$$$$$$$$$', answer)
#                 else:
#                     print("Invalid selected language")
#             else:
#                 print("Data not found for the given data_id")

            # data = json_advance_eng
            # val = request.session.get('question')
            # for d in data['Para']:
            #     if d['id'] == data_id:
            #         val = d['data']
            #         break
            
            # if selected_language == 'hindi':
            #         print("selected",'hindi')
            #         request.session['lan'] = selected_language
            # elif selected_language == 'marathi':
            #     print('selected','marathi')
            #     request.session['lan'] = selected_language

            # data = json_advance_eng
            # selected_data = next((item for item in data['Para'] if item['id'] == data_id), None)
            # print('selected_data#######################################',selected_data)

            # if selected_data:
            #     question = selected_data['questions']
            #     question = question[0]
                
            #     if selected_language == 'hindi' or selected_language == 'marathi':
            #         answer = question['language'][selected_language]['answers']
            #         print('answer is $$$$$$$$$$$$$$$$$$$$$$', answer)
            #     else:
            #         print("Invalid selected language")
            # else:
            #     print("Data not found for the given data_id")

            # if selected_language == 'hindi':
            #         # find the data with matching data_id
            #     data = json_advance_eng
            #     selected_data = next((item for item in data['Para'] if item['id'] == data_id), None)
            #     print('selected_data#######################################',selected_data)
            #     if selected_data:
            #         question = selected_data['questions']
            #         # languages = selected_data['language']
            #         # selected_language = languages.get(selected_language)
            #         # options = selected_language.get('options')
            #         # answer = selected_language.get('answers')
            #         question = question[0]
            #         answer = question['language'][selected_language]['answers']
            #         print('answer is $$$$$$$$$$$$$$$$$$$$$$', answer)
            #     else:
            #         print("Data not found for the given data_id")
            # elif selected_language == 'marathi':
            #     data = json_advance_eng
            #     # find the data with matching data_id
            #     selected_data = next((item for item in data['Para'] if item['id'] == data_id), None)
            #     print('selected_data##############################################',selected_data)
            #     if selected_data:
            #         question = selected_data['questions']
            #         print('question is $$$$$$$$$$$$$$$$$$$$$$',question)
            #         # languages = selected_data['language']
            #         # selected_language = languages.get(selected_language)
            #         # options = selected_language.get('options')
            #         # answer = selected_language.get('answers')
            #         question = question[0]
            #         answer = question['language'][selected_language]['answers']
            #         print('answer is $$$$$$$$$$$$$$$$$$$$$$', answer)

            #     else:
            #         print("Data not found for the given data_id")
            # print("student_id",id_value)
            # print("sample_id",data_id)
            # print("level")
            # print("section")
            # print("question",val)
            # print("answer",selected_div) 
            # print('audio_url:', audio_url)
            # print('mistakes_count', audio_url)
            # print('no_mistakes:', no_mistakes)
            # print('no_mistakes_edited', no_mistakes)
            # print('process_time:', process_time)
            # print('language:', 'English')
            # print('no_del:', no_del)
            # print('del_details:', del_details)
            # print('no_sub:', "no_sub")
            # print('sub_details:', sub_details)
            # print("test_type",status)
            # print("next level",ans_next_level)
            # print("correct_answer:", answer)
            # print("answer_check_status:", "answer")
            # lan = request.session.get('lan')
            # print("lan",lan)
            # data={}
            # data["student_id"]=id_value
            # data["sample_id"]= "data_id"
            # data["level"]= 'L1'
            # data["question"]= val
            # data["section "]= 'MCQ'
            # data["answer"]= selected_div
            # data["audio_url"]= ''
            # data["mistakes_count"]= '0'
            # data["no_mistakes"]= '0'
            # data["no_mistakes_edited"]= '0'
            # data["api_process_time"]= '0'
            # data["language"]= 'English'
            # data["no_del"]= '0'
            # data["del_details"]= '0'
            # data["no_sub"]= '0'
            # data["sub_details"]= '0'
            # data["test_type"]= status
            # data["next_level"]= ans_next_level
            # data["correct_answer"]= answer
            # data["answer_check_status"]= 'true'
            # data["mcq_language"]= lan
            # data["program"] = my_program
            # print(data)
            # url = 'https://parakh.pradigi.org/v1/saveprogress/'
            # files = []
            # payload = {'data': json.dumps(data)}
            # headers = {}
            # response = requests.request("POST", url, headers=headers, data=payload, files=files)
            # print('student_id', response.text)
            # response_data = json.loads(response.text)
            # print(response.text)
            # del request.session['data_id']
            # return redirect('bl_mcq1')

        else:
            data = json_l1_data
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
                    # find the data with matching data_id
                data = json_l1_data
                selected_data = next((item for item in data['Sentence'] if item['id'] == data_id), None)
                if selected_data:
                    languages = selected_data['language']
                    selected_language = languages.get(selected_language)
                    options = selected_language.get('options')
                    answer = selected_language.get('answers')
                else:
                    print("Data not found for the given data_id")
            elif selected_language == 'marathi':
                data = json_l1_data
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
            data["program"] = my_program
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
        request.session['selected-ans'] = selected_div
        selected_language = request.POST.get('selected_language')
        context['selected_language'] = selected_language
        print('selected_language', selected_language)
        if selected_language in ['English', 'hindi', 'marathi']:
            data = context['val']
            languages = context['languages']
            
            # Get the answer for the selected language
            answer = languages[selected_language]['answers']
            
            print('answer is', answer)
            request.session['answer'] = answer
        else:
            print('Invalid selected language')

        my_result = request.session.get('my_result', []) # Retrieve existing my_result from session
        if selected_div == answer:
            my_result.append(1)
        print('my_result**********************',my_result)
        request.session['my_result'] = my_result 

        my_program = request.session.get('my_program')  # Retrieve selected program from session
        print('my_program is', my_program)
        if my_program == 'Advance English Program':
            return render(request, "Advance/bl_mcq_next.html", context)
    context['selected_div'] = context.get('selected_div')  # Add selected_div to context
    return render(request, "AOP_PRO/bl_mcq.html", context)


def bl_mcq_next_mcq(request):
    # selected_option = request.session.get('selected_option')
    # print("@",selected_option)
    # selected_level = request.session.get('selected_level')
    # print("@",selected_level)
    data = get_random_sentence1(request)
    context = {"val": data['data'], "recording": True, "data_id": data['data_id'], "languages": data['languages']}
    print('##########context###############',context)
    request.session['my_context'] = context
    
    phone_number = request.session.get('phone_number')
    print("ph", phone_number)
    enrollment_id = request.session.get('enrollment_id')
    print("enrollment_id",enrollment_id)
    my_program = request.session.get('my_program')  # Retrieve selected program from session
    print('my_program is', my_program)
    if my_program == 'Advance English Program':
        return render(request, "Advance/bl_mcq.html", context)
    # if request.method == 'POST':
    return redirect('bl_mcq_last')
    # return render(request, "AOP_PRO/bl_mcq_next.html", context)

def get_random_sentence1(request):
    selected_option = request.session.get('selected_option')
    print("get_random_sentence",selected_option)
    my_program = request.session.get('my_program')  # Retrieve selected program from session
    print('my_program is', my_program)
    if my_program == 'Advance English Program' and (selected_option == 'BL' or selected_option == 'EL'):
        data = json_advance_eng
        data_id = request.session.get('data_id')
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^data id new', data_id)
        selected_para = None  # Variable to store the selected paragraph
        for d in data['Para']:
            if d['id'] == data_id:  # Check if the current data_id matches the desired data_id
                print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^data id new', data_id)
                selected_para = d
                break
        
        if selected_para:
            # Continue with the selected paragraph and its associated data
            data_question = selected_para['questions']
            languages = data_question[1]['language']
            print('languages@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@', languages)
            question = data_question[1]['ques']
            print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@1st question for the para',question)
            # Update the data_id with the new value
            data_id = selected_para['id']
            request.session['indexing'] = 1 
            request.session['data_id'] = data_id
            print('data id updated', data_id)
            request.session['question'] = question
            # selected_language = 'English'  # Replace with your logic to get the selected language

            # if selected_language in languages:
            #     answer = languages[selected_language]['answers']
            #     print('answer is $$$$$$$$$$$$$$$$$$$$$$', answer)
            #     request.session['answer'] = answer 

            return {
                'data': question,
                'data_id': data_id,
                'languages': languages,
            }
        
def bl_mcq_last(request):
    data = get_random_sentence2(request)
    context = {"val": data['data'], "recording": True, "data_id": data['data_id'], "languages": data['languages']}
    request.session['my_context'] = context
    phone_number = request.session.get('phone_number')
    print("ph", phone_number)
    enrollment_id = request.session.get('enrollment_id')
    print("enrollment_id",enrollment_id)
    my_program = request.session.get('my_program')  # Retrieve selected program from session
    print('my_program is', my_program)
    if my_program == 'Advance English Program':
        return render(request, "Advance/bl_mcq.html", context)
    # if request.method == 'POST':
    return redirect('bl_mcq_last')


def get_random_sentence2(request):
    selected_option = request.session.get('selected_option')
    print("get_random_sentence",selected_option)
    my_program = request.session.get('my_program')  # Retrieve selected program from session
    print('my_program is', my_program)
    if my_program == 'Advance English Program' and (selected_option == 'BL' or selected_option == 'EL'):
        data = json_advance_eng
        data_id = request.session.get('data_id')
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^data id new', data_id)
        selected_para = None  # Variable to store the selected paragraph
        for d in data['Para']:
            if d['id'] == data_id:  # Check if the current data_id matches the desired data_id
                print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^data id new', data_id)
                selected_para = d
                break
        
        if selected_para:
            # Continue with the selected paragraph and its associated data
            data_question = selected_para['questions']
            languages = data_question[2]['language']
            print('languages@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@', languages)
            question = data_question[2]['ques']
            print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@1st question for the para',question)
            # Update the data_id with the new value
            data_id = selected_para['id']
            request.session['data_id'] = data_id
            print('data id updated', data_id)
            request.session['question'] = question
            mcq_complete = 3
            request.session['mcq_complete'] = mcq_complete
            # selected_language = 'English'  # Replace with your logic to get the selected language

            # if selected_language in languages:
            #     answer = languages[selected_language]['answers']
            #     print('answer is $$$$$$$$$$$$$$$$$$$$$$', answer)
            #     request.session['answer'] = answer 
            

            return {
                'data': question,
                'data_id': data_id,
                'languages': languages,
            }


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
    print('val:', context['val'])
    print('recording:', context['recording'])
    print('data_id:', context['data_id'])
    print('languages:', context['languages'])
    request.session['my_context'] = context
    phone_number = request.session.get('phone_number')
    print("ph", phone_number)
    enrollment_id = request.session.get('enrollment_id')
    print("enrollment_id",enrollment_id)
    my_program = request.session.get('my_program')  # Retrieve selected program from session
    print('my_program is', my_program)
    if my_program == 'Advance English Program':
        return render(request, "Advance/bl_mcq.html", context)
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


def error_recording(request):
    if request.method == 'GET':
        data_id = request.session.get('data_id')
        print("data_id", data_id)
        data = json_l1_data
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
    paragraph = request.session.get('paragraph')
    print("######",paragraph)
    return render(request, "AOP_PRO/bl_recording.html",{'val': paragraph})


#############################################################################################

def get_random_ml1(request):
    selected_option = request.session.get('selected_option')
    data = json_l1_data
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
    my_program = request.session.get('my_program')  # Retrieve selected program from session
    print('my_program is', my_program)
    if my_program == 'Advance English Program' and (selected_option == 'BL' or selected_option == 'EL'):
        data = json_advance_eng
        data_id = request.session.get('data_id')
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^data id new', data_id)
        selected_para = None  # Variable to store the selected paragraph
        for d in data['Story']:
            if d['id'] == data_id:  # Check if the current data_id matches the desired data_id
                print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^data id new', data_id)
                selected_para = d
                break
        
        if selected_para:
            # Continue with the selected paragraph and its associated data
            data_question = selected_para['questions']
            languages = data_question[0]['language']
            print('languages@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@', languages)
            question = data_question[0]['ques']
            print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@1st question for the para',question)
            # Update the data_id with the new value
            request.session['index'] = 0 
            data_id = selected_para['id']
            request.session['data_id'] = data_id
            print('data id updated', data_id)
            request.session['question'] = question

            return {
                'data': question,
                'data_id': data_id,
                'languages': languages,
            }
    elif selected_option == 'ML1':
        data = json_l2
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
            data = json_l2_data
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
        data = json_eng
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break
    elif selected_option == 'BL':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        data = json_l2_data
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break
    
    data_id = request.session.get('data_id')
    print("data_id",data_id)
    data = json_l2_data
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
    else:
        return render(request, 'Error/pages-500.html' )


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
    
    data_id = request.session.get('data_id')
    print("data_id",data_id)
    my_program = request.session.get('my_program')
    if my_program == 'Advance English Program':
        data = json_advance_eng
        Story = None
        for d in data['Story']:
            if d['id'] == data_id:
                val = d['data']
                print('Val@@@@@@@@@@@@@@@@@@@@val',val)
                break
    else:
        data = json_l1_data
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
    else:
        return render(request, 'Error/pages-500.html' )


def ml1_retake(request):
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    media_folder = os.path.join(settings.MEDIA_ROOT)
    for file in os.listdir(media_folder):
        file_path = os.path.join(media_folder, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
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
    my_program = request.session.get('my_program')
    if my_program == 'Advance English Program' :
        data = json_advance_eng
        paragraph = None
        for d in data['Story']:
            if d['id'] == data_id:
                val = d['data']
                break

    # with open(json_l2, 'r', encoding='utf-8') as f:
    #     data = json.load(f)
    else:
        data = json_l2_data
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
    if my_program == 'Advance English Program' :
        return render(request, "story_rec_next.html", {"recording": True,"val":val })
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
    data = json_l2_data
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
    del_details = ', '.join([f"{i + 1}-{word}" for i, word in enumerate(my_list[1:])])
    print('del_details',del_details)

    sub_details_index = 0
    sub_details = f"{sub_details_index}-{my_list[sub_details_index]}"
    print('sub_details',sub_details)
    ml1_response = {
        "no_mistakes": last_index,
        "no_del": last_index - 1,
        "del_details": del_details,
        "no_sub": 1,
        "sub_details": sub_details,
        "status": "success",
        "wcpm": 0.0,
        "text": "",
        "audio_url": "",
        "process_time": 0.7457363605499268
    }
    transcript = json.dumps(ml1_response)
    request.session['ml1_res'] = transcript
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
        data = json_l2_data
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
        del_details = ', '.join([f"{i + 1}-{word}" for i, word in enumerate(my_list[1:])])
        print('del_details',del_details)

        sub_details_index = 0
        sub_details = f"{sub_details_index}-{my_list[sub_details_index]}"
        print('sub_details',sub_details)
        ml1_response = {
            "no_mistakes": last_index,
            "no_del": last_index - 1,
            "del_details": del_details,
            "no_sub": 1,
            "sub_details": sub_details,
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
    my_program = request.session.get('my_program')
    if my_program == 'Advance English Program':
        data = json_advance_eng
        try:
            fluency_adjustment = request.POST.get('fluency_adjustment')
            number = int(fluency_adjustment)
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
            my_program = request.session.get('my_program')
            print('my program is saveprogress',my_program)
            
            data = json_advance_eng
            Story = None
            for d in data['Story']:
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
            data["program"] = my_program
            print(data)
            url = 'https://parakh.pradigi.org/v1/saveprogress/'
            files = []
            payload = {'data': json.dumps(data)}
            headers = {}
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            response_data = json.loads(response.text)
            print(response_data)
            print(fluency_adjustment)
            # if fluency_adjustment == '0':
            #     return redirect('ml1_mcq_next')  # redirect to bl_mcq function
            # else:
            #     return redirect('ml1_next')

            if number < 3:
                return redirect('ml1_mcq_next')  # redirect to bl_mcq function
            else:
                context = {
                        'level' : "Para Level With Comprehension"
                    }
                return render(request,"AOP_PRO/ans_page_aop.html", context=context) 
        except TypeError:
            return HttpResponse("Invalid adjustment value")
    else:    
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
            my_program = request.session.get('my_program')
            print('my program is saveprogress',my_program)
            
            data = json_l1_data
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
            data["program"] = my_program
            print(data)
            url = 'https://parakh.pradigi.org/v1/saveprogress/'
            files = []
            payload = {'data': json.dumps(data)}
            headers = {}
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            response_data = json.loads(response.text)
            print(response.text)
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
        my_program = request.session.get('my_program')
        print('my program is saveprogress',my_program)

        data = json_l1_data
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
        data["program"] = my_program

        print(data)
        url = 'https://parakh.pradigi.org/v1/saveprogress/'
        files = []
        payload = {'data': json.dumps(data)}
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        # print('student_id', response.text)
        response_data = json.loads(response.text)
        print(response.text)
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
                'level' : "L1-sentence"
            }
            return render(request, "AOP_PRO/ans_page_aop.html", context=context)
    except TypeError:
        return HttpResponse("Invalid adjustment value")


def ml1_final_mcq(request):
    context = request.session.get('ml1_context', {})
    print("contextWWWWWWWWWWWWWWWWWWW", context)
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
        request.session['selected-ans'] = selected_div
        if selected_language in ['English', 'hindi', 'marathi']:
            data = context['val']
            languages = context['languages']
            
            # Get the answer for the selected language
            answer = languages[selected_language]['answers']
            
            print('answer isdfgdskmgskdngksdgsdvfaf', answer)
            request.session['answer'] = answer
        else:
            print('Invalid selected language')

        my_story_result = request.session.get('my_story_result', []) # Retrieve existing my_result from session
        if selected_div == answer:
            my_story_result.append(1)
        print('my_story_result**********************',my_story_result)
        request.session['my_story_result'] = my_story_result

        my_program = request.session.get('my_program')
        if my_program == 'Advance English Program':
            return render(request, "Advance/ml1_mcq_next.html", context)
        return render(request, "AOP_PRO/ml1_mcq.html", context)
    return render(request, "AOP_PRO/ml1_mcq.html", context)

####################################################################################################################

def bl_story_mcq_next_mcq(request):
    # selected_option = request.session.get('selected_option')
    # print("@",selected_option)
    # selected_level = request.session.get('selected_level')
    # print("@",selected_level)
    data = get_random_sentence4(request)
    context = {"val": data['data'], "recording": True, "data_id": data['data_id'], "languages": data['languages']}
    request.session['ml1_context'] = context
    phone_number = request.session.get('phone_number')
    print("ph", phone_number)
    enrollment_id = request.session.get('enrollment_id')
    print("enrollment_id",enrollment_id)
    my_program = request.session.get('my_program')  # Retrieve selected program from session
    print('my_program is', my_program)
    if my_program == 'Advance English Program':
        return render(request, "Advance/ml1_mcq.html", context)
    # if request.method == 'POST':
    return redirect('bl_mcq_last')
    # return render(request, "AOP_PRO/bl_mcq_next.html", context)

def get_random_sentence4(request):
    selected_option = request.session.get('selected_option')
    print("get_random_sentence",selected_option)
    my_program = request.session.get('my_program')  # Retrieve selected program from session
    print('my_program is', my_program)
    if my_program == 'Advance English Program' and (selected_option == 'BL' or selected_option == 'EL'):
        data = json_advance_eng
        data_id = request.session.get('data_id')
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^data id new', data_id)
        selected_para = None  # Variable to store the selected paragraph
        for d in data['Story']:
            if d['id'] == data_id:  # Check if the current data_id matches the desired data_id
                print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^data id new', data_id)
                selected_para = d
                break
        
        if selected_para:
            # Continue with the selected paragraph and its associated data
            data_question = selected_para['questions']
            languages = data_question[1]['language']
            print('languages@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@', languages)
            question = data_question[1]['ques']
            print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@1st question for the para',question)
            # Update the data_id with the new value
            data_id = selected_para['id']
            request.session['indexing'] = 1 
            request.session['data_id'] = data_id
            print('data id updated', data_id)
            request.session['question'] = question 

            return {
                'data': question,
                'data_id': data_id,
                'languages': languages,
            }
        
def bl_story_mcq_last(request):
    data = get_random_sentence5(request)
    context = {"val": data['data'], "recording": True, "data_id": data['data_id'], "languages": data['languages']}
    request.session['ml1_context'] = context
    phone_number = request.session.get('phone_number')
    print("ph", phone_number)
    enrollment_id = request.session.get('enrollment_id')
    print("enrollment_id",enrollment_id)
    my_program = request.session.get('my_program')  # Retrieve selected program from session
    print('my_program is', my_program)
    if my_program == 'Advance English Program':
        return render(request, "Advance/ml1_mcq.html", context)
    # if request.method == 'POST':
    return redirect('bl_mcq_last')


def get_random_sentence5(request):
    selected_option = request.session.get('selected_option')
    print("get_random_sentence",selected_option)
    my_program = request.session.get('my_program')  # Retrieve selected program from session
    print('my_program is', my_program)
    if my_program == 'Advance English Program' and (selected_option == 'BL' or selected_option == 'EL'):
        data = json_advance_eng
        data_id = request.session.get('data_id')
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^data id new', data_id)
        selected_para = None  # Variable to store the selected paragraph
        for d in data['Story']:
            if d['id'] == data_id:  # Check if the current data_id matches the desired data_id
                print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^data id new', data_id)
                selected_para = d
                break
        
        if selected_para:
            # Continue with the selected paragraph and its associated data
            data_question = selected_para['questions']
            languages = data_question[2]['language']
            print('languages@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@', languages)
            question = data_question[2]['ques']
            print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@1st question for the para',question)
            # Update the data_id with the new value
            data_id = selected_para['id']
            request.session['data_id'] = data_id
            print('data id updated', data_id)
            mcq_complete = 3
            request.session['mcq_complete'] = mcq_complete
            request.session['question'] = question 

            return {
                'data': question,
                'data_id': data_id,
                'languages': languages,
            }



##########################################################################################################################
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
    my_program = request.session.get('my_program')  # Retrieve selected program from session
    print('my_program is', my_program)
    if my_program == 'Advance English Program':
        return render(request, "Advance/ml1_mcq.html", context)

    if request.method == 'POST':
        transcript = request.session.get('transcript')
        print("transcript",transcript)
        return redirect('ml2')
    return render(request, "AOP_PRO/ml1_mcq_next.html", context)


def ml1_mcq_api(request):
    selected_option = request.session.get('selected_option')
    selected_level = request.session.get('selected_level')

    if request.method == 'POST':
        selected_lan = request.POST.get('selected_language_input')
        print("lan",selected_lan)
        status = request.session.get('status')
        selected_language = request.POST.get('selected_language')
        # selected_div = request.POST.get('selected-div')
        # print("#################################################################")
        data_id = request.session.get('data_id')
        print(data_id)
        selected_div = request.session.get('selected-ans')
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@selected_div',selected_div)
        answer = request.session.get('answer')
        print('###%%%%%%%%%%%%%%%#######################',answer)
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
        my_program = request.session.get('my_program')
        print('my program is saveprogress',my_program)
        print('text:', text)
        print('audio_url:', audio_url)
        print('process_time:', process_time)

        if my_program == 'Advance English Program' and (selected_option == 'BL' or selected_option == 'EL'):
            data = json_advance_eng
            val = request.session.get('question')
            # for d in data['Story']:
            #     if d['id'] == data_id:
            #         print('data_id#######################################', data_id)
            #         val = d['data']
            #         break
            selected_data = next((item for item in data['Story'] if item['id'] == data_id), None)
            print('selected_data#######################################', selected_data)

            if selected_data:
                # question = selected_data['questions']
                # question = question[0]

                if selected_language == 'hindi':
                    print("selected", 'hindi')
                    request.session['lan'] = selected_language
                elif selected_language == 'marathi':
                    print('selected', 'marathi')
                    request.session['lan'] = selected_language
                elif selected_language == 'English':
                    print('selected', 'English')
                    request.session['lan'] = selected_language
                else:
                    print("Invalid selected language")

                if selected_language in ['hindi', 'marathi', 'English']:
                    pass
                    # answer = question['language'][selected_language]['answers']
                    # print('answer is $$$$$$$$$$$$$$$$$$$$$$', answer)
                else:
                    print("Invalid selected language")
            else:
                print("Data not found for the given data_id")
            print("student_id", id_value)
            print("sample_id", data_id)
            print("level")
            print("section")
            print("question", val)
            print("answer", selected_div)
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
            print("test_type", status)
            print("next level", ans_next_level)
            print("correct_answer:", answer)
            print("answer_check_status:", "answer")
            lan = request.session.get('lan')
            print("lan", lan)
            data = {}
            data["student_id"] = id_value
            data["sample_id"] = "data_id"
            data["level"] = 'L1'
            data["question"] = val
            data["section "] = 'MCQ'
            data["answer"] = selected_div
            data["audio_url"] = ''
            data["mistakes_count"] = '0'
            data["no_mistakes"] = '0'
            data["no_mistakes_edited"] = '0'
            data["api_process_time"] = '0'
            data["language"] = 'English'
            data["no_del"] = '0'
            data["del_details"] = '0'
            data["no_sub"] = '0'
            data["sub_details"] = '0'
            data["test_type"] = status
            data["next_level"] = ans_next_level
            data["correct_answer"] = answer
            data["answer_check_status"] = 'true'
            data["mcq_language"] = lan
            data["program"] = my_program
            print(data)
            url = 'https://parakh.pradigi.org/v1/saveprogress/'
            files = []
            payload = {'data': json.dumps(data)}
            headers = {}
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            print('student_id', response.text)
            response_data = json.loads(response.text)
            print(response.text)
            index = request.session.get('index')
            indexing = request.session.get('indexing')

            if index == 0:
                request.session['index'] = 1
                return redirect('bl_story_mcq_next_mcq')
            if indexing == 1:
                request.session['indexing'] = 2
                return redirect('bl_story_mcq_last')
            # mcq_complete = request.session.get('mcq_complete')
            # if mcq_complete:
            #     return HttpResponse('flow completed for story')
            my_story_result = request.session.get('my_story_result')
            my_story_result = sum(my_story_result)

            if my_story_result >= 2:
                context = {
                        'level' : "Story Level With Comprehension"
                    }
                return render(request,"AOP_PRO/ans_page_aop.html", context=context) 
            else:
                context = {
                        'level' : "Story Level Without Comprehension"
                    }
                return render(request,"AOP_PRO/ans_page_aop.html", context=context) 
        else:    
            data = json_l2_data
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
                    data = json_l2_data
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
                    data = json_l2_data
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
            data["program"] = my_program
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
  
    
#############################################################################################

def get_random_ml2(request):
        data = json_l3_data
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
            data = json_l3_data
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
        data = json_l3_data
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
    data_id = request.session.get('data_id')
    print("data_id",data_id)
    data = json_l2_data
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
    else:
        return render(request, 'Error/pages-500.html' )


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
    data_id = request.session.get('data_id')
    print("data_id",data_id)
    data = json_l2_data
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
    else:
        return render(request, 'Error/pages-500.html' )


def ml2_retake(request):
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    media_folder = os.path.join(settings.MEDIA_ROOT)
    for file in os.listdir(media_folder):
        file_path = os.path.join(media_folder, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(e)

    data_id = request.session.get('data_id')
    print("data_id",data_id)
    request.session['audio_recorded'] = True
    data = json_l2_data
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
        data = json_l3_data
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
        del_details = ', '.join([f"{i + 1}-{word}" for i, word in enumerate(my_list[1:])])
        print('del_details',del_details)

        sub_details_index = 0
        sub_details = f"{sub_details_index}-{my_list[sub_details_index]}"
        print('sub_details',sub_details)
        ml2_response = {
            "no_mistakes": last_index,
            "no_del": last_index - 1,
            "del_details": del_details,
            "no_sub": 1,
            "sub_details": sub_details,
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
        data = json_l3_data
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
        del_details = ', '.join([f"{i + 1}-{word}" for i, word in enumerate(my_list[1:])])
        print('del_details',del_details)

        sub_details_index = 0
        sub_details = f"{sub_details_index}-{my_list[sub_details_index]}"
        print('sub_details',sub_details)
        ml2_response = {
            "no_mistakes": last_index,
            "no_del": last_index - 1,
            "del_details": del_details,
            "no_sub": 1,
            "sub_details": sub_details,
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
            print("student_id",id_value)
            data_id = request.session.get('data_id')
            print("sample_id",data_id)
            my_program = request.session.get('my_program')
            print('my program is saveprogress',my_program)
            data = json_l1_data
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

            if val:
                print("question",val)

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
            data["program"] = my_program
            print(data)
            url = 'https://parakh.pradigi.org/v1/saveprogress/'
            files = []
            payload = {'data': json.dumps(data)}
            headers = {}
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            response_data = json.loads(response.text)
            print(fluency_adjustment)
            if fluency_adjustment == '0':
                return redirect('ml2_mcq_next')  # redirect to bl_mcq function
            else:
                return redirect('ml2_next')
    except TypeError:
        return HttpResponse("Invalid adjustment value")

def ml2_next_store(request):
  if request.method == 'POST':
    try:
            fluency_adjustment = request.POST.get('fluency_adjustment')
            print("fluency_adjustment", fluency_adjustment)
            
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
            print("student_id",id_value)
            data_id = request.session.get('data_id')
            print("sample_id",data_id)
            my_program = request.session.get('my_program')
            print('my program is saveprogress',my_program)
            data = json_l1
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

            if val:
                print("question",val)

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
            data["program"] = my_program
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
    except TypeError:
        return HttpResponse("Invalid adjustment value")


def ml2_mcq_api(request):
    selected_option = request.session.get('selected_option')
    selected_level = request.session.get('selected_level')
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
        my_program = request.session.get('my_program')
        print('my program is saveprogres',my_program)
        print('text:', text)
        print('audio_url:', audio_url)
        print('process_time:', process_time)
        data = json_l3_data
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
                data = json_l3_data
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
                data = json_l3_data
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
        data["program"] = my_program
        
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
    data = get_random_ml2_sentence(request)
    context = {"val": data['data'], "recording": True, "data_id": data['data_id'], "languages": data['languages']}
    request.session['ml2_context'] = context
    if request.method == 'POST':
        return redirect('ml2')
    return render(request, "AOP_PRO/ml2_mcq_next.html", context)


#############################################################################################

def get_random_ml3(request):
            data = json_l4_data
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
            data = json_l4_data
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
            data = json_l4_data
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
    data_id = request.session.get('data_id')
    print("data_id",data_id)
    data = json_l4_data
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
    else:
        return render(request, 'Error/pages-500.html' )


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
    data_id = request.session.get('data_id')
    print("data_id",data_id)
    data = json_l4_data
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
    else:
        return render(request, 'Error/pages-500.html' )


def ml3_retake(request):
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    media_folder = os.path.join(settings.MEDIA_ROOT)
    for file in os.listdir(media_folder):
        file_path = os.path.join(media_folder, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(e)

    data_id = request.session.get('data_id')
    print("data_id",data_id)
    request.session['audio_recorded'] = True
    data = json_l4_data
    paragraph = None
    for d in data['Paragraph']:
        if d['id'] == data_id:
            val = d['data']
            break
    if val:
        print("the val",val)
    return render(request, "AOP_PRO/ml3_retake.html", {"recording": True,"val":val })
   

def ml3_skip(request):
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
    data = json_l4_data
    paragraph = None
    for d in data['Paragraph']:
        if d['id'] == data_id:
            val = d['data']
            break

    words = val.split()
    my_list = list(words)
    last_index = len(my_list) 
    del_details = ', '.join([f"{i + 1}-{word}" for i, word in enumerate(my_list[1:])])
    print('del_details',del_details)

    sub_details_index = 0
    sub_details = f"{sub_details_index}-{my_list[sub_details_index]}"
    print('sub_details',sub_details)
    ml3_response = {
        "no_mistakes": last_index,
        "no_del": last_index - 1,
        "del_details": del_details,
        "no_sub": 1,
        "sub_details": sub_details,
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
    data = json_l4_data
    paragraph = None
    for d in data['Paragraph']:
        if d['id'] == data_id:
            val = d['data']
            break

    words = val.split()
    my_list = list(words)
    
    last_index = len(my_list) 
    del_details = ', '.join([f"{i + 1}-{word}" for i, word in enumerate(my_list[1:])])
    print('del_details',del_details)

    sub_details_index = 0
    sub_details = f"{sub_details_index}-{my_list[sub_details_index]}"
    print('sub_details',sub_details)
    ml3_response = {
        "no_mistakes": last_index,
        "no_del": last_index - 1,
        "del_details": del_details,
        "no_sub": 1,
        "sub_details": sub_details,
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
        print("student_id",id_value)
        data_id = request.session.get('data_id')
        print("sample_id",data_id)
        data =json_l4_data
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
        my_program = request.session.get('my_program')
        print('my program is saveprogres',my_program)

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
        data["program"] = my_program
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
        print("student_id",id_value)
        data_id = request.session.get('data_id')
        print("sample_id",data_id)
        data = json_l4_data
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
        my_program = request.session.get('my_program')
        print('my program is saveprogres',my_program)

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
        data["program"] = my_program
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
                'level' : "L3-sentence"
            }
            return render(request, "AOP_PRO/ans_page_aop.html", context=context)
            # return redirect('ml3_answer_page')
    except TypeError:
      return HttpResponse("Invalid adjustment value")
    

def ml3_mcq_api(request):
    selected_option = request.session.get('selected_option')
    selected_level = request.session.get('selected_level')

    if request.method == 'POST':
        selected_lan = request.POST.get('selected_language_input')
        print("lan",selected_lan)
        status = request.session.get('status')
        selected_language = request.POST.get('selected_language')
        selected_div = request.POST.get('selected-div')
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
        data = json_l4_data
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
            data = json_l4_data
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
            data = json_l4_data
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
        my_program = request.session.get('my_program')
        print('my program is saveprogres',my_program)
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
        data["program"] = my_program

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
            'level' : "L4-sentence"
        }
        return render(request, "AOP_PRO/ans_page_aop.html", context=context)


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
    return render(request, "AOP_PRO/ml3_mcq.html", context)

def ml3_mcq_next(request):
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
    my_program = request.session.get('my_program')  # Retrieve selected option from session
    print('my_program is', my_program)
    # if my_program == 'Advance English Program':
    #     return redirect('start_recording')
    if request.method == 'POST':
        # if my_program == 'Advance English Program':
        #     return redirect('start_recording')
        return redirect('start_recording')
    return render(request, 'para_start.html')


def get_random_paragraph(request):
    selected_option = request.session.get('selected_option')
    print("get_random_paragraph",selected_option)
    json_files = {
        'English': json_eng,
        'Hindi': json_hin,
        'Assamese': json_ass,
        'Bengali': json_ben,
        'Gujarati': json_guj,
        'Marathi': json_mar,
        'Kannada': json_kan,
        'Malayalam': json_mal,
        'Odiya': json_odi,
        'Punjabi': json_pun,
        'Tamil': json_tami,
        'Telugu': json_tel,
        'Urdu': json_urdu,
        'BL' : json_l1_data,
        'ML1': json_l2,
        'ML2' : json_l3,
        'EL' : json_l4,
        'Advance English Program BL' : json_advance_eng
    }
    if 'my_result' in request.session and len(request.session['my_result']) > 0:
        del request.session['my_result']
    my_program = request.session.get('my_program')  # Retrieve selected option from session
    print('my_program is', my_program)
    request.session['my_language'] = 'English'
    if my_program == 'Advance English Program' and (selected_option == 'BL' or selected_option == 'EL') :
        json_file = json_advance_eng
        # print(json_file)
        data1 = random.choice(json_file['Para'])
        print("the value ", data1['id'])
        data_id = data1['id']
        request.session['data_id'] = data_id
        print(data_id)
        # print("data", data1['data'])
        request.session['data_value'] = data1['data']
        return data1['data'], data_id
    else:
        selected_option in json_files
        json_file = json_files[selected_option]
        print(json_file)
        data1 = random.choice(json_file['Paragraph'])
        print("the value ", data1['id'])
        data_id = data1['id']
        request.session['data_id'] = data_id
        print(data_id)
        print("data", data1['data'])
        request.session['data_value'] = data1['data']
        return data1['data'], data_id

    # elif selected_option == 'BL':
    #     data = json_l1_data
    #     data1 = random.choice(data['Paragraph'])
    #     print("the value ",data1['id'])
    #     data_id = data1['id']
    #     request.session['data_id'] = data_id
    #     print(data_id)
    #     print("dta",data1['data'])
    #     return data1['data'], data_id
    # elif selected_option == 'ML1':
    #     data = json_l2
    #     data1 = random.choice(data['Paragraph'])
    #     print("the value ",data1['id'])
    #     data_id = data1['id']
    #     request.session['data_id'] = data_id
    #     print(data_id)
    #     print("dta",data1['data'])
    #     return data1['data'], data_id
    # elif selected_option == 'ML2':
    #     data = json_l3
    #     data1 = random.choice(data['Paragraph'])
    #     print("the value ",data1['id'])
    #     data_id = data1['id']
    #     request.session['data_id'] = data_id
    #     print(data_id)
    #     print("dta",data1['data'])
    #     return data1['data'], data_id
    # elif selected_option == 'EL':
    #     data = json_l4
    #     data1 = random.choice(data['Paragraph'])
    #     print("the value ",data1['id'])
    #     data_id = data1['id']
    #     request.session['data_id'] = data_id
    #     print(data_id)
    #     print("dta",data1['data'])
    #     return data1['data'], data_id
    

@csrf_exempt
def save_file(request):
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
            return render(request, 'para_ans.html', { 'filepath': filepath})


def answer(request):
    my_program = request.session.get('my_program')  # Retrieve selected program from session
    print('my_program is', my_program)
    if my_program == 'Advance English Program':
        filepath = request.session.get('filepath')
        filename = request.session.get('filename')
        print(filename)
        selected_option = request.session.get('selected_option')
        print("@",selected_option)
        data_id = request.session.get('data_id')
        my_language = request.session.get('my_language')  # Retrieve selected language from session
        print('my_language is', my_language)
        selected_option = my_language
        if selected_option == 'English':
            data_id = request.session.get('data_id')
            print("data_id", data_id)
            # with open(json_eng) as f:
            #     data = json.load(f)
            data = json_advance_eng
            # print('json advance english',data)
            paragraph = None
            val = None  # Initialize the val variable
            for d in data['Para']:
                if d['id'] == data_id:
                    val = d['data']
                    break

            if val:
                print("the val", val)
                url = 'http://3.7.133.80:8000/gettranscript/'
                
                filepath = request.session.get('filepath')  # Retrieve the filepath from session
                if filepath:
                    # Check if the file exists
                    if os.path.exists(filepath):
                        # Get the file name from the file path
                        filename = os.path.basename(filepath)
                        audio_url = request.build_absolute_uri(settings.MEDIA_URL + filename)
                    else:
                        filepath = None
                else:
                    filepath = None

                if filepath:
                    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
                    payload = {'language': selected_option, 'question': val}
                    headers = {}
                    response = requests.request("POST", url, headers=headers, data=payload, files=files)
                    print('***', response.text)

                    if response.status_code == 200:
                        print("text", val)
                        request.session['val'] = val
                        data_string = response.json().get('text')
                        mistake = response.json().get('no_mistakes')
                        fluency = response.json().get('wcpm')
                        index = response.json().get('sub_details')
                        deld = response.json().get('del_details')
                        request.session['no_mistakes'] = mistake

                        # Format wcpm to have only two decimal places
                        wcpm_formatted = '{:.2f}'.format(float(fluency)) if fluency else None

                        audio_url = None
                        if filepath:
                            audio_url = request.build_absolute_uri(settings.MEDIA_URL + filename)

                        return render(request, 'AOP_PRO/bl_answer.html', {'transcript': data_string, 'text':data_string, 'originaltext':val , 'sub_details':index,'del_details':deld, 'audio_url': audio_url, 'no_mistakes': mistake, 'wcpm': wcpm_formatted})


    # filepath = request.session.get('filepath')
    # print(filepath)
    # selected_option = request.session.get('selected_option')
    # print("@",selected_option)
    # my_program = request.session.get('my_program')
    # if my_program == 'Advance English Program':
    #     filepath = request.session.get('filepath')
    #     filename = request.session.get('filename')
    #     print(filename)
    #     selected_option = request.session.get('selected_option')
    #     print("@",selected_option)
        
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     data = json_advance_eng
    #     paragraph = None
    #     for d in data['Story']:
    #         if d['id'] == data_id:
    #             val = d['data']
    #             break

    #     if val:
    #         print("the val",val)
    #     url = 'http://3.7.133.80:8000/gettranscript/'
    #     files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    #     payload = {'language': 'English' ,'question':val}
    #     headers = {}
    #     response = requests.request("POST", url, headers=headers, data=payload, files=files)
    #     print('***', response.text)
    #     request.session['ml1_res'] = response.text
    #     phone_number = request.session.get('phone_number')
    #     print("ph", phone_number)
    #     enrollment_id = request.session.get('enrollment_id')
    #     print("enrollment_id",enrollment_id)
    #     if response.status_code == 200:
    #         print("text",val)
    #         data_string = response.json().get('text')
    #         mistake = response.json().get('no_mistakes')
    #         fluency = response.json().get('wcpm') 
    #         index = response.json().get('sub_details') 
    #         deld = response.json().get('del_details') 
    #         # Format wcpm to have only two decimal places
    #         wcpm_formatted = '{:.2f}'.format(float(fluency)) if fluency else None              
    #         filepath = request.session.get('filepath')
    #         audio_url = None
    #         if filepath:
    #             # Check if the file exists
    #             if os.path.exists(filepath):
    #                 # Get the file name from the file path
    #                 filename = os.path.basename(filepath)
    #                 audio_url = request.build_absolute_uri(settings.MEDIA_URL + filename)
    #             else:
    #                 filepath = None  
    #         return render(request, 'AOP_PRO/ml1_answer.html', {'transcript': data_string, 'text':data_string, 'originaltext':val , 'sub_details':index,'del_details':deld, 'audio_url': audio_url, 'no_mistakes': mistake, 'wcpm': wcpm_formatted,'mobile_number': phone_number})
    #     else:
    #         return render(request, 'Error/pages-500.html' )
    else:
        filepath = request.session.get('filepath')
        filename = request.session.get('filename')
        print(filename)
        selected_option = request.session.get('selected_option')
        print("@",selected_option)
        data_id = request.session.get('data_id')
        if selected_option is not None:
            data_id = request.session.get('data_id')
            print("data_id", data_id)
            json_file = json_files[selected_option]
            paragraph = None
            for d in json_file['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

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
                audio_url = request.build_absolute_uri(settings.MEDIA_URL + filename)
            else:
                filepath = None 
        return render(request, 'para_ans.html', {'transcript': data_string, 'text':data_string, 'originaltext':val , 'sub_details':index,'del_details':deld, 'audio_url': audio_url, 'no_mistakes': mistake, 'wcpm': wcpm_formatted})
    else:
        return render(request, 'Error/pages-500.html' )
    

def skip_answer(request):
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    data_id = request.session.get('data_id')
    print("data_id",data_id)
    my_program = request.session.get('my_program')
    if my_program == 'Advance English Program':
        json_file = json_advance_eng
        data = json_advance_eng
        paragraph = None
        for d in data['Para']:
            if d['id'] == data_id:
                val = d['data']
                break
    else:
        json_file = json_files[selected_option]
        if json_file is not None:
            data = json_file
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
    # if selected_option == 'English':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     data = json_eng
    #     paragraph = None
    #     for d in data['Paragraph']:
    #         if d['id'] == data_id:
    #             val = d['data']
    #             break
    # elif selected_option == 'BL':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     data = json_l1_data
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
    my_program = request.session.get('my_program')
    if my_program == 'Advance English Program':
        return render(request, 'AOP_PRO/bl_answer.html', {'originaltext': val, 'wcpm': None, 'no_mistakes': last_index})
    return render(request, 'para_ans.html', {'originaltext': val, 'wcpm': None, 'no_mistakes': last_index})


def next_page(request):
    if request.method == 'POST':
        total_mis = request.POST.get('total_mis')
        print("total_mis",total_mis)
        number = int(total_mis)
        media_folder = os.path.join(settings.MEDIA_ROOT)
        for file in os.listdir(media_folder):
            file_path = os.path.join(media_folder, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(e)
        audio_file_name = request.session.setdefault('audio_file_name', [])
        audio_file_name.clear()
        if number <= 1:
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
        number = int(word_mistakes)
        media_folder = os.path.join(settings.MEDIA_ROOT)
        for file in os.listdir(media_folder):
            file_path = os.path.join(media_folder, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(e)
        audio_file_name = request.session.setdefault('audio_file_name', [])
        audio_file_name.clear()

        if number <= 3:
            return redirect("story")
        else:
            return redirect("word")

def next_page_story(request):
    if request.method == 'POST':
        word_mistakes = request.POST.get('no_mistakes')
        print("no_mistakes",word_mistakes)
        number = int(word_mistakes)
        media_folder = os.path.join(settings.MEDIA_ROOT)
        for file in os.listdir(media_folder):
            file_path = os.path.join(media_folder, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(e)
        audio_file_name = request.session.setdefault('audio_file_name', [])
        audio_file_name.clear()

        
        if number <= 3:
            child_name = request.session.get('child_name')
            level = "Story"
            return render(request,'answer_page_gen.html',{'child_name': child_name, 'level': level})
            # return redirect("next_answer")
        else:
            child_name = request.session.get('child_name')
            level = "Paragraph"
            return render(request,'answer_page_gen.html',{'child_name': child_name, 'level': level})
            # return redirect("word_msg")

def next_page_letter(request):
    if request.method == 'POST':
        total_mis = request.POST.get('total_mis')
        print("total_mis",total_mis)
        number = int(total_mis)
        media_folder = os.path.join(settings.MEDIA_ROOT)
        for file in os.listdir(media_folder):
            file_path = os.path.join(media_folder, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(e)
        audio_file_name = request.session.setdefault('audio_file_name', [])
        audio_file_name.clear()

        if number <= 1:
            child_name = request.session.get('child_name')
            level = "Letter"
            return render(request,'answer_page_gen.html',{'child_name': child_name, 'level': level})
        else:
            child_name = request.session.get('child_name')
            level = "Beginner"
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
                    os.remove(file_path)
                    print("the file is removed")
            except Exception as e:
                print(e)

    my_program = request.session.get('my_program')
    if my_program == 'Advance English Program' :
        json_file = json_advance_eng
        # print(json_file)
        data_id = request.session.get('data_id')
        print("data_id", data_id)
        data = json_file  # Assuming the desired data is directly under the 'json_file' variable
        para = None

        for d in data['Para']:  # Assuming the data is stored under the 'Paragraph' key
            if d['id'] == data_id:
                val = d['data']
                break

    if selected_option is not None:
        data_id = request.session.get('data_id')
        print("data_id", data_id)
        json_file = json_files[selected_option]
        paragraph = None
        for d in json_file['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break
    
    # # old code remove upto API
    # if selected_option == 'English':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     request.session['audio_recorded'] = True
    #     data = json_eng
    #     paragraph = None
    #     for d in data['Paragraph']:
    #         if d['id'] == data_id:
    #             val = d['data']
    #             break
    # elif selected_option == 'BL':
    #     data_id = request.session.get('data_id')
    #     print("data_id",data_id)
    #     request.session['audio_recorded'] = True
    #     data = json_l1_data
    #     paragraph = None
    #     for d in data['Paragraph']:
    #         if d['id'] == data_id:
    #             val = d['data']
    #             break

    # elif selected_option == 'Hindi':
    #     data_id = request.session.get('data_id')
    #     print("data_id", data_id)
    #     json_file = json_files[selected_option]
    #     paragraph = None
    #     for d in json_file['Paragraph']:
    #         if d['id'] == data_id:
    #             val = d['data']
    #             break


    if val:
        print("the val",val)
    return render(request, "para_rec_next.html", {"recording": True,"val":val })
   

#                   Story Recording
def story(request):
    if request.method == 'POST':
        # my_program = request.session.get('my_program')
        # if my_program == 'Advance English Program':
        #     return redirect('start_recording_ml1')
        return redirect('story_recording')
    return render(request, 'story_start.html')


def get_random_story(request):
    selected_option = request.session.get('selected_option')
    print("@selected option",selected_option)
    my_program = request.session.get('my_program')
    if my_program == 'Advance English Program':
        selected_option = 'Advance English Program'
    json_files = {
        'English': json_eng,
        'Hindi': json_hin,
        'Assamese': json_ass,
        'Bengali': json_ben,
        'Gujarati': json_guj,
        'Marathi': json_mar,
        'Kannada': json_kan,
        'Malayalam': json_mal,
        'Odiya': json_odi,
        'Punjabi': json_pun,
        'Tamil': json_tami,
        'Telugu': json_tel,
        'Urdu': json_urdu,
        'BL' : json_l1_data,
        'ML1': json_l2,
        'ML2' : json_l3,
        'EL' : json_l4,
        'Advance English Program' : json_advance_eng
    }
    if 'my_result' in request.session and len(request.session['my_result']) > 0:
        del request.session['my_result']
    if selected_option in json_files:
        json_file = json_files[selected_option]
        data1 = random.choice(json_file['Story'])
        print("the value ", data1['id'])
        data_id = data1['id']
        request.session['data_id'] = data_id
        print(data_id)
        print("data", data1['data'])
        request.session['data_value'] = data1['data']
        return data1['data'], data_id


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

    
def story_answer(request):
    filepath = request.session.get('filepath')
    print(filepath)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    my_program = request.session.get('my_program')
    if my_program == 'Advance English Program':
        if 'my_result' in request.session and len(request.session['my_result']) > 0:
            del request.session['my_result']
        filepath = request.session.get('filepath')
        filename = request.session.get('filename')
        print(filename)
        selected_option = request.session.get('selected_option')
        print("@",selected_option)
        
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        data = json_advance_eng
        paragraph = None
        for d in data['Story']:
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
        else:
            return render(request, 'Error/pages-500.html' )
        
    

    else:
        selected_option is not None
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        data = json_files[selected_option]
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
        else:
            return render(request, 'Error/pages-500.html' )
   
def skip_story_answer(request):
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    my_program = request.session.get('my_program')
    if my_program == 'Advance English Program' and (selected_option == 'BL' or selected_option == 'EL'):
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        data = json_advance_eng
        story = None
        for d in data['Story']:
            if d['id'] == data_id:
                val = d['data']
                break

    elif selected_option == 'English':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        data = json_eng
        story = None
        for d in data['Story']:
            if d['id'] == data_id:
                val = d['data']
                break

    elif selected_option == 'BL':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        data = json_advance_eng
        story = None
        for d in data['Story']:
            if d['id'] == data_id:
                val = d['data']
                break
    elif selected_option == 'Hindi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        data = json_hin
        story = None
        for d in data['Story']:
            if d['id'] == data_id:
                val = d['data']
                break

    elif selected_option == 'Assamese':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        data = json_ass
        story = None
        for d in data['Story']:
            if d['id'] == data_id:
                val = d['data']
                break
    elif selected_option == 'Bengali':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        data = json_ben
        story = None
        for d in data['Story']:
            if d['id'] == data_id:
                val = d['data']
                break
    elif selected_option == 'Gujarati':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        data = json_guj
        story = None
        for d in data['Story']:
            if d['id'] == data_id:
                val = d['data']
                break
    elif selected_option == 'Marathi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        data = json_mar
        story = None
        for d in data['Story']:
            if d['id'] == data_id:
                val = d['data']
                break
    elif selected_option == 'Kannada':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        data = json_kan
        story = None
        for d in data['Story']:
            if d['id'] == data_id:
                val = d['data']
                break
    elif selected_option == 'Malayalam':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        data = json_mal
        story = None
        for d in data['Story']:
            if d['id'] == data_id:
                val = d['data']
                break
    elif selected_option == 'Odiya':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        data = json_odi
        story = None
        for d in data['Story']:
            if d['id'] == data_id:
                val = d['data']
                break
    elif selected_option == 'Punjabi':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        data = json_pun
        story = None
        for d in data['Story']:
            if d['id'] == data_id:
                val = d['data']
                break
    elif selected_option == 'Tamil':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        data = json_tami
        story = None
        for d in data['Story']:
            if d['id'] == data_id:
                val = d['data']
                break
    elif selected_option == 'Telugu':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        data = json_tel
        story = None
        for d in data['Story']:
            if d['id'] == data_id:
                val = d['data']
                break
    elif selected_option == 'Urdu':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        data = json_urdu
        story = None
        for d in data['Story']:
            if d['id'] == data_id:
                val = d['data']
                break

    if val:
        print("the val",val)
    words = val.split()
    my_list = list(words)
    last_index = len(my_list) 
    my_program = request.session.get('my_program')
    if my_program == 'Advance English Program':
        return render(request, 'AOP_PRO/ml1_answer.html', {'originaltext': val, 'wcpm': None, 'no_mistakes': last_index})
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
                    os.remove(file_path)
            except Exception as e:
                print(e)

    if selected_option is not None:
        data_id = request.session.get('data_id')
        print("data_id", data_id)
        json_file = json_files[selected_option]
        Story = None
        for d in json_file['Story']:
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
    print("@",selected_option)
    json_file = json_files[selected_option]

    if json_file is not None:
        data = json_file  # Assuming json_hin contains the actual JSON data for Hindi
        data1 = random.choice(data['Word'])
        print("the value ", data1['id'])
        data_id = data1['id']
        while data_id in word_ids:
            data1 = random.choice(data['Word'])
            data_id = data1['id']
        word_ids.append(data_id)
        request.session['word_ids'] = word_ids
        print("word_ids", word_ids)
        request.session['data_id'] = data_id
        print("dta", data1['data'])
        if len(word_ids) == 5:
            d_dataid = word_ids.copy()
            print(d_dataid)
            request.session['d_dataid'] = d_dataid

            word_ids.clear()
        return data1['data'], data_id


def word_recording(request):
    d_dataid = request.session.setdefault('d_dataid', [])
    dc_res = request.session.setdefault('dc_res', [])
    if len(dc_res) == 5:
        dc_res.clear()
        d_dataid.clear()

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

    if len(dc_res) == 4:
        dc_res.clear()
        d_dataid.clear()
        print(d_dataid)
   
    Word, data_id = get_random_word(request)
    context = {"val": Word, "recording": True, "data_id": data_id}
    return render(request, "word_rec_next.html", context)

json_files = {
            'English': json_eng,
            'Hindi': json_hin,
            'Assamese': json_ass,
            'Bengali': json_ben,
            'Gujarati': json_guj,
            'Marathi': json_mar,
            'Kannada': json_kan,
            'Malayalam': json_mal,
            'Odiya': json_odi,
            'Punjabi': json_pun,
            'Tamil': json_tami,
            'Telugu': json_tel,
            'Urdu': json_urdu,
            'BL' : json_l1_data,
            'ML1': json_l2,
            'ML2' : json_l3,
            'EL' : json_l4
        }

def word_skip(request):
    if request.method == 'POST':
        val = request.POST.get('val')
        skip_val = request.session.setdefault('skip_val', [])

        d_audio_files = request.session.get('d_audio_files', [])
        d_audio_files_name = request.session.get('d_audio_files_name', [])
        word_ids = request.session.get('word_ids', [])
        qword = request.session.setdefault('qword', [])

        print("d_audio_files_name", d_audio_files_name)
        print("word_ids next", word_ids)

        missing_indices = [i for i, id in enumerate(word_ids) if id not in d_audio_files_name]

        # Print the missing indices
        print("The missing indices are:", missing_indices)
        for word_id in word_ids:
            audio_file = word_id + '.wav'
            if audio_file not in d_audio_files_name:
                d_audio_files_name.append(audio_file)

        # update the session variable with the new list
        for word_id in word_ids:
            wav_file = os.path.join(base_path, f"{word_id}.wav")
            if wav_file not in d_audio_files:
                d_audio_files.append(wav_file)
                skip_val.append(wav_file)

        request.session['d_audio_files'] = d_audio_files
        request.session['skip_val'] = skip_val
        request.session['d_audio_files_name'] = d_audio_files_name

        print("skip_val  word_answer", skip_val)
        print("d_audio_files  word_answer", d_audio_files)

        selected_option = request.session.get('selected_option')
        print("@", selected_option)
        if selected_option in json_files:
            json_file = json_files[selected_option]
            print('@###############################',json_file)
            request.session['json_file'] = json_file
            data_id = request.session.get('data_id')
            print("data_id", data_id)
            # with open(json_file, 'r', encoding='utf-8') as f:
            #     data = json.load(f)
            data = json_file
            val = None
            for d in data['Word']:
                if d['id'] == data_id:
                    val = d['data']
                    break
            if val is None:
                return HttpResponseBadRequest('Data not found in the JSON file')
        else:
            return HttpResponseBadRequest('Selected language JSON file not found')

        qword = request.session.setdefault('qword', [])
        d_copy_audio_files = request.session.get('d_copy_audio_files', [])
        d_audio_files = request.session.get('d_audio_files', [])
        d_audio_files_name = request.session.setdefault('d_audio_files_name', [])
        copy_word_name = request.session.setdefault('copy_word_name', [])

        print("d_audio_files_name", d_audio_files_name)
        if len(d_audio_files) == 5:
            d_copy_audio_files = d_audio_files.copy()
        if len(d_audio_files_name) == 5:
            copy_word_name = d_audio_files_name.copy()
        
        print("copy_word_name", copy_word_name)
        request.session['copy_word_name'] = copy_word_name

        if val:
            print("the val", val)
            qword = request.session.get("qword")
            qword.append(val)
            request.session["qword"] = qword
            print("qword", qword)
            dc_res = request.session.setdefault('dc_res', [])
            if request.session.get("dc_res", None) is None:
                dc_res = []
            else:
                dc_res = request.session.get("dc_res")
            request.session["dc_res"] = dc_res
            dc_res.append(
                '{"no_mistakes": 1, "no_del": 0, "del_details": "", "no_sub": 1, "sub_details": "0-\\u092a\\u0948\\u0938\\u093e:", "status": "success", "wcpm": 0.0, "text": "", "audio_url": "", "process_time": 0.47053098678588867}')
            print("testing the data", dc_res)
            if len(dc_res) == 5:
                request.session['dc_rec'] = dc_res
                context = {'l_res': dc_res}
                url = reverse('wans_page')
                return redirect(url, context)
            if len(d_audio_files) == 4:
                return redirect('word_recording')
        return redirect('word_recording_next')


def submit_word_skip(request):
    if request.method == 'POST':
        submit_id = request.session.get('submit_id')
        data_id = submit_id.get('data_id')
        word_ids = request.session.get('word_ids')
        val = request.POST.get('val')
        skip_val = request.session.setdefault('skip_val', [])
        d_audio_files = request.session.get('d_audio_files', [])
        d_audio_files_name = request.session.get('d_audio_files_name', [])
        missing_indices = [i for i, id in enumerate(word_ids) if id not in d_audio_files_name]

        audio_file = data_id + '.wav'
        if audio_file not in d_audio_files_name:
            d_audio_files_name.append(audio_file)
            wav_file = os.path.join(base_path, f"{data_id}.wav")  # Added this line
            d_audio_files.append(wav_file)
            skip_val.append(wav_file)

        request.session['d_audio_files'] = d_audio_files
        request.session['skip_val'] = skip_val
        request.session['d_audio_files_name'] = d_audio_files_name
        selected_option = request.session.get('selected_option')
        json_file = request.session.get('json_file')
        data = json_file
        Word = None
        for d in data['Word']:
            if d['id'] == data_id:
                val = d['data']
                break

        qword = request.session.setdefault('qword', [])
        qword.append(val)
        request.session['qword'] = qword

        dc_res = request.session.setdefault('dc_res', [])
        dc_res.append('{"no_mistakes": 1, "no_del": 0, "del_details": "", "no_sub": 1, "sub_details": "0-\\u092a\\u0948\\u0938\\u093e:", "status": "success", "wcpm": 0.0, "text": "", "audio_url": "", "process_time": 0.47053098678588867}')
        request.session['dc_res'] = dc_res

        if len(dc_res) == 5:
            request.session['dc_rec'] = dc_res
            context = {'l_res': dc_res}
            url = reverse('wans_page')
            return redirect(url, context)

        if len(d_audio_files) == 4:
            return redirect('word_recording')

    return redirect('word_recording_next')


def word_answer(request):
    filepath = request.session.get('filepath')
    selected_option = request.session.get('selected_option')
    print("@", selected_option)

    if selected_option in json_files:
        json_file_path = json_files[selected_option]
        print('@###############################', json_file_path)
        data_id = request.session.get('data_id')
        print("data_id", data_id)
        data = json_file_path
        word = next((d['data'] for d in data['Word'] if d['id'] == request.session.get('data_id')), None)


    qword = request.session.setdefault('qword', [])
    if word:
        qword.append(word)
        request.session['qword'] = qword
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': selected_option, 'question': word}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    dc_res = request.session.setdefault('dc_res', [])
    if response.status_code == 200:
        dc_res.append(response.text)
        request.session['dc_res'] = dc_res

        if len(qword) == 5:
            request.session['dc_rec'] = dc_res
            return redirect(reverse('wans_page'), context={'l_res': dc_res})
        elif len(qword) == 4:
            return redirect('word_recording')
    else:
        return render(request, 'Error/pages-500.html' )
            
    return redirect('word_recording_next')


@csrf_exempt
def save_word(request):
    d_audio_files = request.session.setdefault('d_audio_files', [])
    d_audio_files_name = request.session.setdefault('d_audio_files_name', [])
    if request.method == 'POST' and request.FILES.get('audio_blob'):
        if len(d_audio_files)>5:
            d_audio_files.clear()
            d_audio_files_name.clear()  
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        print(val)
        filename = f'{data_id}.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
        d_audio_files.append(filepath)
        d_audio_files_name.append(filename)
        print("###",d_audio_files)
        request.session['filepath'] = filepath
        return render(request, 'word_rec.html', { 'audio_url': filepath})


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
    return render(request, 'word_answer.html', context)


def next_word(request):
    t.sleep(2)
    d_dataid = request.session.setdefault('d_dataid', [])
    copy_word_name = request.session.setdefault('copy_word_name', [])
    if request.method == "POST":
        copy_word_name = request.session.get('copy_word_name')
        copy_word_name = request.session.setdefault('copy_word_name', [])
        d_dataid = request.session.get('d_dataid', [])
        print("^^^",d_dataid)
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
            print("@",selected_option)

            if selected_option is not None:
                print("d_dataid0",d_dataid[0])
                request.session['d_dataid[0]'] = d_dataid[0]
                request.session['audio_recorded'] = True
                json_file_path = json_files[selected_option]
                print('@###############################', json_file_path)
                # request.session['json_file'] = json_file_path
                data_id = request.session.get('data_id')
                print("data_id", data_id)
                if data_id is not None:
                    data = json_file_path
                    Word = None
                    for d in data['Word']:
                        if d['id'] == d_dataid[0]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_word/retake_word1.html", {"recording": True,"val":val })

        elif "record2" in request.POST:
           
            selected_option = request.session.get('selected_option')
            print("@",selected_option)
            request.session['d_dataid[1]'] = d_dataid[1]

            filename = d_dataid[1] + '.wav'
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

            if selected_option is not None:
                print("d_dataid1",d_dataid[1])
                request.session['d_dataid[1]'] = d_dataid[1]
                request.session['audio_recorded'] = True
                json_file_path = json_files[selected_option]
                print('@###############################', json_file_path)
                data_id = request.session.get('data_id')
                print("data_id", data_id)
                if data_id is not None:
                    data = json_file_path
                    Word = None
                    for d in data['Word']:
                        if d['id'] == d_dataid[1]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_word/retake_word2.html", {"recording": True,"val":val })

        elif "record3" in request.POST:
            selected_option = request.session.get('selected_option')
            print("@",selected_option)
            request.session['d_dataid[2]'] = d_dataid[2]

            filename = d_dataid[2] + '.wav'
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

            if selected_option is not None:
                print("d_dataid2",d_dataid[2])
                request.session['d_dataid[2]'] = d_dataid[2]
                request.session['audio_recorded'] = True
                json_file_path = json_files[selected_option]
                print('@###############################', json_file_path)
                data_id = request.session.get('data_id')
                print("data_id", data_id)
                if data_id is not None:
                    data = json_file_path
                    Word = None
                    for d in data['Word']:
                        if d['id'] == d_dataid[2]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_word/retake_word3.html", {"recording": True,"val":val })

        elif "record4" in request.POST:
            selected_option = request.session.get('selected_option')
            print("@",selected_option)
            request.session['d_dataid[3]'] = d_dataid[3]

            filename = d_dataid[3] + '.wav'
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

            if selected_option is not None:
                print("d_dataid3",d_dataid[3])
                request.session['d_dataid[3]'] = d_dataid[3]
                request.session['audio_recorded'] = True
                json_file_path = json_files[selected_option]
                print('@###############################', json_file_path)
                data_id = request.session.get('data_id')
                print("data_id", data_id)
                if data_id is not None:
                    data = json_file_path
                    Word = None
                    for d in data['Word']:
                        if d['id'] == d_dataid[3]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_word/retake_word4.html", {"recording": True,"val":val })
        
        elif "record5" in request.POST:
            selected_option = request.session.get('selected_option')
            print("@",selected_option)
            request.session['d_dataid[4]'] = d_dataid[4]
            filename = d_dataid[4] + '.wav'
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

            if selected_option is not None:
                print("d_dataid3",d_dataid[4])
                request.session['d_dataid[4]'] = d_dataid[4]
                request.session['audio_recorded'] = True
                json_file_path = json_files[selected_option]
                print('@###############################', json_file_path)
                data_id = request.session.get('data_id')
                print("data_id", data_id)
                if data_id is not None:
                    data = json_file_path
                    Word = None
                    for d in data['Word']:
                        if d['id'] == d_dataid[4]:
                            val = d['data']
                            break
                    if val:
                        print("the val",val)
                    return render(request, "retake_word/retake_word5.html", {"recording": True,"val":val })

    return redirect('word_answer')


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
        request.session['filepath'] = filepath
        return render(request, 'word_answer.html', { 'audio_url': filepath})
    
def save_word1(request):
    d_dataid = request.session.setdefault('d_dataid', [])
    filepath = request.session.get('filepath')
    print(filepath)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    request.session['d_dataid[0]'] = d_dataid[0]
    print("data_id", d_dataid[0])
    json_file_path = json_files.get(selected_option)
    print('@###############################', json_file_path)
    data_id = request.session.get('data_id')
    print("data_id", data_id)
    if json_file_path:
            data = json_file_path
            if data is not None:
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
    else:
        return render(request, 'Error/pages-500.html' )
        

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
        request.session['filepath'] = filepath
        return render(request, 'word_answer.html', { 'audio_url': filepath})
    

def save_word2(request):
    d_dataid = request.session.setdefault('d_dataid', [])
    filepath = request.session.get('filepath')
    print(filepath)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    request.session['d_dataid[1]'] = d_dataid[1]
    print("data_id", d_dataid[1])
    json_file_path = json_files.get(selected_option)
    print('@###############################', json_file_path)
    data_id = request.session.get('data_id')
    print("data_id", data_id)
    if json_file_path:
            data = json_file_path
            if data is not None:
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
                    
    else:
        return render(request, 'Error/pages-500.html' )


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
        request.session['filepath'] = filepath
        return render(request, 'word_answer.html', { 'audio_url': filepath})


def save_word3(request):
    d_dataid = request.session.setdefault('d_dataid', [])
    filepath = request.session.get('filepath')
    print(filepath)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    request.session['d_dataid[2]'] = d_dataid[2]
    print("data_id", d_dataid[2])
    json_file_path = json_files.get(selected_option)
    print('@###############################', json_file_path)
    data_id = request.session.get('data_id')
    print("data_id", data_id)
    if json_file_path:
            data = json_file_path
            if data is not None:
                Word = None
                for d in data['Word']:
                    if d['id'] == d_dataid[2]:
                        val = d['data']
                        break
    
    if selected_option == 'English':
        request.session['d_dataid[2]'] = d_dataid[2]
        print("data_id",d_dataid[2])
        data = json_eng
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
                    
    else:
        return render(request, 'Error/pages-500.html' )


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
    request.session['d_dataid[3]'] = d_dataid[3]
    print("data_id", d_dataid[3])
    json_file_path = json_files.get(selected_option)
    print('@###############################', json_file_path)
    data_id = request.session.get('data_id')
    print("data_id", data_id)
    
    if json_file_path:
            data = json_file_path
            if data is not None:
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
                    
    else:
        return render(request, 'Error/pages-500.html' )


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
    request.session['d_dataid[4]'] = d_dataid[4]
    print("data_id", d_dataid[4])
    json_file_path = json_files[selected_option]
    print('@###############################', json_file_path)
    data_id = request.session.get('data_id')
    print("data_id", data_id)
    
    if json_file_path:
        data = json_file_path
        if data is not None:
            Word = None
            for d in data['Word']:
                if d['id'] == d_dataid[4]:
                    val = d['data']
                    break
    
    if selected_option == 'English':
        request.session['d_dataid[4]'] = d_dataid[4]
        print("data_id",d_dataid[4])
        data = json_eng
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
                    
    else:
        return render(request, 'Error/pages-500.html' )

    
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
    # data_ids.clear()
    json_file = json_files[selected_option]
    if json_file is not None:
        data = json_file 
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
                                                                                                    
    print(l_dataid)
    Letter, data_id = get_random_letter(request)
    context = {"val": Letter, "recording": True, "data_id": data_id}
    return render(request, "letter_rec_next.html", context)


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
    data_id = request.session.get('data_id')
    print("data_id",data_id)

    if selected_option is not None:
        json_file = json_files[selected_option]
        print('@###############################',json_file)
        request.session['json_file'] = json_file
        data_id = request.session.get('data_id')
        print("data_id", data_id)
            # with open(json_file, 'r', encoding='utf-8') as f:
            #     data = json.load(f)
        data = json_file
        Letter = None
        for d in data['Letter']:
            if d['id'] == data_id:
                val = d['data']
                break
    
    if selected_option == 'English':
        data_id = request.session.get('data_id')
        print("data_id",data_id)
        # with open(json_eng) as f:
        #     data = json.load(f)
        data = json_eng
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
    wav_file = os.path.join(base_path, f"{data_id}.wav")
    if wav_file not in l_audio_files:
        l_audio_files.append(wav_file)
        skip_val_letter.append(wav_file)

    request.session['l_audio_files'] = l_audio_files
    request.session['skip_val_letter'] = skip_val_letter
    print("l_audio_files  word_answer",l_audio_files)
    request.session['l_audio_files_name'] = l_audio_files_name
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    data_id = request.session.get('data_id')
    print("data_id",data_id)
    json_file = json_files[selected_option]

    if selected_option is not None:
        data = json_file
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

    if selected_option in json_files:
        json_file_path = json_files[selected_option]
        print('@###############################', json_file_path)
        # request.session['json_file'] = json_file_path
        data_id = request.session.get('data_id')
        print("data_id", data_id)
        data = json_file_path

        # with open(json_file_path, 'r', encoding='utf-8') as f:
        #     data = json.load(f)
        letter = next((d['data'] for d in data['Letter'] if d['id'] == request.session.get('data_id')), None)

    qletter = request.session.setdefault('qletter', [])
    if letter:
        qletter.append(letter)
        request.session['qletter'] = qletter

    # if val:
    #     print("the val",val)
    #     qletter = request.session.get("qletter")
    #     qletter.append(val)
    #     request.session["qletter"] = qletter

        print("qletter",qletter)
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': selected_option ,'question':letter}
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
    else:
        return render(request, 'Error/pages-500.html' )
            
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
                print('audiourls',audio_urls)
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
            if selected_option is not None:
                print("l_dataid0",l_dataid[0])
                request.session['l_dataid[0]'] = l_dataid[0]
                json_file_path = json_files[selected_option]
                print('@###############################', json_file_path)
                # request.session['json_file'] = json_file_path
                data_id = request.session.get('data_id')
                print("data_id", data_id)
                if data_id is not None:
                    data = json_file_path
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

            if selected_option is not None:
                print("l_dataid0",l_dataid[0])
                request.session['l_dataid[1]'] = l_dataid[1]
                json_file_path = json_files[selected_option]
                print('@###############################', json_file_path)
                # request.session['json_file'] = json_file_path
                data_id = request.session.get('data_id')
                print("data_id", data_id)
                if data_id is not None:
                    data = json_file_path
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
            if selected_option is not None:
                print("l_dataid0",l_dataid[2])
                request.session['l_dataid[2]'] = l_dataid[2]
                request.session['audio_recorded'] = True
                json_file_path = json_files[selected_option]
                print('@###############################', json_file_path)
                # request.session['json_file'] = json_file_path
                data_id = request.session.get('data_id')
                print("data_id", data_id)
                if data_id is not None:
                    data = json_file_path
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
            if selected_option is not None:
                print("l_dataid0",l_dataid[3])
                request.session['l_dataid[3]'] = l_dataid[3]
                request.session['audio_recorded'] = True
                json_file_path = json_files[selected_option]
                print('@###############################', json_file_path)
                data_id = request.session.get('data_id')
                print("data_id", data_id)
                if data_id is not None:
                    data = json_file_path
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
            if selected_option is not None:
                print("l_dataid0",l_dataid[4])
                request.session['l_dataid[4]'] = l_dataid[4]
                request.session['audio_recorded'] = True
                json_file_path = json_files[selected_option]
                print('@###############################', json_file_path)
                data_id = request.session.get('data_id')
                print("data_id", data_id)
                if data_id is not None:
                    data = json_file_path
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
    request.session['l_dataid[0]'] = l_dataid[0]
    print("data_id", l_dataid[0])
    json_file_path = json_files.get(selected_option)
    print('@###############################', json_file_path)
    data_id = request.session.get('data_id')
    print("data_id", data_id)
    
    if json_file_path:
            data = json_file_path
            if data is not None:
                Word = None
                for d in data['Letter']:
                    if d['id'] == l_dataid[0]:
                        val = d['data']
                        break

    if selected_option == 'English':
        request.session['l_dataid[0]'] = l_dataid[0]
        print("data_id",l_dataid[0])
        # with open(json_eng) as f:
        #     data = json.load(f)
        data = json_eng
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
                    
    else:
        return render(request, 'Error/pages-500.html' )
    

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
    request.session['l_dataid[1]'] = l_dataid[1]
    print("data_id", l_dataid[1])
    json_file_path = json_files.get(selected_option)
    print('@###############################', json_file_path)
    data_id = request.session.get('data_id')
    print("data_id", data_id)
    
    if json_file_path:
            data = json_file_path
            if data is not None:
                Word = None
                for d in data['Letter']:
                    if d['id'] == l_dataid[1]:
                        val = d['data']
                        break

    if selected_option == 'English':
        request.session['l_dataid[1]'] = l_dataid[1]
        print("data_id",l_dataid[1])
        # with open(json_eng) as f:
        #     data = json.load(f)
        data = json_eng
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

    if response.status_code == 200:
        lc_res = request.session.setdefault('lc_res', [])
        if request.session.get("lc_res",None) is None:
            lc_res = []
        else:
            lc_res = request.session.get("lc_res")
            lc_res[1] = response.text
            request.session["lc_res"] = lc_res
            print("testing the data", lc_res)
            if len(lc_res)==5:
                    request.session['lc_rec'] = lc_res
                    context = {'l_res': lc_res}
                    url = reverse('lans_page')
                    if len(lc_res)==5:
                        
                        return redirect(url,context)
                    
    else:
        return render(request, 'Error/pages-500.html' )


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
        request.session['filepath'] = filepath
        return render(request, 'letter_answer.html', { 'audio_url': filepath})
    

def save_letter3(request):
    l_dataid = request.session.setdefault('l_dataid', [])
    filepath = request.session.get('filepath')
    print(filepath)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    request.session['l_dataid[2]'] = l_dataid[2]
    print("data_id", l_dataid[2])
    json_file_path = json_files.get(selected_option)
    print('@###############################', json_file_path)
    data_id = request.session.get('data_id')
    print("data_id", data_id)
    
    if json_file_path:
            data = json_file_path
            if data is not None:
                Word = None
                for d in data['Letter']:
                    if d['id'] == l_dataid[2]:
                        val = d['data']
                        break

    if selected_option == 'English':
        request.session['l_dataid[2]'] = l_dataid[2]
        print("data_id",l_dataid[2])
        # with open(json_eng) as f:
        #     data = json.load(f)
        data = json_eng
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
                    
    else:
        return render(request, 'Error/pages-500.html' )


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
        request.session['filepath'] = filepath
        return render(request, 'letter_answer.html', { 'audio_url': filepath})
    

def save_letter4(request):
    l_dataid = request.session.setdefault('l_dataid', [])
    filepath = request.session.get('filepath')
    print(filepath)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    request.session['l_dataid[3]'] = l_dataid[3]
    print("data_id", l_dataid[3])
    json_file_path = json_files.get(selected_option)
    print('@###############################', json_file_path)
    data_id = request.session.get('data_id')
    print("data_id", data_id)
    
    if json_file_path:
            data = json_file_path
            if data is not None:
                Word = None
                for d in data['Letter']:
                    if d['id'] == l_dataid[3]:
                        val = d['data']
                        break

    if selected_option == 'English':
        request.session['l_dataid[3]'] = l_dataid[3]
        print("data_id",l_dataid[3])
        # with open(json_eng) as f:
        #     data = json.load(f)
        data = json_eng
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
    else:
        return render(request, 'Error/pages-500.html' )


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
        request.session['filepath'] = filepath
        return render(request, 'letter_answer.html', { 'audio_url': filepath})
    
def save_letter5(request):
    l_dataid = request.session.setdefault('l_dataid', [])
    
    filepath = request.session.get('filepath')
    print(filepath)
    selected_option = request.session.get('selected_option')
    print("@",selected_option)
    request.session['l_dataid[4]'] = l_dataid[4]
    print("data_id", l_dataid[4])
    json_file_path = json_files.get(selected_option)
    print('@###############################', json_file_path)
    data_id = request.session.get('data_id')
    print("data_id", data_id)
    
    if json_file_path:
            data = json_file_path
            if data is not None:
                Word = None
                for d in data['Letter']:
                    if d['id'] == l_dataid[4]:
                        val = d['data']
                        break

    if selected_option == 'English':
        request.session['l_dataid[4]'] = l_dataid[4]
        print("data_id",l_dataid[4])
        # with open(json_eng) as f:
        #     data = json.load(f)
        data = json_eng
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
                    
    else:
        return render(request, 'Error/pages-500.html' )


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


# for advance english program
def advance_bl_store(request):
    no_mistakes = request.session.get('no_mistakes')
    number = int(no_mistakes)
    if request.method == 'POST':   
        # fluency_adjustment = request.POST.get('fluency_adjustment')
        # number = int(fluency_adjustment)
        print("fluency_adjustment", no_mistakes)
        # adjustment_from_storage = request.POST.get('adjustment')
        # print('adjustment_from_storage',adjustment_from_storage)
        # Store the value in the session
        # request.session['adjustment'] = adjustment
        # nomistake_list = []
        # nomistake_list.append(str(request.session['adjustment']))
        # nomistake = nomistake_list[0]
        # print("nomistake", nomistake)
        
        if no_mistakes == 0:
            request.session['ans_next_level'] = 'EL'
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
        # data["no_mistakes_edited"]= fluency_adjustment
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
        if number <= 2:
            return redirect('bl_mcq_next')  # redirect to bl_mcq function
        else:
            context = {
                    'level' : "Paragraph without Exeception"
                }
            return render(request,'answer_page_gen.html', context=context) 

    
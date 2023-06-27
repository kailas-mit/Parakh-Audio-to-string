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
from firebase_admin import credentials as fb_credentials,firestore
from dotenv import dotenv_values
from .models import Program, Aop_lan, Aop_sub_lan,MyModel,Avatar,MyUser


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
    'json_urd': 'ParakhData_urdu'
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
base_path = os.path.join(settings.MEDIA_ROOT, "")


def first(request):
    """
    This view handles the first page of the application.
    It displays the available program options and saves the selected option in the session.
    If the user selects the 'General Program', it redirects to the 'login' page.
    If the user selects the 'AOP Program' or 'Advance English Program', it redirects to the 'aop_language' page.
    """ 
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
    """
    This view handles the AOP language selection page.
    It displays the available options for AOP sub-languages and English language options.
    If a selection is made and submitted via POST request.
    """
    options = Aop_sub_lan.OPTION_CHOICES
    eng_option= Aop_lan.OPTION_CHOICES
    if request.method == 'POST':
        selected_level = request.POST.get('options')
        print("selected_level",selected_level)
    return render(request, 'AOP_PRO/language.html',{'options': options, 'eng_option': eng_option})


def aop_num(request,selected_option):
    """
    This view handles the AOP number search page.
    It receives the selected option as a parameter and stores it in the session.
    It then renders the 'AOP_PRO/search_num.html' template.
    """
    request.session['selected_option'] = selected_option
    return render(request, 'AOP_PRO/search_num.html')


def red_start(request):
    """
    This view handles the process of creating a profile and starting the assessment for the AOP program.
    It receives enrollment ID and phone number as input and makes a POST request to create a profile using the API.
    The created profile ID is stored in the session for further use.
    If the request method is GET, it retrieves the enrollment ID, phone number, name, and program from the session.
    It then makes an API request to fetch children details based on the mobile number provided.
    If the mobile number is found, the name and status are stored in the session and rendered in the template.
    If the mobile number is not found, an error message is displayed.
    If the request method is POST and contains the 'search' parameter, it retrieves the selected option and mobile number from the request.
    The mobile number is stored in the session, and an API request is made to fetch children details.
    If the mobile number is found, the name and status are stored in the session and rendered in the template.
    If the mobile number is not found, an error message is displayed.
    """
    selected_option = request.session.get('selected_option')
    print("selected_option",selected_option)
    if request.method == 'GET':
        enrollment_id = request.GET.get('enrollment_id')
        phone_number = request.session.get('phone_number')
        name = request.session.get('name')
        my_program = request.session.get('my_program')
        data={}
        data["name"]=name
        data["profile_pic"]= ""
        data["platform"]= 'web'
        data["phone_number"]= phone_number
        data["enrollment_id"]= enrollment_id
        data["program"]= my_program
        url = 'https://parakh.pradigi.org/v1/createprofile/'
        files = []
        payload = {'data': json.dumps(data)}
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        response_data = json.loads(response.text)
        id_value = response_data["data"][0]["id"]
        request.session['id_value'] = id_value
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


def msg_api_for_general_program(request):
    """
    This view handles the process of making an API request to update the result for the general program assessment.
    If the request method is POST and contains the 'search' parameter, it retrieves the selected option, enrollment ID,
    profile ID, program, and current date from the session.
    It then constructs the API URL with the necessary parameters and makes a GET request to update the assessment result.
    If the API response is successful (status code 200), it redirects the user to the home page.
    Otherwise, it returns an error message indicating an invalid API response.
    """
    if "search" in request.POST:
        now = datetime.now()
        today_date = now.strftime("%Y-%m-%d")
        selected_option = request.session.get('selected_option')
        enrollment_id = request.session.get('enrollment_id')
        id_value = request.session.get('id_value')
        my_program = request.session.get('my_program')
        url = f'https://prajeevika.org/apis/aop/update-result.php?token=eyNsWgAdBF0KafwGPwOC9h5rWABTBuAKYxDxv8zRgJyuP&enrollment_id={enrollment_id}&student_id={id_value}&assessment_type={selected_option}&assessment_date={today_date}&assessment_level=L1&program={my_program}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return redirect('/')
        else:
            return HttpResponse("Error: Invalid API response")


def msg_api(request):
    """
    This view handles the process of making an API request to update the assessment result and retrieve children details.
    If the request method is POST and contains the 'search' parameter, it retrieves the selected option, enrollment ID,
    profile ID, program, and current date from the session.
    It then constructs the API URL with the necessary parameters and makes a GET request to update the assessment result.
    If the API response is successful (status code 200), it retrieves the mobile number from the request POST data and
    makes another API request to retrieve the children details.
    If the children details API response is successful, it extracts the name and status from the response data and stores
    them in the session.
    Finally, it renders the 'AOP_PRO/search_num.html' template with the retrieved data and selected option.
    If any API response is unsuccessful, it renders the 'Error/pages-500.html' template.
    """
    if "search" in request.POST:
        now = datetime.now()
        today_date = now.strftime("%Y-%m-%d")
        selected_option = request.session.get('selected_option')
        enrollment_id = request.session.get('enrollment_id')
        id_value = request.session.get('id_value')
        my_program = request.session.get('my_program')
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
            return render(request, 'AOP_PRO/search_num.html', context)
        else:
            return render(request, 'Error/pages-500.html' )


def login(request):
    """
    This view handles the login process. If the request method is POST, it retrieves the mobile number from the request
    POST data and stores it in the session. It performs basic validation to ensure that the mobile number is in the
    correct format. If the mobile number already exists in the database, it redirects to the 'choose_avatar' page.
    Otherwise, it creates a new user with a default username and the provided mobile number, and redirects to the
    'choose_avatar' page. If the request method is GET, it renders the 'login.html' template.
    """
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
    """
    This view handles the selection of an avatar. If the request method is POST, it retrieves the child name and
    selected image from the request POST data. It performs basic validation to ensure that the child name is provided.
    It then creates a new Avatar instance with the child name and selected image, and saves it to the database.
    The child name and avatar URL are stored in the session. The mobile number and my_program values are retrieved
    from the session. A data dictionary is created with the necessary information for creating a profile.
    The data is sent as a JSON payload to the specified URL using the POST method. Finally, it redirects to the
    'select_profile' page. If the request method is GET, it renders the 'chooseavtar.html' template.
    """
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
    """
    This view is responsible for displaying the selected profile and handling the selection of a profile.
    If the request method is POST, it redirects to the 'language' page.
    If the request method is GET, it retrieves the child name and avatar image URL from the session.
    It renders the 'selectavtar.html' template, passing the child name and avatar URL as context variables.
    """
    if request.method == 'POST':
        return redirect('language')
    child_name = request.session.get('child_name')
    avatar_image = request.session.get('avatar_url')
    return render(request, 'selectavtar.html', {'child_name': child_name, 'avatar_url': avatar_image})


def language(request):
    """
    This view is responsible for displaying the language selection page.
    It retrieves the child name and avatar image URL from the session.
    It also retrieves the available options and English levels.
    If the request method is POST, it handles the selected option and level.
    - If the selected option is 'BL', 'ML1', 'ML2', or 'EL', it redirects to the 'aop_num' view.
    - Otherwise, it redirects to the 'start_assesment' view.
    If the request method is GET, it renders the 'select_lan.html' template, passing the necessary context variables.
    """
    child_name = request.session.get('child_name')
    avatar_image = request.session.get('avatar_url')
    options = MyModel.OPTION_CHOICES
    eng_level = Aop_sub_lan.OPTION_CHOICES

    if request.method == 'POST':
        selected_option = request.POST.get('option')
        selected_level = request.POST.get('options')
        request.session['selected_level'] = selected_level

        # if selected_option == 'option1':
        #     with open('1.json') as f:
        #         json_data = json.load(f)
        # elif selected_option == 'option2':
        #     with open('2.json') as f:
        #         json_data = json.load(f)
        # else:
        #     pass
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
    """
    This view is responsible for rendering the AOP assessment start page.
    """
    return render(request, 'AOP_PRO/six_one.html')


def start_assesment(request,selected_option):
    """
    This view is responsible for rendering the assessment start page.
    It receives the 'selected_option' parameter to determine the assessment type.
    It retrieves the 'enrollment_id' and 'status' from the session.
    If the request method is POST and the selected level is 'BL' or 'ML1',
    it redirects to the 'bl' view.
    It renders the 'start_assesment.html' template, passing the 'selected_option',
    'selected_level', and 'status' as context variables.
    """
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
    """
    This view is responsible for redirecting to different views based on the selected option.
    It receives the 'selected_option' parameter and stores it in the session.
    It retrieves the 'selected_option' and 'selected_level' from the session.
    If the request method is POST, it checks the selected option and redirects accordingly.
    If the selected option is 'BL', it redirects to the 'bl' view.
    If the selected option is 'ML1', it redirects to the 'ml1' view.
    Otherwise, it redirects to the 'paragraph' view.
    """
    request.session['selected_option'] = selected_option
    selected_option = request.session.get('selected_option')
    selected_level = request.session.get('selected_level')
    if request.method == 'POST':
        selected_option = request.session.get('selected_option')
        if selected_option == 'BL':
            return redirect('bl')
        elif selected_option == 'ML1':
            return redirect('ml1')
        else:
            return redirect('paragraph')

#############################################################################

#                   English Level
def nextpage(request):
    """
    This view handles the submission of a form via POST method.
    It retrieves the selected option from the form data.
    It creates a list 'nomistake_list' and appends the selected option to it.
    It retrieves the first item from the 'nomistake_list' and assigns it to 'nomistake' variable.
    Finally, it returns an HTTP response containing the string representation of 'nomistake'.
    """
    if request.method == 'POST':
        selected_option = request.POST.get('selected_option')
        nomistake_list = []
        nomistake_list.append(selected_option)
        nomistake = nomistake_list[0]
        return HttpResponse(str(nomistake))
    
    
def bl(request):
    """
    This view handles the rendering of the 'bl_startrecording.html' template for the BL (Basic Level) assessment.
    It retrieves the selected option and level from the session variables.
    It also retrieves the enrollment ID and phone number from the session variables.
    The 'mobile_number' is included in the context dictionary for rendering purposes.
    If the request method is POST, it redirects to the 'start_recording_bl' view.
    Otherwise, it renders the 'bl_startrecording.html' template with the provided context.
    """
    selected_option = request.session.get('selected_option')
    selected_level = request.session.get('selected_level')
    enrollment_id = request.session.get('enrollment_id')
    phone_number = request.session.get('phone_number')
    enrollment_id = request.session.get('enrollment_id')

    context = {
        'mobile_number': phone_number,
    }
    if request.method == 'POST':
        return redirect('start_recording_bl')
    return render(request, 'AOP_PRO/bl_startrecording.html',context)


def start_recording_bl(request):
    """
    This view handles the rendering of the 'bl_recording.html' template for recording the BL (Basic Level) assessment.
    It calls the 'get_random_paragraph' function to retrieve a random paragraph and data ID for the assessment.
    The retrieved paragraph and data ID are included in the context dictionary for rendering purposes.
    The 'recording' flag is set to True in the context to indicate that recording is active.
    Finally, it renders the 'bl_recording.html' template with the provided context.
    """
    paragraph, data_id = get_random_paragraph(request)
    context = {"val": paragraph, "recording": True, "data_id": data_id}
    return render(request, "AOP_PRO/bl_recording.html", context)


def bl_next(request):
    """
    This view handles the rendering of the 'bl_startrecording_next.html' template for the next step in the BL (Basic Level) assessment.
    It retrieves the selected option, selected level, phone number, and enrollment ID from the session.
    If the request method is POST, it redirects to the 'start_recording_next_bl' view.
    Otherwise, it renders the 'bl_startrecording_next.html' template with the provided context.
    """
    selected_option = request.session.get('selected_option')
    selected_level = request.session.get('selected_level')
    phone_number = request.session.get('phone_number')
    enrollment_id = request.session.get('enrollment_id')
    if request.method == 'POST':
        return redirect('start_recording_next_bl')
    return render(request, 'AOP_PRO/bl_startrecording_next.html',{'mobile_number': phone_number})


def start_recording_next_bl(request):
    """
    This view handles the rendering of the 'bl_recording_next.html' template for the next step in the BL (Basic Level) assessment.
    It calls the 'get_random_paragraph' function to retrieve a random paragraph and its associated data ID.
    The paragraph and data ID are passed as context to the template.
    """
    paragraph, data_id = get_random_paragraph(request)
    context = {"val": paragraph, "recording": True, "data_id": data_id}
    return render(request, "AOP_PRO/bl_recording_next.html", context)


def bl_answer_final(request):
    """
    This view handles the processing of the final answer in the BL (Basic Level) assessment.
    It retrieves the necessary session data such as file paths, selected options, and data IDs.
    Based on the selected option, it retrieves the corresponding data from JSON files.
    It sends a POST request to a transcript API with the audio file and question data.
    The response is processed and relevant information is extracted.
    The transcript, mistake details, fluency, and other data are passed to the 'bl_answer_final.html' template for rendering.
    """
    filepath = request.session.get('filepath')
    filename = request.session.get('filename')
    selected_option = request.session.get('selected_option')
    if selected_option == 'English':
        data_id = request.session.get('data_id')
        data = json_eng
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break
    elif selected_option == 'BL':
        data_id = request.session.get('data_id')
        data = json_l1_data
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break
    else:
        data_id = request.session.get('data_id')
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
    request.session['transcript'] = response.text
    phone_number = request.session.get('phone_number')
    enrollment_id = request.session.get('enrollment_id')
    if response.status_code == 200:
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
    """
    This view handles the saving of the audio file in the BL (Basic Level) assessment.
    It checks if the request method is POST and if the 'audio_blob' file is present.
    It retrieves the necessary session data such as data ID and value.
    It creates a unique filename based on the data ID and saves the file to the media folder.
    The file path and name are stored in the session for later use.
    The 'bl_answer.html' template is rendered with the file path and mobile number.
    """
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
    """
    This view handles the processing of the audio file in the BL (Basic Level) assessment.
    It retrieves the necessary session data such as file path, file name, selected option, and data ID.
    Based on the selected option, it retrieves the appropriate data (English or BL) and the corresponding paragraph.
    It makes a request to the transcript API with the audio file and paragraph data.
    The transcript and other relevant information are stored in the session.
    If the API response is successful, the transcript data is extracted and formatted.
    The audio URL is generated for playback if the file exists.
    The 'bl_answer.html' template is rendered with the transcript and other data for display.
    """
    filepath = request.session.get('filepath')
    filename = request.session.get('filename')
    selected_option = request.session.get('selected_option')
    if selected_option == 'English':
        data_id = request.session.get('data_id')
        data = json_eng
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break
    elif selected_option == 'BL':
        data_id = request.session.get('data_id')
        data = json_l1_data
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break
    
    else: 
        data_id = request.session.get('data_id')
        data = json_l1_data
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break

    if val:
        phone_number = request.session.get('phone_number')
        enrollment_id = request.session.get('enrollment_id')
        url = 'http://3.7.133.80:8000/gettranscript/'
        files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
        payload = {'language': 'English' ,'question':val}
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        request.session['transcript'] = response.text
        if response.status_code == 200:
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
    # Get the selected option from the session
    selected_option = request.session.get('selected_option')
    
    # Remove existing files from the media folder
    media_folder = os.path.join(settings.MEDIA_ROOT)
    for file in os.listdir(media_folder):
        file_path = os.path.join(media_folder, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except OSError as e:
            # Handle the exception and display an error message
            print(f"Error occurred while deleting file: {file_path}")
            print(f"Error message: {str(e)}")
    
    # Check the selected option and retrieve the appropriate data
    if selected_option == 'English':
        data_id = request.session.get('data_id')
        request.session['audio_recorded'] = True
        data = json_eng
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break
    elif selected_option == 'BL':
        data_id = request.session.get('data_id')
        request.session['audio_recorded'] = True
        data = json_l1_data
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break

    # Render the appropriate template based on the availability of 'val'
    if val:
        return render(request, "AOP_PRO/bl_retake.html", {"recording": True, "val": val})
    else:
        return render(request, 'Error/pages-500.html')


def bl_skip(request):
    # Get the selected option from the session
    selected_option = request.session.get('selected_option')
    
    # Get the data_id from the session
    data_id = request.session.get('data_id')
    
    # Retrieve the data based on the selected option
    if selected_option == 'English':
        data = json_eng
    elif selected_option == 'BL':
        data = json_l1_data
    
    paragraph = None
    
    # Find the corresponding data based on the data_id
    for d in data['Paragraph']:
        if d['id'] == data_id:
            val = d['data']
            break
    
    # Process the text to generate the necessary details
    words = val.split()
    my_list = list(words)
    phone_number = request.session.get('phone_number')
    enrollment_id = request.session.get('enrollment_id')
    last_index = len(my_list)

    del_details = ', '.join([f"{i + 1}-{word}" for i, word in enumerate(my_list[1:])])

    sub_details_index = 0
    sub_details = f"{sub_details_index}-{my_list[sub_details_index]}"

    # Prepare the BL response
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

    # Convert the BL response to JSON and store it in the session as transcript
    transcript = json.dumps(bl_response)
    request.session['transcript'] = transcript
    
    # Render the bl_answer.html template with the necessary details
    return render(request, 'AOP_PRO/bl_answer.html', {'originaltext': val, 'wcpm': None, 'no_mistakes': last_index, 'mobile_number': phone_number})


def bl_skip_next(request):
    # Get the selected option from the session
    selected_option = request.session.get('selected_option')
    
    # Get the data_id from the session
    data_id = request.session.get('data_id')
    
    # Retrieve the data based on the selected option
    data = json_l1_data
    
    paragraph = None
    
    # Find the corresponding data based on the data_id
    for d in data['Paragraph']:
        if d['id'] == data_id:
            val = d['data']
            break
    
    # Process the text to generate the necessary details
    words = val.split()
    my_list = list(words)
    last_index = len(my_list)
    del_details = ', '.join([f"{i + 1}-{word}" for i, word in enumerate(my_list[1:])])
    sub_details_index = 0
    sub_details = f"{sub_details_index}-{my_list[sub_details_index]}"
    
    # Prepare the BL response
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
    
    # Convert the BL response to JSON and store it in the session as transcript
    transcript = json.dumps(bl_response)
    request.session['transcript'] = transcript
    
    # Get phone number from the session
    phone_number = request.session.get('phone_number')
    enrollment_id = request.session.get('enrollment_id')
    
    # Render the bl_answer_final.html template with the necessary details
    return render(request, 'AOP_PRO/bl_answer_final.html', {'originaltext':val ,'wcpm': None,'no_mistakes': last_index, 'mobile_number': phone_number})


def bl_store(request):
    if request.method == 'POST':
        # Retrieve the fluency_adjustment value from the form
        fluency_adjustment = request.POST.get('fluency_adjustment')
        
        # Determine the ans_next_level based on the fluency_adjustment value
        if fluency_adjustment == '0':
            request.session['ans_next_level'] = 'L2'
        else:
            request.session['ans_next_level'] = 'L1'
        
        # Retrieve necessary values from the session
        enrollment_id = request.session.get('enrollment_id')
        status = request.session.get('status')
        filepath = request.session.get('filepath')
        bl_rec = request.session.get('transcript')
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
        
        data = json_l1_data
        paragraph = None
        
        # Find the corresponding data based on the data_id
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break
        
        if val:
            # Prepare the data to be sent for saving progress
            ans_next_level = request.session.get('ans_next_level')
            data = {
                "student_id": id_value,
                "sample_id": "data_id",
                "level": 'L2',
                "question": val,
                "section": 'reading',
                "answer": text,
                "audio_url": audio_url,
                "mistakes_count": '0',
                "no_mistakes": no_mistakes,
                "no_mistakes_edited": fluency_adjustment,
                "api_process_time": process_time,
                "language": 'English',
                "no_del": no_del,
                "del_details": del_details,
                "no_sub": no_sub,
                "sub_details": sub_details,
                "test_type": status,
                "next_level": ans_next_level,
                "program": my_program
            }
            
            # Send the data for saving progress via API
            url = 'https://parakh.pradigi.org/v1/saveprogress/'
            files = []
            payload = {'data': json.dumps(data)}
            headers = {}
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            
            # Redirect to the appropriate view based on the fluency_adjustment value
            if fluency_adjustment == '0':
                return redirect('bl_mcq_next')  # redirect to bl_mcq function
            else:
                return redirect('bl_next')


def bl_next_store(request):
    if request.method == 'POST':
        try:
            # Retrieve and validate the fluency_adjustment value from the form
            fluency_adjustment = request.POST.get('fluency_adjustment')
            number = int(fluency_adjustment)
            
            if fluency_adjustment == '0':
                request.session['ans_next_level'] = 'L2'
            else:
                request.session['ans_next_level'] = 'L1'
            
            # Retrieve necessary values from the session
            enrollment_id = request.session.get('enrollment_id')
            status = request.session.get('status')
            filepath = request.session.get('filepath')
            bl_rec = request.session.get('transcript')
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
            data_id = request.session.get('data_id')
            my_program = request.session.get('my_program')
            
            data = json_l1_data
            paragraph = None
            
            # Find the corresponding data based on the data_id
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
            
            if val:
                # Prepare the data to be sent for saving progress
                ans_next_level = request.session.get('ans_next_level')
                data = {
                    "student_id": id_value,
                    "sample_id": "data_id",
                    "level": 'L2',
                    "question": val,
                    "section": 'reading',
                    "answer": text,
                    "audio_url": audio_url,
                    "mistakes_count": '0',
                    "no_mistakes": no_mistakes,
                    "no_mistakes_edited": fluency_adjustment,
                    "api_process_time": process_time,
                    "language": 'English',
                    "no_del": no_del,
                    "del_details": del_details,
                    "no_sub": no_sub,
                    "sub_details": sub_details,
                    "test_type": status,
                    "next_level": ans_next_level,
                    "program": my_program
                }
                
                # Send the data for saving progress via API
                url = 'https://parakh.pradigi.org/v1/saveprogress/'
                files = []
                payload = {'data': json.dumps(data)}
                headers = {}
                response = requests.request("POST", url, headers=headers, data=payload, files=files)
                response_data = json.loads(response.text)
                
                if number == 0:
                    return redirect('bl_mcq_next')
                else:
                    # Retrieve additional values from the session
                    phone_number = request.session.get('phone_number')
                    enrollment_id = request.session.get('enrollment_id')
                    
                    # Prepare the context for rendering the template
                    context = {
                        'mobile_number': phone_number,
                        'level': "beginner"
                    }
                    return render(request, "AOP_PRO/ans_page_aop.html", context=context)
        except TypeError:
            return HttpResponse("Invalid adjustment value")

    
def get_random_sentence(request):
    selected_option = request.session.get('selected_option')
    
    # Check the selected_option to determine the data source
    if selected_option == 'BL':
        data = json_l1_data
    else:
        data = json_l1_data
    
    # Select a random sentence from the data
    data1 = random.choice(data['Sentence'])
    data_id = data1['id']
    
    # Store the data_id in the session
    request.session['data_id'] = data_id
    
    # Retrieve the language information
    languages = data1['language']
    
    # Return the data, data_id, and languages as a dictionary
    return {
        'data': data1['data'],
        'data_id': data_id,
        'languages': languages,
    }
       


def bl_mcq_api(request):
    # Get session variables
    selected_option = request.session.get('selected_option')
    selected_level = request.session.get('selected_level')

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
        my_program = request.session.get('my_program')

        # Retrieve data from json_l1_data
        data = json_l1_data
        val = None
        answer = None

        for d in data['Sentence']:
            if d['id'] == data_id:
                val = d['data']
                break

        # Set selected language
        if selected_language == 'hindi':
            request.session['lan'] = selected_language
        elif selected_language == 'marathi':
            request.session['lan'] = selected_language

        # Retrieve data based on selected language
        if selected_language == 'hindi':
            # Find the data with matching data_id
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
            # Find the data with matching data_id
            selected_data = next((item for item in data['Sentence'] if item['id'] == data_id), None)
            if selected_data:
                languages = selected_data['language']
                selected_language = languages.get(selected_language)
                options = selected_language.get('options')
                answer = selected_language.get('answers')
            else:
                pass

        lan = request.session.get('lan')

        # Prepare data for API request
        data = {}
        data["student_id"] = id_value
        data["sample_id"] = data_id
        data["level"] = 'L1'
        data["question"] = val
        data["section"] = 'MCQ'
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

        url = 'https://parakh.pradigi.org/v1/saveprogress/'
        files = []
        payload = {'data': json.dumps(data)}
        headers = {}
        
        # Make API request to save progress
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        response_data = json.loads(response.text)

        # Delete the 'data_id' session variable
        del request.session['data_id']

        # Redirect to 'ml1' view
        return redirect('ml1')
       

def bl_final_mcq(request):
    # Retrieve 'my_context' from session
    context = request.session.get('my_context', {})

    if request.method == 'POST':
        selected_div = request.POST.get('selected-div')
        selected_divid = request.POST.get('selected-div_id')
        
        # Update context with selected values
        context['selected_divid'] = selected_divid
        context['selected_div'] = selected_div
        selected_language = request.POST.get('selected_language')
        context['selected_language'] = selected_language
        
        # Render 'bl_mcq.html' template with updated context
        return render(request, "AOP_PRO/bl_mcq.html", context)
    
    # Add 'selected_div' to context
    context['selected_div'] = context.get('selected_div')

    # Render 'bl_mcq.html' template with context
    return render(request, "AOP_PRO/bl_mcq.html", context)


def bl_mcq(request):
    # Retrieve 'phone_number' and 'enrollment_id' from session
    phone_number = request.session.get('phone_number')
    enrollment_id = request.session.get('enrollment_id')

    # Get random sentence data
    data = get_random_sentence(request)

    # Create context dictionary with initial values
    context = {"val": data['data'], "recording": True, "data_id": data['data_id'], "languages": data['languages'], 'mobile_number': phone_number}

    if request.method == 'POST':
        selecteddiv = request.session.get('selected-div')
        data_id = request.session.get('data_id')
        transcript = request.session.get('transcript')

        # Redirect to 'ml1' view
        return redirect('ml1')

    # Render 'bl_mcq.html' template with context
    return render(request, "AOP_PRO/bl_mcq.html", context)


def bl_mcq_next(request):
    # Get random sentence data
    data = get_random_sentence(request)

    # Create context dictionary with initial values
    context = {"val": data['data'], "recording": True, "data_id": data['data_id'], "languages": data['languages']}

    # Store context in session
    request.session['my_context'] = context

    # Retrieve 'phone_number' and 'enrollment_id' from session
    phone_number = request.session.get('phone_number')
    enrollment_id = request.session.get('enrollment_id')

    if request.method == 'POST':
        # Redirect to 'ml1' view
        return redirect('ml1')

    # Render 'bl_mcq_next.html' template with context
    return render(request, "AOP_PRO/bl_mcq_next.html", context)


def bl_answer_page(request):
    # Retrieve 'phone_number' and 'enrollment_id' from session
    phone_number = request.session.get('phone_number')
    enrollment_id = request.session.get('enrollment_id')

    # Create context dictionary with 'mobile_number' value
    context = {
        'mobile_number': phone_number,
    }

    # Render 'bl_cong.html' template with context
    return render(request, "AOP_PRO/bl_cong.html", context=context)


def error_recording(request):
    if request.method == 'GET':
        # Retrieve 'data_id' from session
        data_id = request.session.get('data_id')

        # Find the paragraph with matching 'data_id'
        data = json_l1_data
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                paragraph = d['data']
                break

        if paragraph:
            # If paragraph is found, store it in session
            request.session['paragraph'] = paragraph

    # Redirect to 'start' view
    return redirect('start')


def start(request):
    # Retrieve 'paragraph' from session
    paragraph = request.session.get('paragraph')

    # Render the 'bl_recording.html' template with the paragraph value
    return render(request, "AOP_PRO/bl_recording.html", {'val': paragraph})


def get_random_ml1(request):
    # Retrieve selected option from session
    selected_option = request.session.get('selected_option')

    # Retrieve ML1 data
    data = json_l1_data

    # Select a random paragraph from the ML1 data
    data1 = random.choice(data['Paragraph'])

    # Get the data and data_id of the selected paragraph
    data_id = data1['id']
    
    # Store the data_id in the session
    request.session['data_id'] = data_id

    # Return the paragraph data and data_id
    return data1['data'], data_id


def nextpage(request):
    if request.method == 'POST':
        # Retrieve selected option from the request POST data
        selected_option = request.POST.get('selected_option')

        # Create a list to store the selected option
        nomistake_list = []
        nomistake_list.append(selected_option)

        # Retrieve the selected option from the list
        nomistake = nomistake_list[0]

        # Return the selected option as an HTTP response
        return HttpResponse(str(nomistake))
    

def ml1(request):
    phone_number = request.session.get('phone_number')
    enrollment_id = request.session.get('enrollment_id')

    if request.method == 'POST':
        # Remove 'filename' and 'filepath' from session
        del request.session['filename']
        del request.session['filepath']

        # Redirect to 'start_recording_ml1' view
        return redirect('start_recording_ml1')

    # Render the template with the phone number
    return render(request, 'AOP_PRO/ml1_startrecording.html', {'mobile_number': phone_number})


def start_recording_ml1(request):
    # Get a random paragraph and data ID for ML1
    paragraph, data_id = get_random_ml1(request)

    # Retrieve phone number and enrollment ID from session
    phone_number = request.session.get('phone_number')
    enrollment_id = request.session.get('enrollment_id')

    # Prepare context for rendering the template
    context = {"val": paragraph, "recording": True, "data_id": data_id, 'mobile_number': phone_number}

    # Render the template for ML1 recording
    return render(request, "AOP_PRO/ml1_recording.html", context)


def ml1_next(request):
    # Retrieve selected option and level from session
    selected_option = request.session.get('selected_option')
    selected_level = request.session.get('selected_level')

    # Retrieve filepath, phone number, and enrollment ID from session
    filepath = request.session.get('filepath')
    phone_number = request.session.get('phone_number')
    enrollment_id = request.session.get('enrollment_id')

    if request.method == 'POST':
        # Redirect to the start recording page for the next ML1 task
        return redirect('start_recording_next_ml1')

    # Render the template for the next ML1 task's start recording page
    return render(request, 'AOP_PRO/ml1_startrecording_next.html', {'mobile_number': phone_number})


def get_random_ml1_sentence(request):
    # Retrieve selected option from session
    selected_option = request.session.get('selected_option')

    if selected_option == 'ML1':
        # Retrieve random sentence data from JSON file for ML1 option
        data = json_l2
        data1 = random.choice(data['Sentence'])
        data_id = data1['id']
        request.session['data_id'] = data_id
        languages = data1['language']
        return {
            'data': data1['data'],
            'data_id': data_id,
            'languages': languages,
        }
    else:
        # Retrieve random sentence data from JSON file for other options
        data = json_l2_data
        data1 = random.choice(data['Sentence'])
        data_id = data1['id']
        request.session['data_id'] = data_id
        languages = data1['language']
        return {
            'data': data1['data'],
            'data_id': data_id,
            'languages': languages,
        }


def start_recording_next_ml1(request):
    # Retrieve a random paragraph and data ID
    paragraph, data_id = get_random_paragraph(request)

    # Retrieve phone number and enrollment ID from session
    phone_number = request.session.get('phone_number')
    enrollment_id = request.session.get('enrollment_id')

    # Prepare the context for rendering the template
    context = {"val": paragraph, "recording": True, "data_id": data_id, 'mobile_number': phone_number}
    return render(request, "AOP_PRO/ml1_recording_next.html", context)


def ml1_answer_final(request):
    # Retrieve session data
    filepath = request.session.get('filepath')
    filename = request.session.get('filename')
    selected_option = request.session.get('selected_option')
    
    # Determine the selected option and retrieve the corresponding data
    if selected_option == 'English':
        data_id = request.session.get('data_id')
        data = json_eng
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break
    elif selected_option == 'BL':
        data_id = request.session.get('data_id')
        data = json_l2_data
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break
    
    # Perform transcript request and retrieve response
    data_id = request.session.get('data_id')
    data = json_l2_data
    paragraph = None
    for d in data['Paragraph']:
        if d['id'] == data_id:
            val = d['data']
            break
    if val:
        url = 'http://3.7.133.80:8000/gettranscript/'
        files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
        payload = {'language': 'English' ,'question':val}
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        request.session['ml1_res'] = response.text
        
        # Retrieve phone number and enrollment ID from session
        phone_number = request.session.get('phone_number')
        
        # Process response data if request is successful
        if response.status_code == 200:
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
            
            # Render the template with the processed data
            return render(request, 'AOP_PRO/ml1_answer_final.html', {'transcript': data_string, 'text':data_string, 'originaltext':val , 'sub_details':index,'del_details':deld, 'audio_url': audio_url, 'no_mistakes': mistake, 'wcpm': wcpm_formatted, 'mobile_number': phone_number})
        else:
            # Render an error page if the request fails
            return render(request, 'Error/pages-500.html')
    else:
        # Render an error page if the data is not found
        return render(request, 'Error/pages-500.html')


@csrf_exempt
def save_file_ml1(request):
    # Check if the request method is POST and an audio file is present
    if request.method == 'POST' and request.FILES.get('audio_blob'):
        # Retrieve necessary session data
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        filename = f'{data_id}.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        phone_number = request.session.get('phone_number')
        enrollment_id = request.session.get('enrollment_id')
        
        # Save the audio file to the specified filepath
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
            request.session['filepath'] = filepath
            request.session['filename'] = filename
            
            # Render the template with the filepath and phone number
            return render(request, 'AOP_PRO/ml1_answer.html', {'filepath': filepath, 'mobile_number': phone_number})


def ml1_answer(request):
    filepath = request.session.get('filepath')
    filename = request.session.get('filename')
    selected_option = request.session.get('selected_option')
    data_id = request.session.get('data_id')
    data = json_l1_data
    paragraph = None
    for d in data['Paragraph']:
        if d['id'] == data_id:
            val = d['data']
            break

    if val:
        print("the val", val)

    # Make a request to obtain the transcript for the audio file
    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': 'English', 'question': val}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    request.session['ml1_res'] = response.text
    phone_number = request.session.get('phone_number')
    enrollment_id = request.session.get('enrollment_id')

    if response.status_code == 200:
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

        return render(request, 'AOP_PRO/ml1_answer.html', {
            'transcript': data_string,
            'text': data_string,
            'originaltext': val,
            'sub_details': index,
            'del_details': deld,
            'audio_url': audio_url,
            'no_mistakes': mistake,
            'wcpm': wcpm_formatted,
            'mobile_number': phone_number
        })
    else:
        return render(request, 'Error/pages-500.html')


def ml1_retake(request):
    # Remove previously recorded audio files
    selected_option = request.session.get('selected_option')
    media_folder = os.path.join(settings.MEDIA_ROOT)
    for file in os.listdir(media_folder):
        file_path = os.path.join(media_folder, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(e)

    data_id = request.session.get('data_id')
    request.session['audio_recorded'] = True
    data = json_l2_data
    paragraph = None
    for d in data['Paragraph']:
        if d['id'] == data_id:
            val = d['data']
            break

    if val:
        print("the val", val)

    phone_number = request.session.get('phone_number')
    enrollment_id = request.session.get('enrollment_id')
    
    return render(request, "AOP_PRO/ml1_retake.html", {"recording": True, "val": val, 'mobile_number': phone_number })
   

def ml1_skip(request):
    selected_option = request.session.get('selected_option')
    data_id = request.session.get('data_id')
    data = json_l2_data
    paragraph = None
    for d in data['Paragraph']:
        if d['id'] == data_id:
            val = d['data']
            break

    words = val.split()
    my_list = list(words)
    phone_number = request.session.get('phone_number')
    enrollment_id = request.session.get('enrollment_id')
    
    # Simulate ML1 response with skipped details
    ml1_res = {}
    last_index = len(my_list)
    del_details = ', '.join([f"{i + 1}-{word}" for i, word in enumerate(my_list[1:])])
    sub_details_index = 0
    sub_details = f"{sub_details_index}-{my_list[sub_details_index]}"
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
    return render(request, 'AOP_PRO/ml1_answer.html', {'originaltext': val, 'wcpm': None, 'no_mistakes': last_index, 'mobile_number': phone_number})


def ml1_skip_next(request):
    data_id = request.session.get('data_id')
    data = json_l2_data
    paragraph = None
    for d in data['Paragraph']:
        if d['id'] == data_id:
            val = d['data']
            break

    words = val.split()
    my_list = list(words)
    phone_number = request.session.get('phone_number')
    enrollment_id = request.session.get('enrollment_id')
    
    # Simulate ML1 response with skipped details
    last_index = len(my_list)
    del_details = ', '.join([f"{i + 1}-{word}" for i, word in enumerate(my_list[1:])])
    sub_details_index = 0
    sub_details = f"{sub_details_index}-{my_list[sub_details_index]}"
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
    return render(request, 'AOP_PRO/ml1_answer_final.html', {'originaltext': val, 'wcpm': None, 'no_mistakes': last_index, 'mobile_number': phone_number})


def ml1_store(request):
  if request.method == 'POST':
    try:
        fluency_adjustment = request.POST.get('fluency_adjustment')
        # Determine the next level based on the fluency adjustment
        if fluency_adjustment == '0':
            request.session['ans_next_level'] = 'L3'
        else:
            request.session['ans_next_level'] = 'L2'

        enrollment_id = request.session.get('enrollment_id')
        status = request.session.get('status')
        filepath = request.session.get('filepath')
        ml1_res = request.session.get('ml1_res')
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
        data_id = request.session.get('data_id')
        my_program = request.session.get('my_program')
        data = json_l1_data
        paragraph = None
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break
        if val:
            print("question",val)

        selected_option = request.session.get('selected_option')
        ans_next_level = request.session.get('ans_next_level')
        # Prepare data for saving progress
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
        response_data = json.loads(response.text)
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
            
            # Determine the next level based on the fluency adjustment value
            if fluency_adjustment == '0':
                request.session['ans_next_level'] = 'L3'
            else:
                request.session['ans_next_level'] = 'L2'

            enrollment_id = request.session.get('enrollment_id')
            status = request.session.get('status')
            filepath = request.session.get('filepath')
            ml1_res = request.session.get('ml1_res')
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
            data_id = request.session.get('data_id')
            my_program = request.session.get('my_program')

            data = json_l1_data
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break
            if val:
                print("question", val)

            selected_option = request.session.get('selected_option')
            ans_next_level = request.session.get('ans_next_level')

            # Prepare data for saving progress
            data = {}
            data["student_id"] = id_value
            data["sample_id"] = "data_id"
            data["level"] = 'L2'
            data["question"] = val
            data["section "] = 'reading'
            data["answer"] = text
            data["audio_url"] = audio_url
            data["mistakes_count"] = '0'
            data["no_mistakes"] = no_mistakes
            data["no_mistakes_edited"] = fluency_adjustment
            data["api_process_time"] = process_time
            data["language"] = 'English'
            data["no_del"] = no_del
            data["del_details"] = del_details
            data["no_sub"] = no_sub
            data["sub_details"] = sub_details
            data["test_type"] = status
            data["next_level"] = ans_next_level
            data["program"] = my_program

            url = 'https://parakh.pradigi.org/v1/saveprogress/'
            files = []
            payload = {'data': json.dumps(data)}
            headers = {}
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            response_data = json.loads(response.text)

            if fluency_adjustment == '0':
                return redirect('ml1_mcq_next')  # redirect to bl_mcq function
            else:
                phone_number = request.session.get('phone_number')
                enrollment_id = request.session.get('enrollment_id')
                
                # Render the answer page for AOP with the appropriate context
                context = {
                    'mobile_number': phone_number,
                    'level': "L1-sentence"
                }
                return render(request, "AOP_PRO/ans_page_aop.html", context=context)
        except TypeError:
            return HttpResponse("Invalid adjustment value")


def ml1_final_mcq(request):
    # Retrieve the context from the session
    context = request.session.get('ml1_context', {})
    
    if request.method == 'POST':
        selected_div = request.POST.get('selected-div')
        selected_divid = request.POST.get('selected-div_id')
        
        # Update the context with the selected division and its ID
        context['selected_divid'] = selected_divid
        context['selected_div'] = selected_div
        
        selected_language = request.POST.get('selected_language')
        
        # Update the context with the selected language
        context['selected_language'] = selected_language
        
        return render(request, "AOP_PRO/ml1_mcq.html", context)
    
    # Render the MCQ page with the context
    return render(request, "AOP_PRO/ml1_mcq.html", context)


def ml1_mcq(request):
    # Retrieve the selected option and level from the session
    selected_option = request.session.get('selected_option')
    selected_level = request.session.get('selected_level')
    
    # Get random ML1 sentence data
    data = get_random_ml1_sentence(request)
    
    # Prepare the context for rendering the MCQ page
    context = {
        "val": data['data'],            # Sentence data
        "recording": True,              # Flag indicating if recording is enabled
        "data_id": data['data_id'],     # ID of the data
        "languages": data['languages']  # Available languages for translation
    }
    
    if request.method == 'POST':
        # Get the transcript from the session
        transcript = request.session.get('transcript')
        
        # Redirect to the next view (e.g., ml2)
        return redirect('ml2')
    
    # Render the MCQ page with the context
    return render(request, "AOP_PRO/ml1_mcq.html", context)


def ml1_mcq_next(request):
    # Get random ML1 sentence data
    data = get_random_ml1_sentence(request)
    
    # Prepare the context for rendering the MCQ page
    context = {
        "val": data['data'],            # Sentence data
        "recording": True,              # Flag indicating if recording is enabled
        "data_id": data['data_id'],     # ID of the data
        "languages": data['languages']  # Available languages for translation
    }
    
    # Store the context in the session
    request.session['ml1_context'] = context
    
    if request.method == 'POST':
        # Get the transcript from the session
        transcript = request.session.get('transcript')
        
        # Redirect to the next view (e.g., ml2)
        return redirect('ml2')
    
    # Render the MCQ page with the context
    return render(request, "AOP_PRO/ml1_mcq_next.html", context)


def ml1_mcq_api(request):
    selected_option = request.session.get('selected_option')
    selected_level = request.session.get('selected_level')

    if request.method == 'POST':
        # Retrieve data from the request
        selected_lan = request.POST.get('selected_language_input')
        status = request.session.get('status')
        selected_language = request.POST.get('selected_language')
        selected_div = request.POST.get('selected-div')
        data_id = request.session.get('data_id')
        id_value = request.session.get('id_value')
        ml1_res = request.session.get('ml1_res')
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
        
        # Retrieve data from json_l2_data based on data_id and selected_language
        data = json_l2_data
        Sentence = None
        for d in data['Sentence']:
            if d['id'] == data_id:
                val = d['data']
                break
        
        if selected_language == 'hindi':
            request.session['lan'] = selected_language
        elif selected_language == 'marathi':
            request.session['lan'] = selected_language
        
        # Retrieve options and answers based on selected_language
        if selected_language == 'hindi' or selected_language == 'marathi':
            data = json_l2_data
            selected_data = next((item for item in data['Sentence'] if item['id'] == data_id), None)
            if selected_data:
                languages = selected_data['language']
                selected_language = languages.get(selected_language)
                options = selected_language.get('options')
                answer = selected_language.get('answers')
            else:
                print("Data not found for the given data_id")
        
        # Retrieve lan from session
        lan = request.session.get('lan')
        
        # Prepare the data to be sent for saving progress
        data = {}
        data["student_id"] = id_value
        data["sample_id"] = "data_id"
        data["level"] = 'L1'
        data["question"] = val
        data["section"] = 'MCQ'
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
        
        url = 'https://parakh.pradigi.org/v1/saveprogress/'
        files = []
        payload = {'data': json.dumps(data)}
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        response_data = json.loads(response.text)
        
        # Redirect to the next view (e.g., ml2)
        return redirect('ml2')
  
    
#############################################################################################

def get_random_ml2(request):
    # Retrieve ML2 data from json_l3_data
    data = json_l3_data
    
    # Randomly select a paragraph from the data
    data1 = random.choice(data['Paragraph'])
    data_id = data1['id']
    
    # Store the selected data_id in the session
    request.session['data_id'] = data_id
    
    # Return the data and data_id
    return data1['data'], data_id
   

def nextpage(request):
    if request.method == 'POST':
        # Retrieve the selected_option from the POST data
        selected_option = request.POST.get('selected_option')
        
        # Create a list to store the selected_option
        nomistake_list = []
        nomistake_list.append(selected_option)
        
        # Retrieve the selected_option from the list
        nomistake = nomistake_list[0]
        
        # Return the selected_option as an HTTP response
        return HttpResponse(str(nomistake))


def ml2(request):
    if request.method == 'POST':
        # If the request method is POST, redirect to the 'start_recording_ml2' view
        return redirect('start_recording_ml2')
    # If the request method is GET, render the 'ml2_startrecording.html' template
    return render(request, 'AOP_PRO/ml2_startrecording.html')


def start_recording_ml2(request):
    # Get a random paragraph and its data_id using the get_random_ml2 function
    paragraph, data_id = get_random_ml2(request)
    
    # Prepare the context data for rendering the template
    context = {"val": paragraph, "recording": True, "data_id": data_id}
    
    # Render the 'ml2_recording.html' template with the provided context
    return render(request, "AOP_PRO/ml2_recording.html", context)


def ml2_next(request):
    selected_option = request.session.get('selected_option')
    selected_level = request.session.get('selected_level')
    
    if request.method == 'POST':
        # If the request method is POST, redirect to the 'start_recording_next_ml2' view
        return redirect('start_recording_next_ml2')
    
    # If the request method is not POST, render the 'ml2_startrecording_next.html' template
    return render(request, 'AOP_PRO/ml2_startrecording_next.html')


def get_random_ml2_sentence(request):
    selected_option = request.session.get('selected_option')
    
    # Check the selected_option value to determine the data source
    if selected_option == 'Ml2':
        # If selected_option is 'Ml2', use json_l3_data for sentence data
        data = json_l3_data
    else:
        # Otherwise, use json_l3_data for sentence data
        data = json_l3_data
    
    # Randomly select a sentence from the data
    data1 = random.choice(data['Sentence'])
    data_id = data1['id']
    request.session['data_id'] = data_id
    languages = data1['language']
    
    return {
        'data': data1['data'],
        'data_id': data_id,
        'languages': languages,
    }


def start_recording_next_ml2(request):
    # Retrieve a random paragraph and data ID
    paragraph, data_id = get_random_paragraph(request)
    
    # Prepare the context for the template
    context = {"val": paragraph, "recording": True, "data_id": data_id}
    
    # Render the template with the provided context
    return render(request, "AOP_PRO/ml2_recording_next.html", context)


def ml2_answer_final(request):
    filepath = request.session.get('filepath')
    filename = request.session.get('filename')
    selected_option = request.session.get('selected_option')
    data_id = request.session.get('data_id')
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
    request.session['ml2_res'] = response.text
    if response.status_code == 200:
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
    """
    View function to save an audio file for ML2 processing.

    - Accepts a POST request with an audio file.
    - Saves the file in the media folder with a unique filename.
    - Updates the session variables with the file path and name.
    - Renders the 'ml2_answer.html' template with the file path.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Raises:
        None
    """
    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        filename = f'{data_id}.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
            request.session['filepath'] = filepath
            request.session['filename'] = filename
            return render(request, 'AOP_PRO/ml2_answer.html', { 'filepath': filepath})


def ml2_answer(request):
    """
    View function to process ML2 answer.

    - Retrieves the file path, selected option, and data ID from session variables.
    - Sends a POST request to an external API to get the transcript for the audio file.
    - Parses the API response and extracts relevant data.
    - Formats the data and prepares the audio URL.
    - Renders the 'ml2_answer.html' template with the transcript and other data.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Raises:
        None
    """
    filepath = request.session.get('filepath')
    filename = request.session.get('filename')
    selected_option = request.session.get('selected_option')
    data_id = request.session.get('data_id')
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
    request.session['ml2_res'] = response.text

    if response.status_code == 200:
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
    """
    View function to retake ML2 recording.

    - Removes the audio file from the media folder.
    - Retrieves the data ID from session variables.
    - Sets the 'audio_recorded' flag in the session.
    - Renders the 'ml2_retake.html' template for recording.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Raises:
        None
    """
    selected_option = request.session.get('selected_option')
    media_folder = os.path.join(settings.MEDIA_ROOT)
    for file in os.listdir(media_folder):
        file_path = os.path.join(media_folder, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(e)

    data_id = request.session.get('data_id')
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
    """
    View function to skip ML2 recording and generate a mock transcript.

    - Retrieves the data ID from session variables.
    - Retrieves the corresponding data paragraph from the JSON data.
    - Generates a mock transcript with no mistakes and deletion details.
    - Formats the transcript and sets it in the session.
    - Renders the 'ml2_answer.html' template with the mock transcript.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Raises:
        None
    """
    data_id = request.session.get('data_id')
    data = json_l3_data
    paragraph = None
    for d in data['Paragraph']:
        if d['id'] == data_id:
            val = d['data']
            break

    words = val.split()
    my_list = list(words)
    last_index = len(my_list) 
    del_details = ', '.join([f"{i + 1}-{word}" for i, word in enumerate(my_list[1:])])
    sub_details_index = 0
    sub_details = f"{sub_details_index}-{my_list[sub_details_index]}"
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
    """
    View function to skip ML2 recording and generate a mock transcript for the next step.

    - Retrieves the data ID from session variables.
    - Retrieves the corresponding data paragraph from the JSON data.
    - Generates a mock transcript with no mistakes and deletion details.
    - Formats the transcript and sets it in the session.
    - Renders the 'ml2_answer_final.html' template with the mock transcript.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Raises:
        None
    """
    data_id = request.session.get('data_id')
    data = json_l3_data
    paragraph = None
    for d in data['Paragraph']:
        if d['id'] == data_id:
            val = d['data']
            break

    words = val.split()
    my_list = list(words)
    last_index = len(my_list) 
    del_details = ', '.join([f"{i + 1}-{word}" for i, word in enumerate(my_list[1:])])
    sub_details_index = 0
    sub_details = f"{sub_details_index}-{my_list[sub_details_index]}"
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
    """
    View function to store ML2 response and redirect to the next step.

    - Retrieves the fluency adjustment value from the POST request.
    - Validates the adjustment value and sets the 'ans_next_level' session variable accordingly.
    - Retrieves various data from session variables and ML1 transcript.
    - Constructs the data dictionary for saving progress.
    - Sends a POST request to the API to save progress.
    - Redirects to the appropriate next step based on the adjustment value.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Raises:
        TypeError: If the fluency adjustment value is invalid.
    """
    if request.method == 'POST':
        try:
            fluency_adjustment = request.POST.get('fluency_adjustment')
            number = int(fluency_adjustment)
            if fluency_adjustment == '0':
                request.session['ans_next_level'] = 'L4'
            else:
                request.session['ans_next_level'] = 'L3'

            enrollment_id = request.session.get('enrollment_id')
            status = request.session.get('status')
            filepath = request.session.get('filepath')
            ml1_res = request.session.get('ml1_res')
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
            data_id = request.session.get('data_id')
            my_program = request.session.get('my_program')
            data = json_l1_data
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

            if val:
                print("question",val)

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
            url = 'https://parakh.pradigi.org/v1/saveprogress/'
            files = []
            payload = {'data': json.dumps(data)}
            headers = {}
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            response_data = json.loads(response.text)
            if number == 0:
                return redirect('ml2_mcq_next')  # redirect to bl_mcq function
            else:
                return redirect('ml2_next')
        except TypeError:
            return HttpResponse("Invalid adjustment value")


def ml2_next_store(request):
    """
    View function to store ML2 response for the next step.

    - Retrieves the fluency adjustment value from the POST request.
    - Validates the adjustment value and sets the 'ans_next_level' session variable accordingly.
    - Retrieves various data from session variables and ML1 transcript.
    - Constructs the data dictionary for saving progress.
    - Sends a POST request to the API to save progress.
    - Redirects to the appropriate next step based on the adjustment value.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Raises:
        TypeError: If the fluency adjustment value is invalid.
    """
    if request.method == 'POST':
        try:
            fluency_adjustment = request.POST.get('fluency_adjustment')
            
            if fluency_adjustment == '0':
                request.session['ans_next_level'] = 'L4'
            else:
                request.session['ans_next_level'] = 'L3'

            enrollment_id = request.session.get('enrollment_id')
            status = request.session.get('status')
            filepath = request.session.get('filepath')
            ml1_res = request.session.get('ml1_res')
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
            data_id = request.session.get('data_id')
            my_program = request.session.get('my_program')
            data = json_l1
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

            if val:
                print("question",val)

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
            url = 'https://parakh.pradigi.org/v1/saveprogress/'
            files = []
            payload = {'data': json.dumps(data)}
            headers = {}
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            response_data = json.loads(response.text)
            if fluency_adjustment == '0':
                return redirect('ml2_mcq_next')  # redirect to bl_mcq function
            else:
                phone_number = request.session.get('phone_number')
                enrollment_id = request.session.get('enrollment_id')
            
                context = {
                    'mobile_number': phone_number,
                    'level' : "L2-sentence"
                }
                return render(request, "AOP_PRO/ans_page_aop.html", context=context)
        except TypeError:
            return HttpResponse("Invalid adjustment value")


def ml2_mcq_api(request):
    """
    API endpoint to handle the ML2 MCQ submission.

    - Retrieves the selected MCQ option, language, and other relevant data from the request.
    - Constructs the data payload to be sent for saving progress.
    - Sends a POST request to the save progress API.
    - Redirects to the 'ml3' view.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.
    """
    selected_option = request.session.get('selected_option')
    selected_level = request.session.get('selected_level')
    if request.method == 'POST':
        selected_lan = request.POST.get('selected_language_input')
        status = request.session.get('status')
        selected_language = request.POST.get('selected_language')
        selected_div = request.POST.get('selected-div')
        data_id = request.session.get('data_id')
        id_value = request.session.get('id_value')
        ml2_res = request.session.get('ml2_res')
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
        data = json_l3_data
        Sentence = None
        for d in data['Sentence']:
            if d['id'] == data_id:
                val = d['data']
                break
        if selected_language == 'hindi':
            request.session['lan'] = selected_language

        elif selected_language == 'marathi':
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
           
        lan = request.session.get('lan')
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
        
        url = 'https://parakh.pradigi.org/v1/saveprogress/'
        files = []
        payload = {'data': json.dumps(data)}
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        response_data = json.loads(response.text)
        return redirect('ml3')


def ml2_final_mcq(request):
    """
    View function to render the ML2 MCQ page.

    - Retrieves the ML2 context from the session.
    - Handles the POST request to save the selected MCQ option and language.
    - Renders the ML2 MCQ page with the updated context.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.
    """
    context = request.session.get('ml2_context', {})
    if request.method == 'POST':
        selected_div = request.POST.get('selected-div')
        selected_divid = request.POST.get('selected-div_id')
        context['selected_divid'] = selected_divid
        context['selected_div'] = selected_div
        selected_language = request.POST.get('selected_language')
        context['selected_language'] = selected_language
        return render(request, "AOP_PRO/ml2_mcq.html", context)
    return render(request, "AOP_PRO/ml2_mcq.html", context)

            
def ml2_mcq(request):
    """
    Renders the ML2 MCQ page.

    - Retrieves the selected option, level, and a random ML2 sentence for the MCQ.
    - Constructs the context for rendering the page.
    - Redirects to the 'ml3' view upon form submission.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.
    """
    selected_option = request.session.get('selected_option')
    selected_level = request.session.get('selected_level')
    data = get_random_ml2_sentence(request)
    context = {"val": data['data'], "recording": True, "data_id": data['data_id'], "languages": data['languages']}
    if request.method == 'POST':
        return redirect('ml3')
    return render(request, "AOP_PRO/ml2_mcq.html", context)


def ml2_mcq_next(request):
    """
    Renders the next ML2 MCQ page.

    - Retrieves a random ML2 sentence for the next MCQ.
    - Constructs the context for rendering the page.
    - Redirects to the 'ml2' view upon form submission.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.
    """
    data = get_random_ml2_sentence(request)
    context = {"val": data['data'], "recording": True, "data_id": data['data_id'], "languages": data['languages']}
    request.session['ml2_context'] = context
    if request.method == 'POST':
        return redirect('ml2')
    return render(request, "AOP_PRO/ml2_mcq_next.html", context)


#############################################################################################

def get_random_ml3(request):
    """
    Retrieves a random ML3 paragraph and its corresponding data ID.

    - Fetches the ML3 data from a predefined data source.
    - Randomly selects a paragraph.
    - Extracts the paragraph data and data ID.
    - Stores the data ID in the session for future reference.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        tuple: A tuple containing the ML3 paragraph data and its corresponding data ID.
    """
    data = json_l4_data
    data1 = random.choice(data['Paragraph'])
    data_id = data1['id']
    request.session['data_id'] = data_id
    return data1['data'], data_id
            

def nextpage(request):
    """
    Handles the form submission on the next page.

    - Retrieves the selected option from the form data.
    - Stores the selected option in a list.
    - Retrieves the selected option from the list and returns it as an HTTP response.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response containing the selected option.
    """
    if request.method == 'POST':
        selected_option = request.POST.get('selected_option')
        nomistake_list = []
        nomistake_list.append(selected_option)
        nomistake = nomistake_list[0]
        return HttpResponse(str(nomistake))
    

def ml3(request):
    """
    Renders the ML3 start recording page.

    - If the request method is POST, redirects to the 'start_recording_ml3' view.
    - If the request method is GET, renders the ML3 start recording template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response.
    """
    if request.method == 'POST':
        return redirect('start_recording_ml3')
    return render(request, 'AOP_PRO/ml3_startrecording.html')


def start_recording_ml3(request):
    """
    Renders the ML3 recording page.

    - Retrieves a random ML3 paragraph and its data ID using the 'get_random_ml3' function.
    - Constructs the context with the paragraph data and data ID.
    - Renders the ML3 recording template with the constructed context.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response.
    """
    paragraph, data_id = get_random_ml3(request)
    context = {"val": paragraph, "recording": True, "data_id": data_id}
    return render(request, "AOP_PRO/ml3_recording.html", context)


def ml3_next(request):
    """
    Renders the ML3 start recording next page.

    - Retrieves the selected option and level from the session.
    - If the request method is POST, redirects to the 'start_recording_next_ml3' view.
    - If the request method is GET, renders the ML3 start recording next template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response.
    """
    selected_option = request.session.get('selected_option')
    selected_level = request.session.get('selected_level')
    if request.method == 'POST':
        return redirect('start_recording_next_ml3')
    return render(request, 'AOP_PRO/ml3_startrecording_next.html')


def get_random_ml3_sentence(request):
    """
    Retrieves a random ML3 sentence and its corresponding data ID.

    - Retrieves the selected option from the session.
    - If the selected option is 'EL' (English Language), fetches the ML3 sentence from the predefined data source.
    - Randomly selects a sentence.
    - Extracts the sentence data, data ID, and language information.
    - Stores the data ID in the session for future reference.
    - Constructs and returns a dictionary containing the sentence data, data ID, and language information.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        dict: A dictionary containing the ML3 sentence data, data ID, and language information.
    """
    selected_option = request.session.get('selected_option')
    if selected_option == 'EL':
        data = json_l4_data
        data1 = random.choice(data['Sentence'])
        data_id = data1['id']
        request.session['data_id'] = data_id
        languages = data1['language']
        return {
            'data': data1['data'],
            'data_id': data_id,
            'languages': languages,
        }
    else:
        data = json_l4_data
        data1 = random.choice(data['Sentence'])
        data_id = data1['id']
        request.session['data_id'] = data_id
        languages = data1['language']
        return {
            'data': data1['data'],
            'data_id': data_id,
            'languages': languages,
        }


def start_recording_next_ml3(request):
    """
    Renders the ML3 next recording page.

    - Retrieves a random paragraph and its data ID using the 'get_random_paragraph' function.
    - Constructs the context with the paragraph data and data ID.
    - Renders the ML3 next recording template with the constructed context.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response.
    """
    paragraph, data_id = get_random_paragraph(request)
    context = {"val": paragraph, "recording": True, "data_id": data_id}
    return render(request, "AOP_PRO/ml3_recording_next.html", context)


def ml3_answer_final(request):
    """
    Handles the submission of ML3 answer and displays the final result.

    - Retrieves the file path, file name, selected option, and data ID from the session.
    - Retrieves the ML3 paragraph data based on the data ID.
    - Sends a POST request to the transcript API to get the transcription and analysis.
    - Stores the API response in the session.
    - If the response is successful, extracts the relevant information from the response.
    - Formats the Words Correct Per Minute (WCPM) to have two decimal places.
    - Checks if the audio file exists and constructs the audio URL.
    - Renders the ML3 answer final template with the transcript, original text, analysis details, and audio URL.
    - If the response is not successful, renders the error page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response.
    """
    filepath = request.session.get('filepath')
    filename = request.session.get('filename')
    selected_option = request.session.get('selected_option')
    data_id = request.session.get('data_id')
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
    request.session['ml3_res'] = response.text
    if response.status_code == 200:
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
    """
    Handles the saving of the ML3 audio file.

    - Checks if the request method is POST and if the 'audio_blob' file is present.
    - Retrieves the data ID and val from the request parameters.
    - Generates the filename based on the data ID.
    - Creates the media folder if it doesn't exist.
    - Constructs the file path for saving the audio file.
    - Writes the audio file to the specified file path.
    - Stores the file path and file name in the session.
    - Renders the ML3 answer template with the file path.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response.
    """
    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        filename = f'{data_id}.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
            request.session['filepath'] = filepath
            request.session['filename'] = filename
            return render(request, 'AOP_PRO/ml3_answer.html', { 'filepath': filepath})


def ml3_answer(request):
    """
    Handles the submission of ML3 answer and displays the result.

    - Retrieves the file path, file name, selected option, and data ID from the session.
    - Retrieves the ML3 paragraph data based on the data ID.
    - Sends a POST request to the transcript API to get the transcription and analysis.
    - Stores the API response in the session.
    - If the response is successful, extracts the relevant information from the response.
    - Formats the Words Correct Per Minute (WCPM) to have two decimal places.
    - Checks if the audio file exists and constructs the audio URL.
    - Renders the ML3 answer template with the transcript, original text, analysis details, and audio URL.
    - If the response is not successful, renders the error page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response.
    """
    filepath = request.session.get('filepath')
    filename = request.session.get('filename')
    selected_option = request.session.get('selected_option')
    data_id = request.session.get('data_id')
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
    request.session['ml3_res'] = response.text

    if response.status_code == 200:
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
    """
    Handles the retake action for ML3.

    - Retrieves the selected option, media folder path, and data ID from the session.
    - Deletes all files in the media folder.
    - Retrieves the ML3 paragraph data based on the data ID.
    - Renders the ML3 retake template with the recording enabled and the paragraph data.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response.
    """
    selected_option = request.session.get('selected_option')
    media_folder = os.path.join(settings.MEDIA_ROOT)
    for file in os.listdir(media_folder):
        file_path = os.path.join(media_folder, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(e)

    data_id = request.session.get('data_id')
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
    """
    Handles the skip action for ML3.

    - Retrieves the selected option and data ID from the session.
    - Retrieves the ML3 paragraph data based on the data ID.
    - Splits the paragraph into words.
    - Generates the deletion details by joining the words with their indices.
    - Sets the substitution details as the first word and its index.
    - Constructs a mock ML3 response with the generated details.
    - Converts the response to JSON and stores it in the session.
    - Renders the ML3 answer template with the original text and the mock analysis details.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response.
    """
    selected_option = request.session.get('selected_option')
    data_id = request.session.get('data_id')
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
    sub_details_index = 0
    sub_details = f"{sub_details_index}-{my_list[sub_details_index]}"
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
    """
    Handles the skip next action for ML3.

    - Retrieves the selected option and data ID from the session.
    - Retrieves the ML3 paragraph data based on the data ID.
    - Splits the paragraph into words.
    - Generates the deletion details by joining the words with their indices.
    - Sets the substitution details as the first word and its index.
    - Constructs a mock ML3 response with the generated details.
    - Converts the response to JSON and stores it in the session.
    - Renders the ML3 answer final template with the original text and the mock analysis details.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response.
    """
    selected_option = request.session.get('selected_option')
    data_id = request.session.get('data_id')
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
    sub_details_index = 0
    sub_details = f"{sub_details_index}-{my_list[sub_details_index]}"
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
    """
    Handles the storage of ML3 data for the current question.

    - Retrieves the fluency adjustment value from the request.
    - Converts the adjustment value to an integer.
    - Sets the 'ans_next_level' session variable based on the adjustment value.
    - Retrieves various session variables related to ML3 data and analysis.
    - Constructs a data dictionary with the retrieved values.
    - Sends a POST request to the 'saveprogress' API with the data.
    - Redirects the user to the appropriate view based on the adjustment value.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response.
    """
    if request.method == 'POST':
        try:
            fluency_adjustment = request.POST.get('fluency_adjustment')
            number = int(fluency_adjustment)
            if fluency_adjustment == '0':
                request.session['ans_next_level'] = 'L4'
            else:
                request.session['ans_next_level'] = 'L4'

            enrollment_id = request.session.get('enrollment_id')
            status = request.session.get('status')
            filepath = request.session.get('filepath')
            ml3_res = request.session.get('ml3_res')
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
            data_id = request.session.get('data_id')
            data =json_l4_data
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

            if val:
                print("question",val)
            selected_option = request.session.get('selected_option')
            ans_next_level = request.session.get('ans_next_level')
            my_program = request.session.get('my_program')

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
            response_data = json.loads(response.text)
            if number == 0:
                return redirect('ml3_mcq_next')  # redirect to bl_mcq function
            else:
                return redirect('ml3_next')
        except TypeError:
            return HttpResponse("Invalid adjustment value")
    

def ml3_next_store(request):
    """
    Handles the storage of ML3 data for the next question.

    - Retrieves the fluency adjustment value from the request.
    - Converts the adjustment value to an integer.
    - Sets the 'ans_next_level' session variable based on the adjustment value.
    - Retrieves various session variables related to ML3 data and analysis.
    - Constructs a data dictionary with the retrieved values.
    - Sends a POST request to the 'saveprogress' API with the data.
    - Redirects the user to the appropriate view based on the adjustment value.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response.
    """
    if request.method == 'POST':
        try:
            fluency_adjustment = request.POST.get('fluency_adjustment')
            number = int(fluency_adjustment)
            
            if fluency_adjustment == '0':
                request.session['ans_next_level'] = 'L4'
            else:
                request.session['ans_next_level'] = 'L4'

            enrollment_id = request.session.get('enrollment_id')
            status = request.session.get('status')
            filepath = request.session.get('filepath')
            ml3_res = request.session.get('ml3_res')
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
            data_id = request.session.get('data_id')
            data = json_l4_data
            paragraph = None
            for d in data['Paragraph']:
                if d['id'] == data_id:
                    val = d['data']
                    break

            if val:
                print("question",val)
            selected_option = request.session.get('selected_option')
            ans_next_level = request.session.get('ans_next_level')
            my_program = request.session.get('my_program')

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
            response_data = json.loads(response.text)
            if number == 0:
                return redirect('ml3_mcq_next')  # redirect to bl_mcq function
            else:
                phone_number = request.session.get('phone_number')
                enrollment_id = request.session.get('enrollment_id')
            
                context = {
                    'mobile_number': phone_number,
                    'level' : "L3-sentence"
                }
                return render(request, "AOP_PRO/ans_page_aop.html", context=context)
        except TypeError:
            return HttpResponse("Invalid adjustment value")
    

def ml3_mcq_api(request):
    """
    API view for saving progress and rendering the answer page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response containing the rendered answer page.
    """
    selected_option = request.session.get('selected_option')
    selected_level = request.session.get('selected_level')

    if request.method == 'POST':
        selected_lan = request.POST.get('selected_language_input')
        status = request.session.get('status')
        selected_language = request.POST.get('selected_language')
        selected_div = request.POST.get('selected-div')
        data_id = request.session.get('data_id')
        id_value = request.session.get('id_value')
        ml3_res = request.session.get('ml3_res')
        transcript_dict = json.loads(ml3_res)
        no_mistakes = transcript_dict.get('no_mistakes')
        no_del = transcript_dict.get('no_del')
        del_details = transcript_dict.get('del_details')
        sub_details = transcript_dict.get('sub_details')
        text = transcript_dict.get('text')
        audio_url = transcript_dict.get('audio_url')
        process_time = transcript_dict.get('process_time')
        ans_next_level = request.session.get('ans_next_level')
        data = json_l4_data
        Sentence = None
        for d in data['Sentence']:
            if d['id'] == data_id:
                val = d['data']
                break
        if selected_language == 'hindi':
            request.session['lan'] = selected_language

        elif selected_language == 'marathi':
            request.session['lan'] = selected_language

        if selected_language == 'hindi':
            data = json_l4_data
            # Find the data with matching data_id
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
           
        
        lan = request.session.get('lan')
        my_program = request.session.get('my_program')

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

        url = 'https://parakh.pradigi.org/v1/saveprogress/'
        files = []
        payload = {'data': json.dumps(data)}
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        response_data = json.loads(response.text)
        phone_number = request.session.get('phone_number')
        enrollment_id = request.session.get('enrollment_id')
    
        context = {
            'mobile_number': phone_number,
            'level' : "L4-sentence"
        }
        return render(request, "AOP_PRO/ans_page_aop.html", context=context)


def ml3_ans(request):
    # Render the congratulatory page for ML3
    return render(request, "AOP_PRO/ml3_cong.html")
    

def ml3_final_mcq(request):
    # Get the context from the session
    context = request.session.get('ml3_context', {})
    
    if request.method == 'POST':
        # Get the selected div and language from the form submission
        selected_div = request.POST.get('selected-div')
        selected_divid = request.POST.get('selected-div_id')
        
        # Update the context with the selected div and language
        context['selected_divid'] = selected_divid
        context['selected_div'] = selected_div
        selected_language = request.POST.get('selected_language')
        context['selected_language'] = selected_language
        
        # Render the ML3 MCQ page with the updated context
        return render(request, "AOP_PRO/ml3_mcq.html", context)
    
    # Render the ML3 MCQ page with the context
    return render(request, "AOP_PRO/ml3_mcq.html", context)
    

def ml3_mcq(request):
    # Get the selected option and level from the session
    selected_option = request.session.get('selected_option')
    selected_level = request.session.get('selected_level')
    
    # Get random ML3 sentence data
    data = get_random_ml3_sentence(request)
    
    # Prepare the context for rendering the ML3 MCQ page
    context = {"val": data['data'], "recording": True, "data_id": data['data_id'], "languages": data['languages']}
    
    # Render the ML3 MCQ page with the context
    return render(request, "AOP_PRO/ml3_mcq.html", context)


def ml3_mcq_next(request):
    # Get random ML3 sentence data
    data = get_random_ml3_sentence(request)

    # Prepare the context for rendering the ML3 MCQ Next page
    context = {"val": data['data'], "recording": True, "data_id": data['data_id'], "languages": data['languages']}

    # Store the context in the session
    request.session['ml3_context'] = context
    
    if request.method == 'POST':
        # Redirect to the ML3 MCQ page
        return redirect('ml3')
    
    # Render the ML3 MCQ Next page with the context
    return render(request, "AOP_PRO/ml3_mcq_next.html", context)


#############################################################################################

def start_recording(request):
    # Get a random paragraph and its data ID
    paragraph, data_id = get_random_paragraph(request)
    
    # Prepare the context for rendering the recording page
    context = {"val": paragraph, "recording": True, "data_id": data_id}
    
    # Render the recording page with the context
    return render(request, "para_rec.html", context)


def paragraph(request):
    # Get the selected option from the session
    selected_option = request.session.get('selected_option')
    
    if request.method == 'POST':
        # Redirect to the start_recording view
        return redirect('start_recording')
    
    # Render the paragraph start page
    return render(request, 'para_start.html')


def get_random_paragraph(request):
    # Get the selected option from the session
    selected_option = request.session.get('selected_option')
    
    # Mapping of selected option to JSON files
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
        'BL': json_l1_data,
        'ML1': json_l2,
        'ML2': json_l3,
        'EL': json_l4
    }
    
    if selected_option in json_files:
        json_file = json_files[selected_option]
        
        # Get a random paragraph from the JSON file
        data1 = random.choice(json_file['Paragraph'])
        data_id = data1['id']
        
        # Store the data ID and data value in the session
        request.session['data_id'] = data_id
        request.session['data_value'] = data1['data']
        
        return data1['data'], data_id


@csrf_exempt
def save_file(request):
    if request.method == 'POST' and request.FILES.get('audio_blob'):
        # Get the data ID and value from the session
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        
        # Generate the filename and file path for saving the audio file
        filename = f'{data_id}.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            # Write the audio file from the request to disk
            audio_file.write(request.FILES['audio_blob'].read())
            
            # Store the filepath and filename in the session
            request.session['filepath'] = filepath
            request.session['filename'] = filename
            
            # Render the paragraph answer page with the filepath
            return render(request, 'para_ans.html', {'filepath': filepath})


def answer(request):
    # Retrieve necessary session data
    filepath = request.session.get('filepath')
    filename = request.session.get('filename')
    selected_option = request.session.get('selected_option')
    data_id = request.session.get('data_id')
    
    if selected_option is not None:
        # Get the JSON file based on the selected option
        json_file = json_files[selected_option]
        paragraph = None
        
        # Find the paragraph with the corresponding data ID
        for d in json_file['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break
    
    if val:
        print("the val", val)
    
    # Set the URL for the transcription API
    url = 'http://3.7.133.80:8000/gettranscript/'
    
    # Prepare the file for sending in the request
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    
    # Prepare the payload data for the request
    payload = {'language': selected_option, 'question': val}
    
    headers = {}
    
    # Send the POST request to the transcription API
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    
    if response.status_code == 200:
        # Store the original paragraph value in the session
        request.session['val'] = val
        
        # Retrieve the transcription and analysis data from the API response
        data_string = response.json().get('text')
        mistake = response.json().get('no_mistakes')
        fluency = response.json().get('wcpm')
        index = response.json().get('sub_details')
        deld = response.json().get('del_details')
        
        # Format wcpm to have only two decimal places
        wcpm_formatted = '{:.2f}'.format(float(fluency)) if fluency else None
        
        # Retrieve the filepath for the audio file
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
        
        # Render the answer page with the obtained data
        return render(request, 'para_ans.html', {'transcript': data_string, 'text': data_string, 'originaltext': val, 'sub_details': index, 'del_details': deld, 'audio_url': audio_url, 'no_mistakes': mistake, 'wcpm': wcpm_formatted})
    else:
        # Render the error page if the request to the transcription API fails
        return render(request, 'Error/pages-500.html')


def skip_answer(request):
    selected_option = request.session.get('selected_option')
    data_id = request.session.get('data_id')
    json_file = json_files[selected_option]
    
    if json_file is not None:
        data = json_file
        paragraph = None
        
        # Find the paragraph with the corresponding data ID
        for d in data['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break
    
    if val:
        print("the val", val)
    
    words = val.split()
    my_list = list(words)
    last_index = len(my_list)
    
    # Render the answer page with the skipped paragraph data
    return render(request, 'para_ans.html', {'originaltext': val, 'wcpm': None, 'no_mistakes': last_index})


def next_page(request):
    if request.method == 'POST':
        # Retrieve the total number of mistakes from the request
        total_mis = request.POST.get('total_mis')
        number = int(total_mis)
        
        media_folder = os.path.join(settings.MEDIA_ROOT)
        
        # Remove all files in the media folder
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
            # Redirect to the appropriate page based on the number of mistakes
            child_name = request.session.get('child_name')
            level = "Word"
            return render(request, 'answer_page_gen.html', {'child_name': child_name, 'level': level})
        else:
            return redirect("letter")


def next_page_para(request):
    if request.method == 'POST':
        # Retrieve the number of mistakes from the request
        word_mistakes = request.POST.get('no_mistakes')
        number = int(word_mistakes)
        
        media_folder = os.path.join(settings.MEDIA_ROOT)
        
        # Remove all files in the media folder
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
            # Redirect to the appropriate page based on the number of mistakes
            return redirect("story")
        else:
            return redirect("word")


def next_page_story(request):
    if request.method == 'POST':
        # Retrieve the number of mistakes from the request
        word_mistakes = request.POST.get('no_mistakes')
        number = int(word_mistakes)
        
        media_folder = os.path.join(settings.MEDIA_ROOT)
        
        # Remove all files in the media folder
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
            # Redirect to the appropriate page based on the number of mistakes
            child_name = request.session.get('child_name')
            level = "Story"
            return render(request, 'answer_page_gen.html', {'child_name': child_name, 'level': level})
        else:
            child_name = request.session.get('child_name')
            level = "Paragraph"
            return render(request, 'answer_page_gen.html', {'child_name': child_name, 'level': level})


def next_page_letter(request):
    if request.method == 'POST':
        # Retrieve the total number of mistakes from the request
        total_mis = request.POST.get('total_mis')
        number = int(total_mis)
        
        media_folder = os.path.join(settings.MEDIA_ROOT)
        
        # Remove all files in the media folder
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
            # Redirect to the appropriate page based on the number of mistakes
            child_name = request.session.get('child_name')
            level = "Letter"
            return render(request, 'answer_page_gen.html', {'child_name': child_name, 'level': level})
        else:
            child_name = request.session.get('child_name')
            level = "Beginner"
            return render(request, 'answer_page_gen.html', {'child_name': child_name, 'level': level})


def next_para(request):
    """
    View function for rendering the next paragraph recording page.

    The function waits for 2 seconds using the `time.sleep` function.
    It retrieves the selected option from the session variables and the media folder path.
    Then, it removes all files in the media folder.
    If the selected option is not None, it retrieves the JSON file corresponding to the selected option
    and finds the paragraph with the corresponding data ID.
    The paragraph text is then passed as a context variable to the template.
    The next paragraph recording page ('para_rec_next.html') is rendered with the provided context.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for rendering the next paragraph recording page.
    """
    t.sleep(2)
    selected_option = request.session.get('selected_option')
    media_folder = os.path.join(settings.MEDIA_ROOT)
    
    # Remove all files in the media folder
    for file in os.listdir(media_folder):
        file_path = os.path.join(media_folder, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(e)
    
    if selected_option is not None:
        data_id = request.session.get('data_id')
        json_file = json_files[selected_option]
        paragraph = None
        
        # Find the paragraph with the corresponding data ID
        for d in json_file['Paragraph']:
            if d['id'] == data_id:
                val = d['data']
                break
    
    if val:
        print("the val", val)
    
    # Render the next paragraph recording page
    return render(request, "para_rec_next.html", {"recording": True, "val": val})
   

#                   Story Recording
def story(request):
    """
    View function for rendering the story start page.

    If the request method is POST, it redirects to the story recording page.
    Otherwise, it renders the story start page ('story_start.html').

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for rendering the story start page or redirecting to the story recording page.
    """
    if request.method == 'POST':
        # Redirect to the story recording page
        return redirect('story_recording')
    # Render the story start page
    return render(request, 'story_start.html')


def get_random_story(request):
    """
    Function for retrieving a random story and its data_id.

    It retrieves the selected option from the session variables and retrieves the corresponding JSON file.
    It selects a random story from the JSON file and retrieves its data and data_id.
    The data_id and data_value are stored in session variables.
    
    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        tuple: A tuple containing the story data and data_id.
    """
    selected_option = request.session.get('selected_option')
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
    if selected_option in json_files:
        json_file = json_files[selected_option]
        data1 = random.choice(json_file['Story'])
        data_id = data1['id']
        request.session['data_id'] = data_id
        request.session['data_value'] = data1['data']
        return data1['data'], data_id


def story_recording(request):
    """
    View function for rendering the story recording page.

    The function calls the `get_random_story` function to retrieve a random story and its corresponding data_id.
    The story and data_id are then passed as context variables to the template.
    The story recording page ('story_rec.html') is rendered with the provided context.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for rendering the story recording page.
    """
    Story, data_id = get_random_story(request)
    context = {"val": Story, "recording": True, "data_id": data_id}
    # Render the story recording page
    return render(request, "story_rec.html", context)


@csrf_exempt
def save_story(request):
    """
    View function for saving the recording of a story and rendering the story answer page.

    If the request method is POST and there is a file in the request named 'audio_blob',
    the function retrieves the data_id and val from the request.
    It creates a filename using the data_id and saves the audio file to the media folder.
    The file path is stored in the session variable 'filepath'.
    The function renders the story answer page ('story_ans.html') and passes the audio URL in the context.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for rendering the story answer page with the audio URL.
    """
    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        filename = f'{data_id}.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
            request.session['filepath'] = filepath
            # Render the story answer page with the audio URL
            return render(request, 'story_ans.html', {'audio_url': filepath})

    
def story_answer(request):
    """
    Renders the story answer page with the transcription and analysis of the recorded story.

    Args:
        request: The HTTP request object.

    Returns:
        The rendered story answer page with the transcription and analysis data.

    """
    filepath = request.session.get('filepath')
    selected_option = request.session.get('selected_option')

    if selected_option is not None:
        data_id = request.session.get('data_id')
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

    if response.status_code == 200: 
        filepath = request.session.get('filepath')
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
    """
    Renders the story answer page without recording, displaying the original story and analysis data.

    Args:
        request: The HTTP request object.

    Returns:
        The rendered story answer page without recording, displaying the original story and analysis data.

    """
    selected_option = request.session.get('selected_option')
    data_id = request.session.get('data_id')
    json_file = json_files[selected_option]
    
    if json_file is not None:
        data = json_file
        
        # Find the story with the corresponding data ID
        for d in data['Story']:
            if d['id'] == data_id:
                val = d['data']
                break

    if val:
        print("the val",val)
    words = val.split()
    my_list = list(words)
    last_index = len(my_list) 
    return render(request, 'story_ans.html', {'originaltext': val, 'wcpm': None, 'no_mistakes': last_index})


def next_story(request):
    """
    Renders the next story recording page, clearing previous recordings and preparing for the next story.

    Args:
        request: The HTTP request object.

    Returns:
        The rendered next story recording page.

    """
    t.sleep(2)
    selected_option = request.session.get('selected_option')
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
    """
    Handles the word exercise, including recording and storing audio files.

    Args:
        request: The HTTP request object.

    Returns:
        If the request method is POST, redirects to the 'word_recording_next' view.
        If the request method is GET, renders the 'word_start.html' template.

    """
    d_audio_files = request.session.setdefault('d_audio_files', [])
    d_audio_files_name = request.session.setdefault('d_audio_files_name', [])
    qword = request.session.setdefault('qword', [])
    skip_val = request.session.setdefault('skip_val', [])
    d_dataid = request.session.setdefault('d_dataid', [])
    audio_file = request.session.setdefault('audio_file', [])
    file = request.session.setdefault('file', [])
    word_ids = request.session.setdefault('word_ids', [])
    dc_res = request.session.setdefault('dc_res', [])

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
        if len(dc_res) == 5:
            dc_res.clear()
            d_dataid.clear()
            skip_val.clear()
            qword.clear()
            word_ids.clear()
            d_audio_files.clear()
            d_audio_files_name.clear()
            dc_res.clear()
            d_dataid.clear()
            audio_file.clear()  # clear the audio_file list
            file.clear()
            if len(d_audio_files)>5:
                d_audio_files.clear()
                d_audio_files_name.clear() 
        elif len(dc_res)==4:
            dc_res.clear()
            d_dataid.clear()
            qword.clear()
            word_ids.clear()
            d_audio_files.clear()
            d_audio_files_name.clear()
            dc_res.clear()
            d_dataid.clear()
            audio_file.clear()  # clear the audio_file list
            file.clear()
            if len(d_audio_files)>5:
                d_audio_files.clear()
                d_audio_files_name.clear() 
        elif len(dc_res)==3:
            dc_res.clear()
            d_dataid.clear()
            qword.clear()
            word_ids.clear()
            d_audio_files.clear()
            d_audio_files_name.clear()
            dc_res.clear()
            d_dataid.clear()
            audio_file.clear()  # clear the audio_file list
            file.clear()
            if len(d_audio_files)>5:
                d_audio_files.clear()
                d_audio_files_name.clear() 
        elif len(dc_res)==2:
            dc_res.clear()
            d_dataid.clear()
            qword.clear()
            word_ids.clear()
            d_audio_files.clear()
            d_audio_files_name.clear()
            dc_res.clear()
            d_dataid.clear()
            audio_file.clear()  # clear the audio_file list
            file.clear()
            if len(d_audio_files)>5:
                d_audio_files.clear()
                d_audio_files_name.clear() 
        elif len(dc_res)==1:
            dc_res.clear()
            d_dataid.clear()
            qword.clear()
            word_ids.clear()
            d_audio_files.clear()
            d_audio_files_name.clear()
            dc_res.clear()
            d_dataid.clear()
            audio_file.clear()  # clear the audio_file list
            file.clear()
            if len(d_audio_files)>5:
                d_audio_files.clear()
                d_audio_files_name.clear() 
        elif len(dc_res) ==0:
            dc_res.clear()
            d_dataid.clear()
            qword.clear()
            word_ids.clear()
            d_audio_files.clear()
            d_audio_files_name.clear()
            dc_res.clear()
            d_dataid.clear()
            audio_file.clear()  # clear the audio_file list
            file.clear()
            if len(d_audio_files)>5:
                d_audio_files.clear()
                d_audio_files_name.clear() 
        return redirect('word_recording_next')
    return render(request, 'word_start.html')


def get_random_word(request):
    """
    Retrieves a random word from the JSON data based on the selected language.

    Args:
        request: The HTTP request object.

    Returns:
        A tuple containing the randomly selected word and its corresponding data ID.

    """
    word_ids = request.session.setdefault('word_ids', [])
    d_dataid = request.session.setdefault('d_dataid', [])
    selected_option = request.session.get('selected_option')
    json_file = json_files[selected_option]

    if json_file is not None:
        data = json_file  # Assuming json_hin contains the actual JSON data for Hindi
        data1 = random.choice(data['Word'])
        data_id = data1['id']
        while data_id in word_ids:
            data1 = random.choice(data['Word'])
            data_id = data1['id']
        word_ids.append(data_id)
        request.session['word_ids'] = word_ids
        request.session['data_id'] = data_id
        if len(word_ids) == 5:
            d_dataid = word_ids.copy()
            request.session['d_dataid'] = d_dataid
            word_ids.clear()
        return data1['data'], data_id


def word_recording(request):
    """
    Handles the word recording process.

    Args:
        request: The HTTP request object.

    Returns:
        Renders the 'word_rec.html' template with the randomly selected word and data ID.

    """
    d_dataid = request.session.setdefault('d_dataid', [])
    dc_res = request.session.setdefault('dc_res', [])
    if len(dc_res) == 5:
        dc_res.clear()
        d_dataid.clear()

    Word, data_id = get_random_word(request)
    context = {"val": Word, "recording": True, "data_id": data_id}
    request.session['submit_id'] = context
    return render(request, "word_rec.html", context)


def word_recording_next(request):
    """
    Handles the next word recording process.

    Args:
        request: The HTTP request object.

    Returns:
        Renders the 'word_rec_next.html' template with the randomly selected word and data ID.

    """
    word_ids = request.session.setdefault('word_ids', [])
    d_dataid = request.session.setdefault('d_dataid', [])
    dc_res = request.session.setdefault('dc_res', [])
    qword = request.session.setdefault('qword', [])

    if len(qword)==5:
        qword.clear()
        dc_res.clear()

    if len(dc_res) == 4:
        dc_res.clear()
        d_dataid.clear()
   
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
    """
    Handles the skipping of a word during the recording process.

    Args:
        request: The HTTP request object.

    Returns:
        - If the word recording is incomplete (less than 5 recordings), redirects to 'word_recording' or 'word_recording_next' view.
        - If the word recording is complete (5 recordings), redirects to 'wans_page' view.

    """
    if request.method == 'POST':
        val = request.POST.get('val')
        skip_val = request.session.setdefault('skip_val', [])
        d_audio_files = request.session.get('d_audio_files', [])
        d_audio_files_name = request.session.get('d_audio_files_name', [])
        word_ids = request.session.get('word_ids', [])
        qword = request.session.setdefault('qword', [])

        missing_indices = [i for i, id in enumerate(word_ids) if id not in d_audio_files_name]

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

        selected_option = request.session.get('selected_option')
        if selected_option in json_files:
            json_file = json_files[selected_option]
            request.session['json_file'] = json_file
            data_id = request.session.get('data_id')
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

        if len(d_audio_files) == 5:
            d_copy_audio_files = d_audio_files.copy()
        if len(d_audio_files_name) == 5:
            copy_word_name = d_audio_files_name.copy()
        
        request.session['copy_word_name'] = copy_word_name

        if val:
            qword = request.session.get("qword")
            qword.append(val)
            request.session["qword"] = qword
            dc_res = request.session.setdefault('dc_res', [])
            if request.session.get("dc_res", None) is None:
                dc_res = []
            else:
                dc_res = request.session.get("dc_res")
            request.session["dc_res"] = dc_res
            dc_res.append(
                '{"no_mistakes": 1, "no_del": 0, "del_details": "", "no_sub": 1, "sub_details": "0-\\u092a\\u0948\\u0938\\u093e:", "status": "success", "wcpm": 0.0, "text": "", "audio_url": "", "process_time": 0.47053098678588867}')
            if len(dc_res) == 5:
                request.session['dc_rec'] = dc_res
                context = {'l_res': dc_res}
                url = reverse('wans_page')
                return redirect(url, context)
            if len(d_audio_files) == 4:
                return redirect('word_recording')
        return redirect('word_recording_next')


def submit_word_skip(request):
    """
    Handles the submission of skipped word during the recording process.

    Args:
        request: The HTTP request object.

    Returns:
        - If the word recording is incomplete (less than 5 recordings), redirects to 'word_recording' or 'word_recording_next' view.
        - If the word recording is complete (5 recordings), redirects to 'wans_page' view.

    """
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
    """
    Retrieves the word from the selected JSON file and sends a POST request to get the word's transcription.

    Args:
        request: The HTTP request object.

    Returns:
        - If the transcription retrieval is successful and there are 5 recorded words, redirects to 'wans_page' view.
        - If the transcription retrieval is successful and there are less than 5 recorded words, redirects to 'word_recording' or 'word_recording_next' view.
        - If the transcription retrieval fails, renders an error page.

    """
    filepath = request.session.get('filepath')
    selected_option = request.session.get('selected_option')

    if selected_option in json_files:
        json_file_path = json_files[selected_option]
        data_id = request.session.get('data_id')
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
    """
    Saves the recorded word audio file and updates the session variables.

    Args:
        request: The HTTP request object.

    Returns:
        Renders the 'word_rec.html' template with the audio URL.

    """
    d_audio_files = request.session.setdefault('d_audio_files', [])
    d_audio_files_name = request.session.setdefault('d_audio_files_name', [])
    if request.method == 'POST' and request.FILES.get('audio_blob'):
        if len(d_audio_files)>5:
            d_audio_files.clear()
            d_audio_files_name.clear()  
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        filename = f'{data_id}.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
        d_audio_files.append(filepath)
        d_audio_files_name.append(filename)
        request.session['filepath'] = filepath
        return render(request, 'word_rec.html', { 'audio_url': filepath})


def wans_page(request):
    """
    Renders the word answer page with audio files and related data.

    Retrieves audio files, audio URLs, and other data from session variables.
    Calculates total mistakes and words per minute.
    Renders the 'word_answer.html' template with the provided context.
    """
    d_copy_audio_files = request.session.get('d_copy_audio_files', [])
    d_audio_files = request.session.get('d_audio_files', [])
    d_audio_files_name = request.session.setdefault('d_audio_files_name', [])
    copy_word_name = request.session.setdefault('copy_word_name', [])
    skip_val = request.session.setdefault('skip_val', [])

    if len(d_audio_files)==5:
        d_copy_audio_files= d_audio_files.copy()
    if len(d_audio_files_name)==5:
        copy_word_name= d_audio_files_name.copy()
    if len(d_audio_files)==4:
        d_copy_audio_files= d_audio_files.copy()
    if len(d_audio_files_name)==4:
        copy_word_name= d_audio_files_name.copy()
    
    request.session['copy_word_name'] = copy_word_name
    audio_urls = []
    if d_copy_audio_files:
        for filepath in d_copy_audio_files:
            if os.path.exists(filepath):
                filename = os.path.basename(filepath)
                audio_url = request.build_absolute_uri(settings.MEDIA_URL + filename)
                audio_urls.append(audio_url)
            else:
                audio_urls.append('')  # Add a blank entry if filepath doesn't exist
        request.session['d_copy_audio_files'] = d_copy_audio_files
    
    text = []
    mis=[]
    wcpm=[]
    dc_res=[]
    dc_res = request.session.setdefault('dc_res', [])
    qword = request.session.setdefault('qword', [])

    for item in dc_res:
        mis.append(eval(item)['no_mistakes'])
        wcpm.append(eval(item)['wcpm'])
    total_wcpm = sum(wcpm) 
    total_mis = sum(mis)
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
    """
    Handles the next word recording page.

    Performs actions based on the user's input.
    Updates session variables and redirects accordingly.
    """
    t.sleep(2)
    d_dataid = request.session.setdefault('d_dataid', [])
    copy_word_name = request.session.setdefault('copy_word_name', [])
    if request.method == "POST":
        copy_word_name = request.session.get('copy_word_name')
        copy_word_name = request.session.setdefault('copy_word_name', [])
        d_dataid = request.session.get('d_dataid', [])
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
            if selected_option is not None:
                print("d_dataid0",d_dataid[0])
                request.session['d_dataid[0]'] = d_dataid[0]
                request.session['audio_recorded'] = True
                json_file_path = json_files[selected_option]
                data_id = request.session.get('data_id')
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
                request.session['d_dataid[1]'] = d_dataid[1]
                request.session['audio_recorded'] = True
                json_file_path = json_files[selected_option]
                data_id = request.session.get('data_id')
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
                request.session['d_dataid[2]'] = d_dataid[2]
                request.session['audio_recorded'] = True
                json_file_path = json_files[selected_option]
                data_id = request.session.get('data_id')
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
                request.session['d_dataid[3]'] = d_dataid[3]
                request.session['audio_recorded'] = True
                json_file_path = json_files[selected_option]
                data_id = request.session.get('data_id')
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
                request.session['d_dataid[4]'] = d_dataid[4]
                request.session['audio_recorded'] = True
                json_file_path = json_files[selected_option]
                data_id = request.session.get('data_id')
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
    """
    Handles the retake word recording page.

    Retrieves session variables and performs actions based on the user's input.
    Saves the recorded audio file and updates session variables accordingly.
    Renders the 'word_answer.html' template with the updated context.
    """
    d_audio_files = request.session.setdefault('d_audio_files', [])
    d_copy_audio_files = request.session.get('d_copy_audio_files', [])
    d_audio_files_name = request.session.setdefault('d_audio_files_name', [])
    d_dataid = request.session.setdefault('d_dataid', [])
    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        request.session['d_dataid[0]'] = d_dataid[0]
        filename = d_dataid[0]+'.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)

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
        request.session['filepath'] = filepath
        return render(request, 'word_answer.html', { 'audio_url': filepath})
    
def save_word1(request):
    """
    Handles the saving of the word recording and performing transcription.

    Retrieves session variables and performs actions based on the user's input.
    Sends the audio file and associated data for transcription.
    Updates session variables with the transcription results.
    Redirects to the word answer page or renders an error page accordingly.
    """
    d_dataid = request.session.setdefault('d_dataid', [])
    filepath = request.session.get('filepath')
    selected_option = request.session.get('selected_option')
    request.session['d_dataid[0]'] = d_dataid[0]
    json_file_path = json_files.get(selected_option)
    data_id = request.session.get('data_id')
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
            request.session["dc_res"] = dc_res
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
    """
    Handles the second retake word recording page.

    Retrieves session variables and performs actions based on the user's input.
    Saves the recorded audio file and updates session variables accordingly.
    Renders the 'word_answer.html' template with the updated context.
    """
    d_audio_files = request.session.setdefault('d_audio_files', [])
    d_copy_audio_files = request.session.get('d_copy_audio_files', [])
    d_audio_files_name = request.session.setdefault('d_audio_files_name', [])
    d_dataid = request.session.setdefault('d_dataid', [])
    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
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
        request.session['filepath'] = filepath
        return render(request, 'word_answer.html', { 'audio_url': filepath})
    

def save_word2(request):
    """
    Handles the saving of the second word recording and performing transcription.

    Retrieves session variables and performs actions based on the user's input.
    Sends the audio file and associated data for transcription.
    Updates session variables with the transcription results.
    Redirects to the word answer page or renders an error page accordingly.
    """
    d_dataid = request.session.setdefault('d_dataid', [])
    filepath = request.session.get('filepath')
    selected_option = request.session.get('selected_option')
    request.session['d_dataid[1]'] = d_dataid[1]
    json_file_path = json_files.get(selected_option)
    data_id = request.session.get('data_id')
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
            request.session["dc_res"] = dc_res
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
    """
    Handles the third retake word recording page.

    Retrieves session variables and performs actions based on the user's input.
    Saves the recorded audio file and updates session variables accordingly.
    Renders the 'word_answer.html' template with the updated context.
    """
    d_audio_files = request.session.setdefault('d_audio_files', [])
    d_copy_audio_files = request.session.get('d_copy_audio_files', [])
    d_audio_files_name = request.session.setdefault('d_audio_files_name', [])
    d_dataid = request.session.setdefault('d_dataid', [])
    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
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
        request.session['filepath'] = filepath
        return render(request, 'word_answer.html', { 'audio_url': filepath})


def save_word3(request):
    """
    Handles the saving of the third word recording and performing transcription.

    Retrieves session variables and performs actions based on the user's input.
    Sends the audio file and associated data for transcription.
    Updates session variables with the transcription results.
    Redirects to the word answer page or renders an error page accordingly.
    """
    d_dataid = request.session.setdefault('d_dataid', [])
    filepath = request.session.get('filepath')
    selected_option = request.session.get('selected_option')
    request.session['d_dataid[2]'] = d_dataid[2]
    json_file_path = json_files.get(selected_option)
    data_id = request.session.get('data_id')
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
            request.session["dc_res"] = dc_res
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
    """
    Handles the fourth retake word recording page.

    Retrieves session variables and performs actions based on the user's input.
    Saves the recorded audio file and updates session variables accordingly.
    Renders the 'word_answer.html' template with the updated context.
    """
    d_audio_files = request.session.setdefault('d_audio_files', [])
    d_copy_audio_files = request.session.get('d_copy_audio_files', [])
    d_audio_files_name = request.session.setdefault('d_audio_files_name', [])
    d_dataid = request.session.setdefault('d_dataid', [])

    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
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
        request.session['filepath'] = filepath
        return render(request, 'word_answer.html', { 'audio_url': filepath})
    

def save_word4(request):
    """
    Handles the saving of the fourth word recording and performing transcription.

    Retrieves session variables and performs actions based on the user's input.
    Sends the audio file and associated data for transcription.
    Updates session variables with the transcription results.
    Redirects to the word answer page or renders an error page accordingly.
    """
    d_dataid = request.session.setdefault('d_dataid', [])
    filepath = request.session.get('filepath')
    selected_option = request.session.get('selected_option')
    request.session['d_dataid[3]'] = d_dataid[3]
    json_file_path = json_files.get(selected_option)
    data_id = request.session.get('data_id')
    
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

            request.session["dc_res"] = dc_res
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
    """
    Handles the fifth retake word recording page.

    Retrieves session variables and performs actions based on the user's input.
    Saves the recorded audio file and updates session variables accordingly.
    Renders the 'word_answer.html' template with the updated context.
    """
    d_audio_files = request.session.setdefault('d_audio_files', [])
    d_copy_audio_files = request.session.get('d_copy_audio_files', [])
    d_audio_files_name = request.session.setdefault('d_audio_files_name', [])
    d_dataid = request.session.setdefault('d_dataid', [])

    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
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
        request.session['filepath'] = filepath
        return render(request, 'word_answer.html', { 'audio_url': filepath})
    

def save_word5(request):
    """
    Handles the saving of the fifth word recording and performing transcription.

    Retrieves session variables and performs actions based on the user's input.
    Sends the audio file and associated data for transcription.
    Updates session variables with the transcription results.
    Redirects to the word answer page or renders an error page accordingly.
    """
    d_dataid = request.session.setdefault('d_dataid', [])
    filepath = request.session.get('filepath')
    selected_option = request.session.get('selected_option')
    request.session['d_dataid[4]'] = d_dataid[4]
    json_file_path = json_files[selected_option]
    data_id = request.session.get('data_id')
    
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

            request.session["dc_res"] = dc_res
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
    """
    View function for handling the letter recording process.

    The function manages the session data related to letter recording,
    clears certain session variables, and redirects to the appropriate
    view based on the current state of recording.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    """
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
        if len(lc_res) == 5:
            lc_res.clear()
            l_dataid.clear()
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
    """
    View function for retrieving a random letter for recording.

    The function retrieves a random letter from the JSON data based on
    the selected language option. It ensures that the letter has not been
    previously recorded by checking against the session data. Once a unique
    letter is found, it updates the session data and returns the letter data
    and its ID.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        tuple: A tuple containing the letter data and its ID.

    """
    data_ids = request.session.setdefault('data_ids', [])
    selected_option = request.session.get('selected_option')
    json_file = json_files[selected_option]
    if json_file is not None:
        data = json_file 
        data1 = random.choice(data['Letter'])
        data_id = data1['id']
        
        while data_id in data_ids:
            data1 = random.choice(data['Letter'])
            data_id = data1['id']
        
        data_ids.append(data_id)
        request.session['data_id'] = data_id
        if len(data_ids) ==5:
            l_dataid = data_ids.copy()
            request.session['l_dataid'] = l_dataid
            data_ids.clear()
        return data1['data'], data_id
    

def letter_recording(request):
    """
    View function for recording a letter.

    The function retrieves a random letter using the `get_random_letter` function.
    It initializes the necessary session data and renders the recording template
    with the letter data and recording flag.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response containing the rendered template.

    """
    l_dataid = request.session.setdefault('l_dataid', [])
    lc_res = request.session.setdefault('lc_res', [])

    if len(lc_res) == 5:
        lc_res.clear()
        l_dataid.clear()
   
    Letter, data_id = get_random_letter(request)
    context = {"val": Letter, "recording": True, "data_id": data_id}
    request.session['submit_id_letter'] = context
    return render(request, "letter_rec.html", context)


def letter_recording_next(request):
    """
    View function for recording the next letter.

    The function retrieves a random letter using the `get_random_letter` function.
    It initializes the necessary session data and renders the recording template
    for the next letter with the letter data and recording flag.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response containing the rendered template.

    """
    l_dataid = request.session.setdefault('l_dataid', [])
    lc_res = request.session.setdefault('lc_res', [])
    qletter = request.session.setdefault('qletter', [])
    if len(lc_res) == 5:
        lc_res.clear()
        l_dataid.clear()
        qletter.clear()
                                                                                                    
    Letter, data_id = get_random_letter(request)
    context = {"val": Letter, "recording": True, "data_id": data_id}
    return render(request, "letter_rec_next.html", context)


def letter_skip(request):
    """
    View function for skipping the current letter and proceeding to the next.

    The function updates the necessary session variables to reflect the skipped letter.
    It retrieves the selected option and corresponding JSON file from the session.
    The function updates the session variables with the skipped letter information,
    such as audio files, names, and skipped values.
    If the selected option is 'English', it retrieves the data from the 'json_eng' variable.
    The function then appends the skipped letter value to the 'qletter' session variable.
    If the 'lc_res' session variable is not set, it initializes it as an empty list.
    It appends a dummy response JSON to the 'lc_res' list to simulate successful recording.
    If the 'lc_res' list has reached a length of 5, it sets the 'dc_rec' session variable,
    prepares the context, and redirects to the 'lans_page' view.
    Finally, if the length of 'l_audio_files' is 4, it redirects to the 'letter_recording' view.
    Otherwise, it redirects to the 'letter_recording_next' view.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for redirecting to the appropriate view.

    """
    skip_val_letter = request.session.setdefault('skip_val_letter', [])
    l_audio_files = request.session.get('l_audio_files', [])
    l_audio_files_name = request.session.get('l_audio_files_name', [])
    data_ids = request.session.get('data_ids', [])
    qletter = request.session.setdefault('qletter', [])
    data_ids = request.session.get('data_ids', [])
    l_audio_files_name = request.session.get('l_audio_files_name', [])
    missing_indices = [i for i, id in enumerate(data_ids) if id not in l_audio_files_name]

    for data_id in data_ids:
        audio_file = data_id + '.wav'
        if audio_file not in l_audio_files_name:
            l_audio_files_name.append(audio_file)
    # update the session variable with the new list
    for data_id in data_ids:
        wav_file = os.path.join(base_path, f"{data_id}.wav")

        if wav_file not in l_audio_files:
            l_audio_files.append(wav_file)
            skip_val_letter.append(wav_file)

    request.session['l_audio_files'] = l_audio_files
    request.session['skip_val_letter'] = skip_val_letter
    request.session['l_audio_files_name'] = l_audio_files_name
    selected_option = request.session.get('selected_option')
    data_id = request.session.get('data_id')

    if selected_option is not None:
        json_file = json_files[selected_option]
        request.session['json_file'] = json_file
        data_id = request.session.get('data_id')
        data = json_file
        Letter = None
        for d in data['Letter']:
            if d['id'] == data_id:
                val = d['data']
                break
    
    if selected_option == 'English':
        data_id = request.session.get('data_id')
        data = json_eng
        Letter = None
        for d in data['Letter']:
            if d['id'] == data_id:
                val = d['data']
                break
   
    if val:
        qletter = request.session.get("qletter")
        qletter.append(val)
        request.session["qletter"] = qletter
        lc_res = request.session.setdefault('lc_res', [])
        if request.session.get("lc_res",None) is None:
            lc_res = []
        else:
            lc_res = request.session.get("lc_res")
            request.session["lc_res"] = lc_res
            lc_res.append('{"no_mistakes": 1, "no_del": 0, "del_details": "", "no_sub": 1, "sub_details": "0-\\u092a\\u0948\\u0938\\u093e:", "status": "success", "wcpm": 0.0, "text": "", "audio_url": "", "process_time": 0.47053098678588867}')
            if len(lc_res)==5:
                request.session['dc_rec'] = lc_res
                context = {'l_res': lc_res}
                url = reverse('lans_page')
                return redirect(url,context)
        if len(l_audio_files) == 4:
            return redirect('letter_recording')
    return redirect('letter_recording_next')


def submit_letter_skip(request):
    """
    View function for submitting the skipped letter.

    The function updates the necessary session variables to reflect the skipped letter.
    It retrieves the data ID and audio files from the session, and appends the skipped
    audio file to the appropriate session variables.
    It retrieves the selected option, JSON file, and data ID from the session.
    If the selected option is not None, it retrieves the data value from the JSON file.
    The function then appends the skipped letter value to the 'qletter' session variable.
    If the 'lc_res' session variable is not set, it initializes it as an empty list.
    It appends a dummy response JSON to the 'lc_res' list to simulate successful recording.
    If the 'lc_res' list has reached a length of 5, it sets the 'dc_rec' session variable,
    prepares the context, and redirects to the 'lans_page' view.
    Finally, if the length of 'l_audio_files' is 4, it redirects to the 'letter_recording' view.
    Otherwise, it redirects to the 'letter_recording_next' view.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for redirecting to the appropriate view.

    """
    skip_val_letter = request.session.setdefault('skip_val_letter', [])
    submit_id_letter = request.session.get('submit_id_letter')
    data_id = submit_id_letter.get('data_id')
    l_audio_files = request.session.get('l_audio_files', [])
    l_audio_files_name = request.session.get('l_audio_files_name', [])
    data_ids = request.session.get('data_ids', [])
    qletter = request.session.setdefault('qletter', [])
    data_ids = request.session.get('data_ids', [])
    l_audio_files_name = request.session.get('l_audio_files_name', [])
    missing_indices = [i for i, id in enumerate(data_ids) if id not in l_audio_files_name]
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
    request.session['l_audio_files_name'] = l_audio_files_name
    selected_option = request.session.get('selected_option')
    data_id = request.session.get('data_id')
    json_file = json_files[selected_option]

    if selected_option is not None:
        data = json_file
        Letter = None
        for d in data['Letter']:
            if d['id'] == data_id:
                val = d['data']
                break

    if val:
        qletter = request.session.get("qletter")
        qletter.append(val)
        request.session["qletter"] = qletter
        lc_res = request.session.setdefault('lc_res', [])
        if request.session.get("lc_res",None) is None:
            lc_res = []
        else:
            lc_res = request.session.get("lc_res")
            request.session["lc_res"] = lc_res
            lc_res.append('{"no_mistakes": 1, "no_del": 0, "del_details": "", "no_sub": 1, "sub_details": "0-\\u092a\\u0948\\u0938\\u093e:", "status": "success", "wcpm": 0.0, "text": "", "audio_url": "", "process_time": 0.47053098678588867}')

            if len(lc_res)==5:
                request.session['dc_rec'] = lc_res
                context = {'l_res': lc_res}
                url = reverse('lans_page')
                return redirect(url,context)
        if len(l_audio_files) == 4:
            return redirect('letter_recording')
    return redirect('letter_recording_next')


@csrf_exempt
def save_letter(request):
    """
    View function for saving the recorded letter audio.

    The function handles the POST request containing the recorded audio file.
    It retrieves the data ID and value from the session.
    It saves the audio file to the media folder using the data ID as the filename.
    The file path is then appended to the 'l_audio_files' and 'l_audio_files_name'
    session variables, and the file path is stored in the session.
    Finally, it renders the 'letter_rec.html' template with the audio URL.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for rendering the 'letter_rec.html' template.

    """
    l_audio_files = request.session.setdefault('l_audio_files', [])
    l_audio_files_name = request.session.setdefault('l_audio_files_name', [])

    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
        filename = f'{data_id}.wav'
        media_folder = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_folder, exist_ok=True)
        filepath = os.path.join(media_folder, filename)
        with open(os.path.join(media_folder, filename), 'wb') as audio_file:
            audio_file.write(request.FILES['audio_blob'].read())
        l_audio_files.append(filepath)
        l_audio_files_name.append(filename)
        request.session['filepath'] = filepath
        return render(request, 'letter_rec.html', { 'audio_url': filepath})

    
def letter_answer(request):
    """
    View function for handling the letter answer and making a request for transcription.

    The function retrieves the necessary session variables, such as 'l_audio_files',
    'filepath', and 'selected_option'.
    If the selected option exists in the 'json_files' dictionary, it retrieves the
    corresponding JSON file and retrieves the letter value for the current data ID.
    The letter value is then appended to the 'qletter' session variable.
    A request is made to the transcription API with the audio file and question payload.
    If the response status code is 200, the response text is appended to the 'lc_res'
    session variable. If the length of 'lc_res' reaches 5, the 'lc_rec' session variable
    is set, and the context is prepared for redirection to the 'lans_page' view.
    If the length of 'l_audio_files' is 4, it redirects to the 'letter_recording' view.
    Otherwise, it redirects to the 'letter_recording_next' view.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for redirecting to the appropriate view or rendering the error template.

    """
    l_audio_files = request.session.setdefault('l_audio_files', [])
    filepath = request.session.get('filepath')
    selected_option = request.session.get('selected_option')

    if selected_option in json_files:
        json_file_path = json_files[selected_option]
        data_id = request.session.get('data_id')
        data = json_file_path
        letter = next((d['data'] for d in data['Letter'] if d['id'] == request.session.get('data_id')), None)

    qletter = request.session.setdefault('qletter', [])
    if letter:
        qletter.append(letter)
        request.session['qletter'] = qletter

    url = 'http://3.7.133.80:8000/gettranscript/'
    files = [('audio', (filepath, open(filepath, 'rb'), 'audio/wav'))]
    payload = {'language': selected_option ,'question':letter}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    if response.status_code == 200:

        lc_res = request.session.setdefault('lc_res', [])
        if request.session.get("lc_res",None) is None:
            lc_res = []
        else:
            lc_res = request.session.get("lc_res")
            lc_res.append(response.text)

            request.session["lc_res"] = lc_res
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
    """
    View function for rendering the LANs (Letter and Number Sequencing) page.

    The function retrieves session variables such as 'l_copy_audio_files',
    'l_audio_files_name', 'l_audio_files', and 'copy_letter_name'.
    If the length of 'l_audio_files' is 5, it copies the contents of 'l_audio_files'
    to 'l_copy_audio_files'.
    If the length of 'l_audio_files_name' is 5, it copies the contents of
    'l_audio_files_name' to 'copy_letter_name'.
    If the length of 'l_audio_files' is 4, it copies the contents of 'l_audio_files'
    to 'l_copy_audio_files'.
    If the length of 'l_audio_files_name' is 4, it copies the contents of
    'l_audio_files_name' to 'copy_letter_name'.
    The 'copy_letter_name' session variable is updated accordingly.
    The audio URLs are generated for each file in 'l_copy_audio_files' if the file exists,
    and the URLs are added to the 'audio_urls' list.
    The session variables 'l_copy_audio_files', 'lc_res', and 'qletter' are retrieved.
    The 'text', 'mis', and 'wcpm' lists are populated from the 'lc_res' session variable.
    The total word correct per minute (WCPM) and total mistakes are calculated.
    The context is prepared with all the necessary variables for rendering the template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for rendering the 'letter_answer.html' template.

    """
    l_copy_audio_files = request.session.get('l_copy_audio_files', [])
    l_audio_files_name = request.session.setdefault('l_audio_files_name', [])
    l_audio_files = request.session.get('l_audio_files', [])
    copy_letter_name = request.session.setdefault('copy_letter_name', [])
    if len(l_audio_files)==5:
        l_copy_audio_files= l_audio_files.copy()
    if len(l_audio_files_name)==5:
        copy_letter_name= l_audio_files_name.copy()
    if len(l_audio_files)==4:
        l_copy_audio_files= l_audio_files.copy()
    if len(l_audio_files_name)==4:
        copy_letter_name= l_audio_files_name.copy()
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
    if len(l_audio_files)==5:
        l_audio_files.clear()
        l_audio_files_name.clear()
    return render(request, 'letter_answer.html', context)


def next_letter(request):
    """
    View function for handling the submission of letter recording choices.

    The function retrieves session variables such as 'l_dataid' and 'copy_letter_name'.
    If the form data contains "record" in the POST request, it retrieves the selected option,
    retrieves the corresponding letter data, and renders the 'retake_letter1.html' template
    with the 'recording' flag set to True.
    Similar logic is followed for "record2", "record3", "record4", and "record5" options.
    The template context includes the 'val' variable containing the letter data.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for rendering the respective 'retake_letter' template.

    """
    t.sleep(2)    
    l_dataid = request.session.setdefault('l_dataid', [])
    copy_letter_name = request.session.setdefault('copy_letter_name', [])

    if request.method == "POST":
        copy_letter_name = request.session.get('copy_letter_name')
        l_dataid = request.session.get('l_dataid', [])

        if "record" in request.POST:
            selected_option = request.session.get('selected_option')
            if selected_option is not None:
                request.session['l_dataid[0]'] = l_dataid[0]
                json_file_path = json_files[selected_option]
                data_id = request.session.get('data_id')
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

            if selected_option is not None:
                request.session['l_dataid[1]'] = l_dataid[1]
                json_file_path = json_files[selected_option]
                data_id = request.session.get('data_id')
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
            if selected_option is not None:
                request.session['l_dataid[2]'] = l_dataid[2]
                request.session['audio_recorded'] = True
                json_file_path = json_files[selected_option]
                data_id = request.session.get('data_id')
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
            if selected_option is not None:
                request.session['l_dataid[3]'] = l_dataid[3]
                request.session['audio_recorded'] = True
                json_file_path = json_files[selected_option]
                data_id = request.session.get('data_id')
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
            if selected_option is not None:
                request.session['l_dataid[4]'] = l_dataid[4]
                request.session['audio_recorded'] = True
                json_file_path = json_files[selected_option]
                data_id = request.session.get('data_id')
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
    """
    View function for handling the submission of retaken letter recordings.

    The function retrieves session variables such as 'l_audio_files', 'l_copy_audio_files',
    'l_audio_files_name', and 'l_dataid'.
    If the request method is POST and there is a file in the request data, it retrieves
    the letter data ID and the corresponding letter data.
    It saves the audio file in the media folder using the data ID as the filename.
    If the file path is already present in 'l_copy_audio_files', it updates the existing path.
    If 'l_copy_audio_files' is empty, it appends the path to the list.
    The 'filepath' session variable is updated with the newly saved file path.
    The 'letter_answer.html' template is rendered with the 'audio_url' variable set to the file path.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for rendering the 'letter_answer.html' template.

    """
    l_audio_files = request.session.setdefault('l_audio_files', [])
    l_copy_audio_files = request.session.get('l_copy_audio_files', [])
    l_audio_files_name = request.session.setdefault('l_audio_files_name', [])
    l_dataid = request.session.setdefault('l_dataid', [])

    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
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
            
        request.session['filepath'] = filepath
        return render(request, 'letter_answer.html', { 'audio_url': filepath})
    

def save_letter1(request):
    """
    View function for saving the recording of letter 1 and sending it for transcription.

    The function retrieves session variables such as 'l_dataid', 'filepath', 'selected_option',
    and 'data_id'.
    It retrieves the letter data corresponding to the selected option.
    If the selected option is 'English', it retrieves the letter data from the 'json_eng' file.
    The function then sends a POST request to a specified URL with the audio file and transcription parameters.
    If the response status code is 200, it updates the 'lc_res' session variable with the transcription result.
    If the 'lc_res' session variable is not present, it initializes it as an empty list.
    The function checks the length of 'lc_res' and if it reaches 5, it redirects to the 'lans_page' URL,
    passing the 'lc_res' as the 'l_res' context variable.
    If the response status code is not 200, it renders an error page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for rendering the 'lans_page' URL or an error page.

    """
    l_dataid = request.session.setdefault('l_dataid', [])
    filepath = request.session.get('filepath')
    selected_option = request.session.get('selected_option')
    request.session['l_dataid[0]'] = l_dataid[0]
    json_file_path = json_files.get(selected_option)
    data_id = request.session.get('data_id')
    
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
    if response.status_code == 200:
        lc_res = request.session.setdefault('lc_res', [])
        if request.session.get("lc_res",None) is None:
            lc_res = []
        else:
            lc_res = request.session.get("lc_res")
            lc_res[0] = response.text
            request.session["lc_res"] = lc_res
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
    """
    View function for handling the retake of letter 2.

    The function retrieves session variables such as 'l_audio_files', 'l_copy_audio_files',
    'l_audio_files_name', and 'l_dataid'.
    If the request method is POST and an audio file is present in the request,
    it saves the audio file, updates the session variables, and renders the 'letter_answer' template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for rendering the 'letter_answer' template with the audio URL.

    """
    l_audio_files = request.session.setdefault('l_audio_files', [])
    l_copy_audio_files = request.session.get('l_copy_audio_files', [])
    l_audio_files_name = request.session.setdefault('l_audio_files_name', [])
    l_dataid = request.session.setdefault('l_dataid', [])

    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
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
        request.session['filepath'] = filepath
        return render(request, 'letter_answer.html', { 'audio_url': filepath})


def save_letter2(request):
    """
    View function for saving the recording of letter 2 and sending it for transcription.

    The function retrieves session variables such as 'l_dataid', 'filepath', 'selected_option',
    and 'data_id'.
    It retrieves the letter data corresponding to the selected option.
    If the selected option is 'English', it retrieves the letter data from the 'json_eng' file.
    The function then sends a POST request to a specified URL with the audio file and transcription parameters.
    If the response status code is 200, it updates the 'lc_res' session variable with the transcription result.
    If the 'lc_res' session variable is not present, it initializes it as an empty list.
    The function checks the length of 'lc_res' and if it reaches 5, it redirects to the 'lans_page' URL,
    passing the 'lc_res' as the 'l_res' context variable.
    If the response status code is not 200, it renders an error page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for rendering the 'lans_page' URL or an error page.

    """
    l_dataid = request.session.setdefault('l_dataid', [])
    filepath = request.session.get('filepath')
    selected_option = request.session.get('selected_option')
    request.session['l_dataid[1]'] = l_dataid[1]
    json_file_path = json_files.get(selected_option)
    data_id = request.session.get('data_id')
    
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
    """
    View function for handling the retake of letter 3.

    The function retrieves session variables such as 'l_audio_files', 'l_copy_audio_files',
    'l_audio_files_name', and 'l_dataid'.
    If the request method is POST and an audio file is present in the request,
    it saves the audio file, updates the session variables, and renders the 'letter_answer' template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for rendering the 'letter_answer' template with the audio URL.

    """
    l_audio_files = request.session.setdefault('l_audio_files', [])
    l_copy_audio_files = request.session.get('l_copy_audio_files', [])
    l_audio_files_name = request.session.setdefault('l_audio_files_name', [])
    l_dataid = request.session.setdefault('l_dataid', [])

    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
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
        request.session['filepath'] = filepath
        return render(request, 'letter_answer.html', { 'audio_url': filepath})
    

def save_letter3(request):
    """
    View function for saving the recording of letter 3 and sending it for transcription.

    The function retrieves session variables such as 'l_dataid', 'filepath', 'selected_option',
    and 'data_id'.
    It retrieves the letter data corresponding to the selected option.
    If the selected option is 'English', it retrieves the letter data from the 'json_eng' file.
    The function then sends a POST request to a specified URL with the audio file and transcription parameters.
    If the response status code is 200, it updates the 'lc_res' session variable with the transcription result.
    If the 'lc_res' session variable is not present, it initializes it as an empty list.
    The function checks the length of 'lc_res' and if it reaches 5, it redirects to the 'lans_page' URL,
    passing the 'lc_res' as the 'l_res' context variable.
    If the response status code is not 200, it renders an error page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for rendering the 'lans_page' URL or an error page.

    """
    l_dataid = request.session.setdefault('l_dataid', [])
    filepath = request.session.get('filepath')
    selected_option = request.session.get('selected_option')
    request.session['l_dataid[2]'] = l_dataid[2]
    json_file_path = json_files.get(selected_option)
    data_id = request.session.get('data_id')
    
    if json_file_path:
        data = json_file_path
        if data is not None:
            for d in data['Letter']:
                if d['id'] == l_dataid[2]:
                    val = d['data']
                    break

    if selected_option == 'English':
        request.session['l_dataid[2]'] = l_dataid[2]
        data = json_eng
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
            request.session["lc_res"] = lc_res
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
    """
    View function for handling the retake of letter 4.

    The function retrieves session variables such as 'l_audio_files', 'l_copy_audio_files',
    'l_audio_files_name', and 'l_dataid'.
    If the request method is POST and an audio file is present in the request,
    it saves the audio file, updates the session variables, and renders the 'letter_answer' template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for rendering the 'letter_answer' template with the audio URL.

    """
    l_audio_files = request.session.setdefault('l_audio_files', [])
    l_copy_audio_files = request.session.get('l_copy_audio_files', [])
    l_audio_files_name = request.session.setdefault('l_audio_files_name', [])
    l_dataid = request.session.setdefault('l_dataid', [])

    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
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
        request.session['filepath'] = filepath
        return render(request, 'letter_answer.html', { 'audio_url': filepath})


def save_letter4(request):
    """
    View function for saving the recording of letter 4 and sending it for transcription.

    The function retrieves session variables such as 'l_dataid', 'filepath', 'selected_option',
    and 'data_id'.
    It retrieves the letter data corresponding to the selected option.
    If the selected option is 'English', it retrieves the letter data from the 'json_eng' file.
    The function then sends a POST request to a specified URL with the audio file and transcription parameters.
    If the response status code is 200, it updates the 'lc_res' session variable with the transcription result.
    If the 'lc_res' session variable is not present, it initializes it as an empty list.
    The function checks the length of 'lc_res' and if it reaches 5, it redirects to the 'lans_page' URL,
    passing the 'lc_res' as the 'l_res' context variable.
    If the response status code is not 200, it renders an error page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for rendering the 'lans_page' URL or an error page.

    """
    l_dataid = request.session.setdefault('l_dataid', [])
    filepath = request.session.get('filepath')
    selected_option = request.session.get('selected_option')
    request.session['l_dataid[3]'] = l_dataid[3]
    json_file_path = json_files.get(selected_option)
    data_id = request.session.get('data_id')

    if json_file_path:
        data = json_file_path
        if data is not None:
            for d in data['Letter']:
                if d['id'] == l_dataid[3]:
                    val = d['data']
                    break

    if selected_option == 'English':
        request.session['l_dataid[3]'] = l_dataid[3]
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
            request.session["lc_res"] = lc_res
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
    """
    View function for retaking the recording of letter 5.

    The function retrieves session variables such as 'l_audio_files', 'l_copy_audio_files', 'l_audio_files_name',
    and 'l_dataid'.
    If the request method is POST and there is a file attached in the request, it saves the file and updates
    the necessary session variables.
    The function creates a file path based on the 'l_dataid' and saves the uploaded audio file with that name.
    It then updates the 'l_copy_audio_files' session variable with the file path.
    If the 'l_copy_audio_files' list has less than 5 items, it appends the new file path.
    If the 'l_copy_audio_files' list has less than 4 items, it appends the new file path.
    Finally, the function renders the 'letter_answer.html' template, passing the 'audio_url' context variable
    as the file path of the saved audio file.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for rendering the 'letter_answer.html' template with the 'audio_url' context.

    """
    l_audio_files = request.session.setdefault('l_audio_files', [])
    l_copy_audio_files = request.session.get('l_copy_audio_files', [])
    l_audio_files_name = request.session.setdefault('l_audio_files_name', [])
    l_dataid = request.session.setdefault('l_dataid', [])

    if request.method == 'POST' and request.FILES.get('audio_blob'):
        data_id = request.session.get('data_id')
        val = request.POST.get('val')
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
        request.session['filepath'] = filepath
        return render(request, 'letter_answer.html', { 'audio_url': filepath})
    
def save_letter5(request):
    """
    View function for saving the recording of letter 5 and sending it for transcription.

    The function retrieves session variables such as 'l_dataid', 'filepath', 'selected_option',
    and 'data_id'.
    It retrieves the letter data corresponding to the selected option.
    If the selected option is 'English', it retrieves the letter data from the 'json_eng' file.
    The function then sends a POST request to a specified URL with the audio file and transcription parameters.
    If the response status code is 200, it updates the 'lc_res' session variable with the transcription result.
    If the 'lc_res' session variable is not present, it initializes it as an empty list.
    The function checks the length of 'lc_res' and if it reaches 5, it redirects to the 'lans_page' URL,
    passing the 'lc_res' as the 'l_res' context variable.
    If the response status code is not 200, it renders an error page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for rendering the 'lans_page' URL or an error page.

    """
    l_dataid = request.session.setdefault('l_dataid', [])
    filepath = request.session.get('filepath')
    selected_option = request.session.get('selected_option')
    request.session['l_dataid[4]'] = l_dataid[4]
    json_file_path = json_files.get(selected_option)
    data_id = request.session.get('data_id')
    
    # if json_file_path:
    #     data = json_file_path
    #     if data is not None:
    #         for d in data['Letter']:
    #             if d['id'] == l_dataid[4]:
    #                 val = d['data']
    #                 break

    # if selected_option == 'English':
    #     request.session['l_dataid[4]'] = l_dataid[4]
    #     data = json_eng
    #     for d in data['Letter']:
    #         if d['id'] == l_dataid[4]:
    #             val = d['data']
    #             break
    if json_file_path:
        data = json_file_path
        if data is not None:
            for letter_data in data['Letter']:
                if letter_data['id'] == l_dataid[4]:
                    val = letter_data['data']
                    break

    if selected_option == 'English':
        request.session['l_dataid[4]'] = l_dataid[4]
        data = json_eng
        for letter_data in data['Letter']:
            if letter_data['id'] == l_dataid[4]:
                val = letter_data['data']
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
            if len(lc_res) ==5:
                lc_res[4] = response.text
            else:
                lc_res.insert(4, response.text)
            request.session["lc_res"] = lc_res
            if len(lc_res)==5:
                request.session['lc_rec'] = lc_res
                context = {'l_res': lc_res}
                url = reverse('lans_page')
                if len(lc_res)==5:
                    return redirect(url,context)
                    
    else:
        return render(request, 'Error/pages-500.html' )


def seventeen(request):
    """
    View function for rendering the 'seventeen.html' template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for rendering the 'seventeen.html' template.
    """
    return render(request,'seventeen.html')


def word_msg(request):
    """
    View function for rendering the 'answer_word.html' template.

    Retrieves the 'child_name' session variable and passes it as the 'child_name' context variable
    to the template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for rendering the 'answer_word.html' template with the 'child_name' context.
    """
    child_name = request.session.get('child_name')
    return render(request,'answer_word.html',{'child_name': child_name})


def next_answer(request):
    """
    View function for rendering the 'answer_story.html' template.

    Retrieves the 'child_name' session variable and passes it as the 'child_name' context variable
    to the template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for rendering the 'answer_story.html' template with the 'child_name' context.
    """
    child_name = request.session.get('child_name')
    return render(request,'answer_story.html',{'child_name': child_name})


def word_ltr(request):
    """
    View function for rendering the 'answer_letter.html' template.

    Retrieves the 'child_name' session variable and passes it as the 'child_name' context variable
    to the template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for rendering the 'answer_letter.html' template with the 'child_name' context.
    """
    child_name = request.session.get('child_name')
    return render(request,'answer_letter.html',{'child_name': child_name})

def word_beg(request):
    """
    View function for rendering the 'answer_beginer.html' template.

    Retrieves the 'child_name' session variable and passes it as the 'child_name' context variable
    to the template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response for rendering the 'answer_beginer.html' template with the 'child_name' context.
    """
    child_name = request.session.get('child_name')
    return render(request,'answer_beginer.html',{'child_name': child_name})

    
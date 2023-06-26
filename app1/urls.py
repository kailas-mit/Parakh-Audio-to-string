"""parakh URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from django.views.i18n import set_language
# from django.utils.translation import gettext_lazy as _
from . import views

# app_name = 'app1'

urlpatterns = [
    path('',views.first, name='first'),
    path('login',  views.login, name='login'),
    # path(_('login'), views.login, name='login'),
    
    path('testing',  views.testing, name='testing'),
    path('language/', set_language, name='set_language'),
    path('choose_avatar',  views.choose_avatar, name='choose_avatar'),
    path('select_profile', views.select_profile, name='select_profile'),

    path('language', views.language, name='language'),
    path('aop_language', views.aop_language, name='aop_language'),
    path('red_start', views.red_start, name='red_start'),
    path('start_assesment/<str:selected_option>/', views.start_assesment, name='start_assesment'),
    path('gen_aop_redirect/<str:selected_option>/', views.gen_aop_redirect, name='gen_aop_redirect'),

    # path('start_assesment', views.start_assesment, name='start_assesment'),

############################################################################ English Level

    path('bl', views.bl, name='bl'),
    path('bl_next', views.bl_next, name='bl_next'),
    path('nextpage', views.nextpage, name='nextpage'),
    path('start_recording_bl', views.start_recording_bl, name='start_recording_bl'),
    path('start_recording_next_bl', views.start_recording_next_bl, name='start_recording_next_bl'),
    path('save_file_bl', views.save_file_bl, name='save_file_bl'),
    path('bl_answer', views.bl_answer, name='bl_answer'),
    path('bl_answer_final', views.bl_answer_final, name='bl_answer_final'),
    path('bl_retake', views.bl_retake, name='bl_retake'),
    path('bl_skip', views.bl_skip, name='bl_skip'),
    path('bl_skip_next', views.bl_skip_next, name='bl_skip_next'),
    path('bl_store', views.bl_store, name='bl_store'),
    path('bl_next_store', views.bl_next_store, name='bl_next_store'),

    path('bl_mcq', views.bl_mcq, name='bl_mcq'),
    path('bl_final_mcq', views.bl_final_mcq, name='bl_final_mcq'),

    path('bl_mcq_next', views.bl_mcq_next, name='bl_mcq_next'),
    path('bl_mcq_next_mcq', views.bl_mcq_next_mcq, name='bl_mcq_next_mcq'),
    path('bl_mcq_last', views.bl_mcq_last, name='bl_mcq_last'),
    path('bl_story_mcq_last', views.bl_story_mcq_last, name='bl_story_mcq_last'),
    path('bl_story_mcq_next_mcq', views.bl_story_mcq_next_mcq, name='bl_story_mcq_next_mcq'),

    path('error_recording', views.error_recording, name='error_recording'),

    path('bl_mcq_api', views.bl_mcq_api, name='bl_mcq_api'),
    path('bl_answer_page', views.bl_answer_page, name='bl_answer_page'),
    path('msg_api', views.msg_api, name='msg_api'),


    path('start', views.start, name='start'),

    path('ml1', views.ml1, name='ml1'),
    path('ml1_next', views.ml1_next, name='ml1_next'),
    path('nextpage', views.nextpage, name='nextpage'),
    path('start_recording_ml1', views.start_recording_ml1, name='start_recording_ml1'),
    path('start_recording_next_ml1', views.start_recording_next_ml1, name='start_recording_next_ml1'),
    path('save_file_ml1', views.save_file_ml1, name='save_file_ml1'),
    path('ml1_answer', views.ml1_answer, name='ml1_answer'),
    path('ml1_answer_final', views.ml1_answer_final, name='ml1_answer_final'),
    path('ml1_retake', views.ml1_retake, name='ml1_retake'),
    path('ml1_skip', views.ml1_skip, name='ml1_skip'),
    path('ml1_skip_next', views.ml1_skip_next, name='ml1_skip_next'),
    path('ml1_store', views.ml1_store, name='ml1_store'),
    path('ml1_next_store', views.ml1_next_store, name='ml1_next_store'),

    path('ml1_mcq', views.ml1_mcq, name='ml1_mcq'),
    path('ml1_final_mcq', views.ml1_final_mcq, name='ml1_final_mcq'),

    path('ml1_mcq_next', views.ml1_mcq_next, name='ml1_mcq_next'),
    path('ml1_mcq_api', views.ml1_mcq_api, name='ml1_mcq_api'),

    path('ml2', views.ml2, name='ml2'),
    path('ml2_next', views.ml2_next, name='ml2_next'),
    path('nextpage', views.nextpage, name='nextpage'),
    path('start_recording_ml2', views.start_recording_ml2, name='start_recording_ml2'),
    path('start_recording_next_ml2', views.start_recording_next_ml2, name='start_recording_next_ml2'),
    path('save_file_ml2', views.save_file_ml2, name='save_file_ml2'),
    path('ml2_answer', views.ml2_answer, name='ml2_answer'),
    path('ml2_answer_final', views.ml2_answer_final, name='ml2_answer_final'),
    path('ml2_retake', views.ml2_retake, name='ml2_retake'),
    path('ml2_skip', views.ml2_skip, name='ml2_skip'),
    path('ml2_skip_next', views.ml2_skip_next, name='ml2_skip_next'),
    path('ml2_store', views.ml2_store, name='ml2_store'),
    path('ml2_next_store', views.ml2_next_store, name='ml2_next_store'),


    path('ml2_mcq', views.ml2_mcq, name='ml2_mcq'),
    path('ml2_final_mcq', views.ml2_final_mcq, name='ml2_final_mcq'),

    path('ml2_mcq_next', views.ml2_mcq_next, name='ml2_mcq_next'),
    path('ml2_mcq_api', views.ml2_mcq_api, name='ml2_mcq_api'),

    path('ml3', views.ml3, name='ml3'),
    path('ml3_next', views.ml3_next, name='ml3_next'),
    path('nextpage', views.nextpage, name='nextpage'),
    path('start_recording_ml3', views.start_recording_ml3, name='start_recording_ml3'),
    path('start_recording_next_ml3', views.start_recording_next_ml3, name='start_recording_next_ml3'),
    path('save_file_ml3', views.save_file_ml3, name='save_file_ml3'),
    path('ml3_answer', views.ml3_answer, name='ml3_answer'),
    path('ml3_answer_final', views.ml3_answer_final, name='ml3_answer_final'),
    path('ml3_retake', views.ml3_retake, name='ml3_retake'),
    path('ml3_skip', views.ml3_skip, name='ml3_skip'),
    path('ml3_skip_next', views.ml3_skip_next, name='ml3_skip_next'),
    path('ml3_store', views.ml3_store, name='ml3_store'),
    path('ml3_next_store', views.ml3_next_store, name='ml3_next_store'),
    path('ml3_mcq', views.ml3_mcq, name='ml3_mcq'),
    path('ml3_final_mcq', views.ml3_final_mcq, name='ml3_final_mcq'),
    path('ml3_mcq_next', views.ml3_mcq_next, name='ml3_mcq_next'),
    path('ml3_mcq_api', views.ml3_mcq_api, name='ml3_mcq_api'),
    path('ml3_ans', views.ml3_ans, name='ml3_ans'),




############################################################################ Paragraph

    path('paragraph', views.paragraph, name='paragraph'),
    path('start_recording', views.start_recording, name='start_recording'),
    path('answer/<str:text>/', views.answer, name='answer'),
    path('answer', views.answer, name='answer'),
    path('skip_answer', views.skip_answer, name='skip_answer'),
    path('next_page_para', views.next_page_para, name='next_page_para'),
    path('next_page_story', views.next_page_story, name='next_page_story'),
    path('next_page_letter', views.next_page_letter, name='next_page_letter'),


    path('next_page', views.next_page, name='next_page'),
    path('aop_num/<str:selected_option>/<str:my_program>/', views.aop_num, name='aop_num'),
    path('next_para', views.next_para, name='next_para'),
    path('save_file', views.save_file, name='save_file'),
    # path('para_skip', views.para_skip, name='para_skip'),

############################################################################ Story

    path('story', views.story, name='story'),
    path('story_recording', views.story_recording, name='story_recording'),
    path('story_answer/<str:text>/', views.story_answer, name='story_answer'),
    path('story_answer', views.story_answer, name='story_answer'),
    path('skip_story_answer', views.skip_story_answer, name='skip_story_answer'),
    path('next_story', views.next_story, name='next_story'),
    path('save_story', views.save_story, name='save_story'),
    # path('story_skip', views.story_skip, name='story_skip'),


#
    path('thirteen', views.thirteen, name='thirteen'),
    path('fourteen', views.fourteen, name='fourteen'),

############################################################################ Word

    path('word', views.word, name='word'),
    path('word_recording', views.word_recording, name='word_recording'),
    path('word_recording_next', views.word_recording_next, name='word_recording_next'),
    path('word_answer', views.word_answer, name='word_answer'),
    # path('skip_word_answer', views.skip_word_answer, name='skip_word_answer'),
    path('next_word', views.next_word, name='next_word'),
    path('save_word', views.save_word, name='save_word'),
    # path('word_skip_save', views.word_skip_save, name='word_skip_save'),

    path('wans_page', views.wans_page, name='wans_page'),
    path('word_skip', views.word_skip, name='word_skip'),
    path('submit_word_skip', views.submit_word_skip, name='submit_word_skip'),

    path('retake_word', views.retake_word, name='retake_word'),
    path('save_word1', views.save_word1, name='save_word1'),
    path('retake_word2', views.retake_word2, name='retake_word2'),
    path('save_word2', views.save_word2, name='save_word2'),
    path('retake_word3', views.retake_word3, name='retake_word3'),
    path('save_word3', views.save_word3, name='save_word3'),
    path('retake_word4', views.retake_word4, name='retake_word4'),
    path('save_word4', views.save_word4, name='save_word4'),
    path('retake_word5', views.retake_word5, name='retake_word5'),
    path('save_word5', views.save_word5, name='save_word5'),

############################################################################ Letter

    path('letter', views.letter, name='letter'),
    path('letter_recording', views.letter_recording, name='letter_recording'),
    path('letter_recording_next', views.letter_recording_next, name='letter_recording_next'),
    path('letter_answer', views.letter_answer, name='letter_answer'),
    path('next_letter', views.next_letter, name='next_letter'),
    path('save_letter', views.save_letter, name='save_letter'),
    path('lans_page', views.lans_page, name='lans_page'),
    path('letter_skip', views.letter_skip, name='letter_skip'),
    path('submit_letter_skip', views.submit_letter_skip, name='submit_letter_skip'),

    path('retake_letter', views.retake_letter, name='retake_letter'),
    path('save_letter1', views.save_letter1, name='save_letter1'),
    path('retake_letter2', views.retake_letter2, name='retake_letter2'),
    path('save_letter2', views.save_letter2, name='save_letter2'),
    path('retake_letter3', views.retake_letter3, name='retake_letter3'),
    path('save_letter3', views.save_letter3, name='save_letter3'),
    path('retake_letter4', views.retake_letter4, name='retake_letter4'),
    path('save_letter4', views.save_letter4, name='save_letter4'),
    path('retake_letter5', views.retake_letter5, name='retake_letter5'),
    path('save_letter5', views.save_letter5, name='save_letter5'),
############################################################################
    path('seventeen', views.seventeen, name='seventeen'),
    path('next_answer', views.next_answer, name='next_answer'),
    path('word_msg', views.word_msg, name='word_msg'),
    path('word_ltr', views.word_ltr, name='word_ltr'),
    path('word_beg', views.word_beg, name='word_beg'),
    # path('start_nextpage', views.start_nextpage, name='start_nextpage'),


    #advance english
    path('advance_bl_store', views.advance_bl_store, name='advance_bl_store'),


    # path('home',views.home, name='home'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
        urlpatterns += static(settings.STATIC_URL , document_root=settings.STATIC_ROOT)

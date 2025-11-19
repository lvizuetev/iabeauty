import os
import time
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.conf import settings

from .models import Empleado, Comment
from django.views.generic import DetailView, UpdateView
from django.shortcuts import get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth import login
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import CreateCommentForm, UserEmpleadoRegisterForm, UserLoginForm, EmpleadoUpdateForm
from django.views.decorators.http import require_POST
from beautyai.prediction import RecognitionError, predict_face_shape, predict_skin_tone, detect_skin_subtone
from beautyai.constants import recommended_hair_tones, skin_tones, skin_subtones, recommended_eyebrow, face_shapes, recommended_makeup
from django.core.files.storage import FileSystemStorage
from beautyai.hairSegmentation import segment_hair

# Create your views here.


def login_view(request):
    return render(request, 'login.html')

@require_POST
def skintone_recognition(request):
    if (request.method == 'POST'):
        try:
            # Obtener el id del usuario
            user_id = request.user.id
            user_folder = os.path.join(settings.MEDIA_ROOT, f'user_{user_id}')

            # Crear la carpeta del usuario si no existe
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)

            deleteProcessedFiles(user_id)
            skin_tone_value = predict_skin_tone(os.path.join(user_folder, 'uploaded_image.jpg'), user_folder)
            skin_subtone_value = detect_skin_subtone(skin_tone_value, os.path.join(user_folder, 'uploaded_image.jpg'))
            file_rect_url = os.path.join('/media', f'user_{user_id}', 'face_rect.jpg')
            file_crop_url = os.path.join('/media', f'user_{user_id}', 'face_crop.jpg')
            data = {
                'skinTone': skin_tones[skin_tone_value],
                'skinSubtone': skin_subtones[skin_subtone_value],
                'recommendedMakeup': recommended_makeup[skin_tone_value][skin_subtone_value],
                'fileRectUrl': file_rect_url,
                'fileRectCrop': file_crop_url,
            }
            return JsonResponse(data)
        except (RecognitionError, Exception) as e:
            data = {
                'error': str(e)
            }
            print(data['error'])
            return JsonResponse(data, status=500)
    else:
        return redirect('home');

@require_POST
def hairtone_recognition(request):
    if (request.method == 'POST'):
        try:
            # Obtener el id del usuario
            user_id = request.user.id
            user_folder = os.path.join(settings.MEDIA_ROOT, f'user_{user_id}')

            # Crear la carpeta del usuario si no existe
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)
            deleteProcessedFiles(user_id)
            skin_tone_value = predict_skin_tone(os.path.join(user_folder, 'uploaded_image.jpg'), user_folder)
            skin_subtone_value = detect_skin_subtone(skin_tone_value, os.path.join(user_folder, 'uploaded_image.jpg'))
            file_rect_url = os.path.join('/media', f'user_{user_id}', 'face_rect.jpg')
            file_crop_url = os.path.join('/media', f'user_{user_id}', 'face_crop.jpg')
            data = {
                'skinTone': skin_tones[skin_tone_value],
                'skinSubtone': skin_subtones[skin_subtone_value],
                'recommendedHairTones': recommended_hair_tones[skin_tone_value][skin_subtone_value],
                'fileRectUrl': file_rect_url,
                'fileRectCrop': file_crop_url,
            }
            return JsonResponse(data)
        except (RecognitionError, Exception) as e:
            data = {
                'error': str(e)
            }
            print(data['error'])
            return JsonResponse(data, status=500)
    else:
        return redirect('home');

@require_POST
def eyebrow_recognition(request):
    if (request.method == 'POST'):
        try:
            # Obtener el id del usuario
            user_id = request.user.id
            user_folder = os.path.join(settings.MEDIA_ROOT, f'user_{user_id}')

            fs = FileSystemStorage()
            fs = FileSystemStorage(location=user_folder)

            # Crear la carpeta del usuario si no existe
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)

            deleteProcessedFiles(user_id)
            face_shape_value = predict_face_shape(os.path.join(user_folder, 'uploaded_image.jpg'), user_folder)
            file_rect_url = os.path.join('/media', f'user_{user_id}', 'face_rect.jpg')
            file_crop_url = os.path.join('/media', f'user_{user_id}', 'face_crop.jpg')
            file_marks_url = os.path.join('/media', f'user_{user_id}', 'face_landmarks.jpg')
            file_landmarks_url = os.path.join('/media', f'user_{user_id}', 'face_landmarks.jpg')

            file_marks_name = "face_landmarks.jpg"
            if not (fs.exists(file_marks_name)):
                file_marks_url = None

            data = {
                'faceShape': face_shapes[face_shape_value],
                'recommendedEyebrow': recommended_eyebrow[face_shape_value],
                'fileRectUrl': file_rect_url,
                'fileRectCropUrl': file_crop_url,
                'fileLandmarksUrl': file_marks_url,
            }
            return JsonResponse(data)
        except (RecognitionError, Exception) as e:
            data = {
                'error': str(e)
            }
            print(data['error'])
            return JsonResponse(data, status=500)
    else:
        return redirect('home');


@login_required
def hairtone_makeup(request):
    if (request.method == 'POST'):
        try:
             # Obtener el id del usuario
            user_id = request.user.id
            user_folder = os.path.join(settings.MEDIA_ROOT, f'user_{user_id}')

            fs = FileSystemStorage()
            fs = FileSystemStorage(location=user_folder)

            # Crear la carpeta del usuario si no existe
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)
        
            segment_hair(os.path.join(user_folder, 'uploaded_image.jpg'), request.POST.get('color'), user_folder)

            recolor_hair_url = os.path.join('/media', f'user_{user_id}', 'recolor_hair.jpg')
            original_hair_url = os.path.join('/media', f'user_{user_id}', 'uploaded-image.jpg')

            file_recolor_name = "recolor_hair.jpg"
            if not (fs.exists(file_recolor_name)):
                recolor_hair_url = None

            data = {
                'originalHairUrl': original_hair_url,
                'recolorHairUrl': recolor_hair_url,
            }
            return JsonResponse(data)

        except Exception as e:
            data = {
                'error': str(e)
            }
            return JsonResponse(data, status=500)
    else:
        return redirect('home');

@login_required
def home(request):
    file_url = check_file_uploaded(request)
    employee = Empleado.objects.get(user=request.user)
    if (file_url):
        context = { 'file_url': file_url, 'employee': employee }
        return render(request, 'index.html', context)
    else:
        context = { 'employee': employee }
        return render(request, 'index.html', context)

@login_required
def skin_tone_view(request):
    file_url = check_file_uploaded(request)
    if (file_url):
        context = { 'file_url': file_url }
        return render(request, 'rec_tono_piel.html', context)
    else:
        return redirect('home')

@login_required
def eyebrow_view(request):
    file_url = check_file_uploaded(request)
    if (file_url):
        context = { 'file_url': file_url }
        return render(request, 'rec_tip_ceja.html', context)
    else:
        return redirect('home')

@login_required
def hair_tone_view(request):
    file_url = check_file_uploaded(request)
    if (file_url):
        context = { 'file_url': file_url }
        return render(request, 'rec_tono_cabello.html', context)
    else:
        return redirect('home')

@login_required
@require_POST
def upload_file(request):
    if (request.method == 'POST' and request.FILES.get('uploaded_file')):
        uploaded_file = request.FILES['uploaded_file']
        fs = FileSystemStorage()

        # Obtener el id del usuario
        user_id = request.user.id
        user_folder = os.path.join(settings.MEDIA_ROOT, f'user_{user_id}')

        # Crear la carpeta del usuario si no existe
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        fs = FileSystemStorage(location=user_folder)

        # Verificar si hay un archivo subido existente en media
        file_name = "uploaded_image.jpg"
        file_url = os.path.join('/media', f'user_{user_id}', file_name)
        if fs.exists(file_name):
            fs.delete(file_name)
            request.session.pop('uploaded_file_url', None)

        # Guardar el archivo de imagen subido
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_url = os.path.join('/media', f'user_{user_id}',filename)
        request.session['uploaded_file_url'] = file_url
        response = {
            'uploadedFileUrl': file_url
        }
        return JsonResponse(response)
    else:
        redirect('home')

@login_required
def cal_sug_view(request):
    empleado = Empleado.objects.get(user=request.user)
    
    initial_data = {
        'nombre': f'{empleado.nombre} {empleado.apellido}', 
        'email': empleado.email,
        'commentario': ''
    }

    comments = Comment.objects.all()
    form = CreateCommentForm(initial_data)

    photo = None
    if (empleado.foto):
        photo = empleado.foto.url


    context = {
        'empleado': empleado, 
        'profile_photo': photo, 
        'form': form, 
        'comments': comments 
    }
    return render(request, 'cal_sug.html', context)


def check_file_uploaded(request):

    # Obtener el id del usuario y la url de la imagen
    user_id = request.user.id
    user_folder = os.path.join(settings.MEDIA_ROOT, f'user_{user_id}')
    file_name = "uploaded_image.jpg"
    file_url = os.path.join('/media', f'user_{user_id}', file_name)
    fs = FileSystemStorage(location=user_folder)

    if fs.exists(file_name):
        request.session["uploaded_file_url"] = file_url
        # Este parámetro se añade para evitar la caché del navegador
        unique_url = f"{file_url}?v={int(time.time())}"
        return unique_url
        # return file_url
    else:
        messages.warning(request, 'Por favor seleccione una foto antes de continuar.')
        return None
    
def deleteProcessedFiles(user_id):
    user_folder = os.path.join(settings.MEDIA_ROOT, f'user_{user_id}')
    files = ["face_landmarks.jpg", "face_crop.jpg", "face_rect.jpg"]
    fs = FileSystemStorage(location=user_folder)
    for file_name in files:
        fs.delete(file_name)

class UserRegisterView(FormView):
    template_name = 'loginout/register.html'
    form_class = UserEmpleadoRegisterForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return redirect(self.success_url)

class UserLoginView(LoginView):
    template_name = 'loginout/login.html'
    form_class = UserLoginForm

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('login')


@method_decorator(login_required, name='dispatch')
class ProfileDetailView(DetailView):
    model = Empleado
    template_name = 'profile/profile_dt.html'
    context_object_name = 'empleado'

    def get_object(self):
        return get_object_or_404(Empleado, user=self.request.user)

@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    model = Empleado
    form_class = EmpleadoUpdateForm
    template_name = 'profile/profile_edt.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return get_object_or_404(Empleado, user=self.request.user)
    
@login_required
def create_comment(request):
    if (request.method == 'POST'):
        try:
            form = CreateCommentForm(request.POST)
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.save()
            return redirect("cal_sug")
        except ValueError:
            return render(request, 'create_task.html', {
                'form': CreateCommentForm,
                'error': 'Por favor revise que los datos'
            })
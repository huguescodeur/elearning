import os
import base64
from functools import wraps
import re
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password, check_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import connection
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from django.contrib.auth import logout
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import uuid
import jwt
import datetime
import secrets


# Logique du décirateur
def custom_login_required(f):
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        if 'user_id' not in request.session:
            return redirect('/connexion/')
        return f(request, *args, **kwargs)

    return decorated_function


# ? Logout
def logout_view(request):
    logout(request)
    return redirect('connexion')


# ? Connexion
def connexion_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # ? utilisateur existe ?
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM account_user WHERE email = %s", [email])
            user = cursor.fetchone()

        if user and check_password(password, user[1]):
            request.session['user_id'] = user[0]
            with connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE account_user
                    SET last_login = %s WHERE email = %s""", [timezone.now(), email])
            return redirect("accueil")

        else:
            messages.error(request, "Email ou mot de passe incorrect")
            return render(request, "connexion.html")

    else:
        current_view_name = request.resolver_match.url_name
        context = {'title': 'Connexion',
                   'current_view_name': current_view_name, }
        return render(request, 'connexion.html', context)


# ? Gestion Back-End inscription
# @custom_login_required
def inscription_view(request):
    if request.method == 'POST':

        nom = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')
        role = request.POST.get('role', 'apprenant')
        default_image = "static/user_image/default_image.png"

        # default_image = 'account/static/images/default.jpg'

        # ? Password pareil??
        if password != confirmpassword:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('inscription')

        # ? utilisateur existe ?
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM account_user WHERE email = %s", [email])
            existing_user = cursor.fetchone()

        if existing_user:
            messages.error(request, "Email déjà utilisé par un utilisateur !")
            return render(request, 'inscription.html', )

        hashed_password = make_password(password)

        # Insértion account_user
        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO account_user
                (username, email, password, role, nom, date_joined, first_name, last_name, 
                is_staff, is_active, is_superuser, last_login, image)
                VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                [nom, email, hashed_password, role, nom, timezone.now(), nom, nom, False, True, False,
                 timezone.now(), default_image])

            # Récupérez l'ID du nouvel utilisateur
            cursor.execute(
                "SELECT id FROM account_user WHERE email = %s", [email])
            user_id = cursor.fetchone()[0]

        # Insertion nouvel apprenant
        if role == 'apprenant':
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO account_apprenant (nom_apprenant, is_premium, user_id) VALUES (%s, %s, %s)",
                    [nom, False, user_id])

        messages.success(request, "Inscription réussie!")

        request.session['user_id'] = user_id
        return redirect('accueil')

    else:
        current_view_name = request.resolver_match.url_name
        context = {'title': 'inscription',
                   'current_view_name': current_view_name, }
        return render(request, 'inscription.html', context)


# ? Settings
@custom_login_required
def settings_view(request):
    user_id = request.session.get('user_id', None)

    current_view_name = request.resolver_match.url_name
    context = {'title': 'Paramètres', 'current_view_name': current_view_name}

    if user_id is not None:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM account_user WHERE id = %s", [user_id])
            user = cursor.fetchone()

        print(user)

        context['user'] = user
        context["image_url"] = context["user"][13].replace(
            'static/', '')

        print(context['user'])
        print(context["image_url"])
    # print(context["user"][-1])

    return render(request, 'settings/settings.html', context)


# ? Update User Info Compte
@custom_login_required
def update_user_info_view(request):
    user_id = request.session.get('user_id', None)

    if user_id is not None:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM account_user WHERE id = %s", [user_id])
            user = cursor.fetchone()
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        old_password = request.POST.get('password-actuel')
        new_password = request.POST.get('new-password')
        confirm_password = request.POST.get('confirm-password')

        print("Name", name)
        print("Email", email)
        print("Old_password", old_password)
        print("New_password", new_password)
        print("Confirm_password", confirm_password)

        with connection.cursor() as cursor:
            if name:
                cursor.execute(
                    "UPDATE account_user SET nom = %s, username = %s, first_name = %s, last_name = %s WHERE id = %s",
                    [name, name, name, name, user_id]
                )

                print("New Name", name)
            if email:
                try:
                    validate_email(email)
                    cursor.execute("UPDATE account_user SET email = %s WHERE id = %s", [
                        email, user_id])
                except ValidationError:
                    return JsonResponse({'error_message': 'Email non valide.'})

            if old_password and new_password and confirm_password:
                current_password = user[1]
                if not check_password(old_password, current_password):
                    return JsonResponse({'error_message': 'Le mot de passe actuel est incorrect.'})

                if new_password != confirm_password:
                    return JsonResponse({'error_message': 'Les mots de passe ne correspondent pas.'})

                if check_password(old_password, user[1]):
                    hashed_password = make_password(new_password)
                    cursor.execute("UPDATE account_user SET password = %s WHERE id = %s", [
                        hashed_password, user_id])
                    print("Password updated", new_password)
                    # return redirect(reverse('settings'))
                    return JsonResponse({'redirect_url': reverse('settings')})

        return redirect(request.META.get('HTTP_REFERER', 'settings'))
        # return redirect(reverse('settings'))


# ? Update image
@custom_login_required
def update_image_view(request):
    user_id = request.session.get('user_id', None)

    if user_id is not None:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM account_user WHERE id = %s", [user_id])
            user = cursor.fetchone()

    if request.method == 'POST':
        image_data = request.FILES['new-image']
        file_name = "{}_{}".format(user[12], image_data.name.replace(' ', '_'))
        file_path = "static/user_image/{}".format(file_name)

        with open(file_path, 'wb+') as destination:
            for chunk in image_data.chunks():
                destination.write(chunk)

        with connection.cursor() as cursor:
            cursor.execute("UPDATE account_user SET image = %s WHERE id = %s", [
                           file_path, user_id])

        return JsonResponse({'redirect_url': reverse('settings')})
    else:
        return JsonResponse({'status': 'failed'})


# ? Delete account
@custom_login_required
def delete_account_view(request):
    user_id = request.session.get('user_id', None)
    with connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM account_apprenant WHERE user_id = %s", [user_id])
        cursor.execute(
            "DELETE FROM account_formateur WHERE user_id = %s", [user_id])
        cursor.execute("DELETE FROM account_user WHERE id = %s", [user_id])
        logout(request)
    return JsonResponse({'redirect_url': reverse('connexion')})


# ? Premium account
def premium_account_view(request):
    user_id = request.session.get('user_id', None)

    current_view_name = request.resolver_match.url_name
    context = {'title': 'Premium', 'current_view_name': current_view_name}

    if user_id is not None:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM account_user WHERE id = %s", [user_id])
            user = cursor.fetchone()

        context['user'] = user
        context["image_url"] = context["user"][13].replace(
            'static/', '')

    return render(request, 'premium/premium.html', context)


# ? Methode d'envoie email
def send_email(sender_email, receiver_email, password, name, email, message_text, request):
    try:
        # Configuration de l'email
        subject = f"Nouveau message de votre formulaire de contact"
        body = f"Nom: {name}\nEmail: {email}\nMessage: {message_text}"

        # Création de l'email
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Reply-To"] = email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # Connexion au serveur SMTP et envoi de l'email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        messages.success(request, 'Email envoyé avec succès!')
    except smtplib.SMTPAuthenticationError:
        messages.error(
            request, "Erreur d'authentification . Vérifiez votre adresse e-mail et votre mot de passe.")
    except Exception as e:
        print(f"Erreur:{e}")
        messages.error(
            request, f"Une erreur s'est produite lors de l'envoi de l'e-mail : {e}")


# ? Contact
def envoie_message_view(request):
    user_id = request.session.get('user_id', None)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message_text = request.POST.get('textarea')

        if user_id is not None:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM account_user WHERE id = %s", [user_id])
                user = cursor.fetchone()

                # Envoyer un email
                sender_email = os.environ.get('EMAIL_HOST_SENDER')
                receiver_email = os.environ.get('EMAIL_HOST_RECEIVER')
                password = os.environ.get('EMAIL_HOST_PASSWORD')

                send_email(sender_email, receiver_email,
                           password, name, email, message_text, request)

                # Insérer les données dans la base de données
                try:
                    with connection.cursor() as cursor:
                        current_time = timezone.now()
                        cursor.execute("INSERT INTO account_contact (user_id, name, email, message, date) VALUES (%s, %s, %s, %s, %s)", [
                            user_id, name, email, message_text, current_time])
                        print(
                            'Message enregistré avec succès!')
                        return redirect("contact")
                except Exception as e:
                    print(
                        f'Une erreur s\'est produite lors de l\'insertion des données dans la base de données : {e}')
                    return redirect("contact")

        elif user_id is None:
            sender_email = os.environ.get('EMAIL_HOST_SENDER')
            receiver_email = os.environ.get('EMAIL_HOST_RECEIVER')
            password = os.environ.get('EMAIL_HOST_PASSWORD')

            send_email(sender_email, receiver_email,
                       password, name, email, message_text, request)
            try:
                with connection.cursor() as cursor:
                    current_time = timezone.now()
                    cursor.execute("INSERT INTO account_guestcontact (name, email, message, date) VALUES (%s, %s, %s, %s)", [
                        name, email, message_text, current_time])
                print(
                    'Message enregistré avec succès!')
                return redirect("contact")
            except Exception as e:
                print(
                    f'Une erreur s\'est produite lors de l\'insertion des données dans la base de données : {e}')

                return redirect("contact")
    else:
        return redirect("contact")


# ? Forgot password
def forgot_password_view(request):
    current_view_name = request.resolver_match.url_name
    context = {'title': 'Password', 'current_view_name': current_view_name}

    if request.method == 'POST':
        email = request.POST.get('email')
        user_password = ""
        user_name = ""

        with connection.cursor() as cursor:
            cursor.execute("SELECT nom, password FROM account_user WHERE email = %s", [
                email])

            user = cursor.fetchone()

        print(user)

        if user is not None:
            user_name = user[0]
            user_password = user[1]

            # Générer un jeton unique
            # token = uuid.uuid4().hex
            secret = secrets.token_hex(32)
            print(secret)
            token = jwt.encode({
                'email': email,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
            }, secret, algorithm='HS256')

            print(token)

            sender_email = os.environ.get('EMAIL_HOST_SENDER')
            receiver_email = email
            password = os.environ.get('EMAIL_HOST_PASSWORD')

            reset_link = request.build_absolute_uri(
                reverse('reset_password')) + '?token=' + token

            # Créer le message
            message = f"Bonjour {user_name},\n\nPour réinitialiser votre mot de passe, veuillez cliquer sur le lien suivant :\n{
                reset_link}\n\nCordialement,\nL'équipe"

            send_email(sender_email, receiver_email,
                       password, user_name, email, message, request)

            return redirect("connexion")

        else:
            messages.error(
                request, "Erreur d'envoie . Vérifiez votre adresse e-mail ")
            return redirect("password_reset")

    return render(request, "forgot_password.html", context)


# ? Password Reset
def reset_password_view(request):
    token = request.GET.get('token')
    print(token)

    current_view_name = request.resolver_match.url_name
    context = {'title': 'Nouveau password',
               'current_view_name': current_view_name,
               'token': token
               }

    if request.method == 'POST':
        new_password = request.POST.get('new-password')
        confirm_password = request.POST.get('confirm-password')
        token = request.POST.get('token')

        if new_password != confirm_password:
            print("Different")
            messages.error(request, "Les mots de passe ne correspondent pas.")
            # return redirect('reset_password', token=token)
            return HttpResponseRedirect(reverse('reset_password') + '?token=' + token)

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            email = payload['email']

            print(f"Mon email: {email}")

            with connection.cursor() as cursor:
                hashed_password = make_password(new_password)
                cursor.execute("UPDATE account_user SET password = %s WHERE email = %s", [
                    hashed_password, email])

            messages.success(
                request, "Votre mot de passe a été réinitialisé avec succès.")

            return redirect('connexion')

        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            messages.error(
                request, "Le lien de réinitialisation du mot de passe est invalide ou a expiré.")

            return redirect("password_reset")

    return render(request, "reset_password.html", context)

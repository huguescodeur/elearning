import json

from django.db import connection
from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404

from videos.models import Videos
from django.http import JsonResponse
from django.core import serializers


def convert_microseconds_to_time(microseconds):
    microseconds = int(microseconds)
    seconds = microseconds // 1000000
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    if hours:
        return f"{hours:02d}h{minutes:02d}min{remaining_seconds:02d}s"
    elif minutes:
        return f"{minutes}min{remaining_seconds:02d}s"
    else:
        return f"{remaining_seconds:02d}s"


# ? Formations
def formations_view(request):
    user_id = request.session.get('user_id', None)
    search_query = request.GET.get('search', '')

    current_view_name = request.resolver_match.url_name
    context = {'title': 'Formations', 'current_view_name': current_view_name}

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT course, course_description, logo_url, SUM(duration), title, COUNT(*)
            FROM videos_videos 
            WHERE category = 'formation' AND LOWER(course) LIKE LOWER(%s)
            GROUP BY course, course_description, logo_url
        """, ['%' + search_query + '%'])
        all_formation = cursor.fetchall()

    if user_id is not None:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM account_user WHERE id = %s", [user_id])
            user = cursor.fetchone()

        context['user'] = user
        context["image_url"] = context["user"][13].replace(
            'static/', '')

    all_formation = [
        (course, course_description, logo_url.replace('videos/static/', ''), convert_microseconds_to_time(duration),
         title, count)
        for course, course_description, logo_url, duration, title, count in
        all_formation]

    context["all_formation"] = all_formation

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(all_formation, safe=False)

    return render(request, 'formations.html', context)


# ? PlayList Formations
def playlist_formations_view(request, course, selected_slug=None):
    user_id = request.session.get('user_id', None)

    current_view_name = request.resolver_match.url_name
    context = {'title': 'Formations Playlist',
               'current_view_name': current_view_name}

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT title, youtube_video_id, description, duration, miniature, access, slug
            FROM videos_videos
            WHERE course = %s AND category = "formation"
        """, [course])
        formation_videos = cursor.fetchall()

    total_duration = sum(video[3] for video in formation_videos)
    hours = total_duration // 3600000000
    minutes = (total_duration % 3600000000) // 60000000
    seconds = (total_duration % 60000000) // 1000000

    context["total_duration"] = f"{hours}h{minutes}min{
        seconds}s" if hours else f"{minutes}min{seconds}s"
    context["total_lessons"] = len(formation_videos)
    context["course_title"] = course

    formation_videos = [
        {
            'id': str(index),
            'title': video[0],
           
            'name': f"https://youtu.be/{video[1]}",
            # 'name': video[1].replace('videos/static/medias/videos/', ''),
            'duration': str(video[3] // 60000000) + ':' + str((video[3] // 1000000) % 60).zfill(2),
            'thumbnail': video[4].replace('videos/static/', ''),
            'access': video[5],
            'slug': video[6]
        }
        for index, video in enumerate(formation_videos, start=1)
    ]

    print(formation_videos)
    context["default_thumbnail"] = formation_videos[0]['thumbnail']

    # print(context["default_thumbnail"])
    context["playlist"] = json.dumps(formation_videos)

    # print(context["playlist"])

    if user_id is not None:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM account_user WHERE id = %s", [user_id])
            user = cursor.fetchone()

            cursor.execute(
                "SELECT is_premium FROM account_apprenant WHERE user_id = %s", [user_id])

            apprenant = cursor.fetchone()

            print(f"data: {apprenant}")

        context["is_premium"] = apprenant[0]
        context['user'] = user
        context["image_url"] = context["user"][13].replace(
            'static/', '')

    # print(context["user"][-1])

    return render(request, 'playlist_formations.html', context)


# ? Tutoriels
def tutoriels_view(request):
    user_id = request.session.get('user_id', None)
    search_query = request.GET.get('search', '')

    current_view_name = request.resolver_match.url_name
    context = {'title': 'Tutoriels', 'current_view_name': current_view_name}

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT title, description, logo_url, duration, niveau, course, slug
            FROM videos_videos 
            WHERE category = 'tutoriel' AND (LOWER(title) LIKE LOWER(%s) OR LOWER(course) LIKE LOWER(%s))
        """, ['%' + search_query + '%', '%' + search_query + '%'])
        all_tutorial = cursor.fetchall()

    if user_id is not None:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM account_user WHERE id = %s", [user_id])
            user = cursor.fetchone()

        context['user'] = user
        context["image_url"] = context["user"][13].replace(
            'static/', '')

    all_tutorial = [
        (title, description, logo_url.replace('videos/static/', ''), convert_microseconds_to_time(duration),
         niveau.capitalize(), course, slug)
        for title, description, logo_url, duration, niveau, course, slug in
        all_tutorial]

    context["all_tutorial"] = all_tutorial

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(all_tutorial, safe=False)

    return render(request, 'tutoriels.html', context)


# ? PlayList Tutoriel
def playlist_tutorial_view(request, course, selected_slug):
    user_id = request.session.get('user_id', None)

    current_view_name = request.resolver_match.url_name
    context = {'title': 'Tutoriels Playlist',
               'current_view_name': current_view_name}

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT title, youtube_video_id, description, duration, miniature, access, slug, course
            FROM videos_videos
            WHERE category = %s AND course = %s
        """, ["tutoriel", course])
        tutoriels_videos = cursor.fetchall()

    print(f"Playlist Tuto: {tutoriels_videos}")

    if not tutoriels_videos:
        return redirect('tutoriels')

    # context["playlist"] = formation_videos

    total_duration = sum(video[3] for video in tutoriels_videos)
    hours = total_duration // 3600000000
    minutes = (total_duration % 3600000000) // 60000000
    seconds = (total_duration % 60000000) // 1000000

    context["total_duration"] = f"{hours}h{minutes}min{
        seconds}s" if hours else f"{minutes}min{seconds}s"
    context["total_lessons"] = len(tutoriels_videos)
    # context["course_title"] = course

    # context['thumbnail']: miniature.replace('videos/static/medias/miniatures/', '')

    tutoriel_videos = [
        {
            'id': str(index),
            'title': video[0],
            'name': f"https://youtu.be/{video[1]}",
            # 'name': video[1].replace('videos/static/medias/videos/', ''),
            'duration': str(video[3] // 60000000) + ':' + str((video[3] // 1000000) % 60).zfill(2),
            'thumbnail': video[4].replace('videos/static/', ''),
            'access': video[5],
            'slug': video[6]
        }
        for index, video in enumerate(tutoriels_videos, start=1)
    ]

    print(tutoriel_videos)
    context["default_thumbnail"] = tutoriel_videos[0]['thumbnail']

    # print(f"Selected Video: {context["selected_tutorial"]}")

    # print(context["default_thumbnail"])
    context["playlist"] = json.dumps(tutoriel_videos)

    # print(context["playlist"])

    if user_id is not None:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM account_user WHERE id = %s", [user_id])
            user = cursor.fetchone()

            cursor.execute(
                "SELECT is_premium FROM account_apprenant WHERE user_id = %s", [user_id])

            apprenant = cursor.fetchone()

            print(f"data: {apprenant}")

        context["is_premium"] = apprenant[0]
        context['user'] = user
        context["image_url"] = context["user"][13].replace(
            'static/', '')

    context["selected_slug"] = selected_slug
    # print(context["image_url"])
    selected_tutorial = [
        tutorial for tutorial in tutoriels_videos if tutorial[6] == selected_slug]
    if not selected_tutorial:
        # Si aucun tutoriel correspondant n'est trouvé, redirigez l'utilisateur vers la page des tutoriels
        return redirect('tutoriels')
    # print(context["user"][-1])

    return render(request, 'playlist_tutorials.html', context)


def search_suggestions_formations(request):
    search_query = request.GET.get('search', '')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT course
            FROM videos_videos 
            WHERE category = 'formation' AND LOWER(course) LIKE LOWER(%s)
            GROUP BY course
        """, ['%' + search_query + '%'])
        courses = cursor.fetchall()
    return JsonResponse(courses, safe=False)

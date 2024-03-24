from django.db import connection
from django.shortcuts import render


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


# ! Les Menu De Navigation
# ? Accueil
def index_view(request):
    user_id = request.session.get('user_id', None)
    user = None
    current_view_name = request.resolver_match.url_name
    context = {'title': 'Accueil', 'current_view_name': current_view_name}

    with connection.cursor() as cursor:
        cursor.execute("""
                SELECT course, course_description, logo_url, SUM(duration), title, COUNT(*), slug
                FROM videos_videos 
                WHERE category = 'formation'
                GROUP BY course, course_description, logo_url
                ORDER BY date DESC
                LIMIT 4
        """)
        all_formation = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT title, description, logo_url, duration, niveau, course, slug
            FROM videos_videos 
            WHERE category = 'tutoriel'
            ORDER BY date DESC
            LIMIT 4
            
        """)
        all_tutorial = cursor.fetchall()

    if user_id is not None:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM account_user WHERE id = %s", [user_id])
            user = cursor.fetchone()

        context['user'] = user
        context["image_url"] = context["user"][13].replace(
            'static/', '')
        
        print(context['user'])
        print(context['image_url'])

    all_formation = [
        (course, course_description, logo_url.replace('videos/static/', ''),
         convert_microseconds_to_time(duration), title, count, slug)
        for course, course_description, logo_url, duration, title, count, slug in
        all_formation]

    all_tutorial = [
        (title, description, logo_url.replace('videos/static/', ''), convert_microseconds_to_time(duration),
         niveau.capitalize(), course, slug)
        for title, description, logo_url, duration, niveau, course, slug in
        all_tutorial]

    context["all_formation"] = all_formation
    context["all_tutorial"] = all_tutorial

    return render(request, 'layouts/menu/index.html', context)


# ? Blog
def blog_view(request):
    user_id = request.session.get('user_id', None)

    current_view_name = request.resolver_match.url_name
    context = {'title': 'Blog', 'current_view_name': current_view_name}

    if user_id is not None:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM account_user WHERE id = %s", [user_id])
            user = cursor.fetchone()

        context['user'] = user
        context["image_url"] = context["user"][13].replace(
            'static/', '')

        print(context["image_url"])
    # print(context["user"][-1])

    return render(request, 'layouts/menu/blog.html', context)


# ? Contact
def contact_view(request):
    user_id = request.session.get('user_id', None)

    current_view_name = request.resolver_match.url_name
    context = {'title': 'Contact', 'current_view_name': current_view_name}

    if user_id is not None:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM account_user WHERE id = %s", [user_id])
            user = cursor.fetchone()

        context['user'] = user
        context["image_url"] = context["user"][13].replace(
            'static/', '')

        print(context["image_url"])
    # print(context["user"][-1])

    return render(request, 'layouts/menu/contact.html', context)

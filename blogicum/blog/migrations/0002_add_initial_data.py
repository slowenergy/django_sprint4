
from django.db import migrations

def create_initial_data(apps, schema_editor):
    Location = apps.get_model('blog', 'Location')
    Category = apps.get_model('blog', 'Category')
    
    # Создание начальных местоположений
    Location.objects.create(name='Москва')
    Location.objects.create(name='Санкт-Петербург')
    
    # Создание начальных категорий
    Category.objects.create(
        title='Технологии',
        description='Посты о технологиях',
        slug='tekhnologii'
    )
    Category.objects.create(
        title='Путешествия',
        description='Посты о путешествиях',
        slug='puteshestviya'
    )

class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_data),
    ]
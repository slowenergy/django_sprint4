# Generated by Django 3.2.16 on 2023-05-24 17:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0005_post_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="image",
            field=models.ImageField(
                blank=True, upload_to="img/", verbose_name="Изображение"
            ),
        ),
    ]
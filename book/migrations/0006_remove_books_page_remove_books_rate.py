# Generated by Django 4.2.13 on 2024-06-07 16:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0005_books_page_books_rate_favorite_bookrating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='books',
            name='page',
        ),
        migrations.RemoveField(
            model_name='books',
            name='rate',
        ),
    ]
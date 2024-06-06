# Generated by Django 4.2.13 on 2024-06-06 11:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pages',
            name='book_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='book.books'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='books',
            name='image',
            field=models.ImageField(upload_to='author/'),
        ),
        migrations.DeleteModel(
            name='BookPages',
        ),
    ]
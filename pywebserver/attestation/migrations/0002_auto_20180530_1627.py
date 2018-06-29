# Generated by Django 2.0.4 on 2018-05-30 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attestation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LinkNew',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pid', models.CharField(db_index=True, default='', max_length=26)),
                ('nmlid', models.CharField(default='', max_length=300)),
                ('entity', models.CharField(default='', max_length=300)),
                ('status', models.IntegerField(choices=[(0, 'Not yet determined'), (1, 'Match'), (2, 'No match'), (3, 'Unknown'), (4, 'Skip')], db_index=True, default=0)),
                ('kind', models.CharField(default='', max_length=300)),
                ('extras', models.CharField(default='', max_length=300)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='linknew',
            unique_together={('pid', 'nmlid')},
        ),
    ]
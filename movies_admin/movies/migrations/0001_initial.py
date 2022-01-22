# Generated by Django 4.0 on 2021-12-14 22:28

import uuid

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FilmWork",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=255, verbose_name="Название")),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                (
                    "creation_date",
                    models.DateField(blank=True, verbose_name="Дата выхода"),
                ),
                (
                    "certificate",
                    models.TextField(blank=True, verbose_name="Сертификат"),
                ),
                (
                    "file_path",
                    models.FileField(
                        blank=True, upload_to="film_works/", verbose_name="Файл"
                    ),
                ),
                (
                    "rating",
                    models.FloatField(
                        blank=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(10),
                        ],
                        verbose_name="Рейтинг",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[("movie", "Movie"), ("tv_show", "TV Show")],
                        max_length=20,
                        verbose_name="Тип",
                    ),
                ),
            ],
            options={
                "verbose_name": "Фильм",
                "verbose_name_plural": "Фильмы",
                "db_table": '"content"."film_work"',
            },
        ),
        migrations.CreateModel(
            name="Genre",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255, verbose_name="Жанр")),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
            ],
            options={
                "verbose_name": "Жанр",
                "verbose_name_plural": "Жанры",
                "db_table": '"content"."genre"',
            },
        ),
        migrations.CreateModel(
            name="Person",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "full_name",
                    models.CharField(max_length=255, verbose_name="Полное имя"),
                ),
                (
                    "birth_date",
                    models.DateField(blank=True, verbose_name="Дата рождения"),
                ),
            ],
            options={
                "verbose_name": "Участник",
                "verbose_name_plural": "Участники",
                "db_table": '"content"."person"',
            },
        ),
        migrations.CreateModel(
            name="PersonFilmWork",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("director", "Режисёр"),
                            ("producer", "Продюссер"),
                            ("operator", "Оператор"),
                            ("composer", "Композитор"),
                            ("actor", "Актёр"),
                            ("writer", "Сценарист"),
                        ],
                        max_length=60,
                        verbose_name="Должность",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "film_work_id",
                    models.ForeignKey(
                        db_column="film_work_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="movies.filmwork",
                    ),
                ),
                (
                    "person_id",
                    models.ForeignKey(
                        db_column="person_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="movies.person",
                    ),
                ),
            ],
            options={
                "verbose_name": "Участник фильма",
                "verbose_name_plural": "Участники фильмов",
                "db_table": '"content"."person_film_work"',
            },
        ),
        migrations.CreateModel(
            name="GenreFilmWork",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "film_work_id",
                    models.ForeignKey(
                        db_column="film_work_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="movies.filmwork",
                    ),
                ),
                (
                    "genre_id",
                    models.ForeignKey(
                        db_column="genre_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="movies.genre",
                    ),
                ),
            ],
            options={
                "verbose_name": "Жанр фильма",
                "verbose_name_plural": "Жанры фильмов",
                "db_table": '"content"."genre_film_work"',
            },
        ),
        migrations.AddField(
            model_name="filmwork",
            name="genres",
            field=models.ManyToManyField(
                related_name="filmworks",
                through="movies.GenreFilmWork",
                to="movies.Genre",
            ),
        ),
        migrations.AddField(
            model_name="filmwork",
            name="persons",
            field=models.ManyToManyField(
                related_name="filmworks",
                through="movies.PersonFilmWork",
                to="movies.Person",
            ),
        ),
        migrations.AddIndex(
            model_name="personfilmwork",
            index=models.Index(
                fields=["film_work_id", "person_id", "role"],
                name="film_work_person_role",
            ),
        ),
        migrations.AddIndex(
            model_name="genrefilmwork",
            index=models.Index(
                fields=["film_work_id", "genre_id"], name="film_work_genre"
            ),
        ),
    ]

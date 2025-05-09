from django.db import migrations

def create_profiles_for_existing_users(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('accounts', 'Profile')
    
    for user in User.objects.all():
        Profile.objects.get_or_create(
            user=user,
            defaults={
                'is_verified': user.is_superuser,
                'approved_posts_count': 0,
                'points': 0
            }
        )

def reverse_profiles_creation(apps, schema_editor):
    Profile = apps.get_model('accounts', 'Profile')
    Profile.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),  # Update this to your last migration
    ]

    operations = [
        migrations.RunPython(create_profiles_for_existing_users, reverse_profiles_creation),
    ] 
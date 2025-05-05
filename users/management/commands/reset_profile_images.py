from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Reset profile images for all users based on gender."

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # Loop through all users and reset profile images based on gender
        updated_count = 0
        for user in User.objects.all():
            # Determine which profile image to assign based on gender
            if user.gender == 'male':
                user.profile_image = 'profile_photos/man.png'
            elif user.gender == 'female':
                user.profile_image = 'profile_photos/woman.png'
            else:
                user.profile_image = 'profile_photos/default.png'
            
            # Save the changes
            user.save()
            updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully updated {updated_count} user profiles."))

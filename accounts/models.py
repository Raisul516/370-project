# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
import datetime

def get_current_datetime():
    return timezone.now()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    approved_posts_count = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    """create table accounts_profile (
    id int auto_increment primary key,
    user_id int not null unique,
    is_verified boolean default false,
    approved_posts_count int default 0,
    points int default 0,
    foreign key (user_id) references auth_user(id) on delete cascade
)"""

    class Meta:
        db_table = 'accounts_profile'
        app_label = 'accounts'

    def __str__(self):
        return f"{self.user.username}'s profile"

    def check_verification_eligibility(self):
        # Auto-verify if user has 10 or more approved posts
        if not self.is_verified and self.approved_posts_count >= 10:
            self.is_verified = True
            self.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Automatically verify admins
        Profile.objects.create(
            user=instance,
            is_verified=instance.is_superuser
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        # Automatically verify admins
        Profile.objects.create(
            user=instance,
            is_verified=instance.is_superuser
        )
    elif instance.is_superuser and not instance.profile.is_verified:
        # Ensure admin is always verified
        instance.profile.is_verified = True
        instance.profile.save()

class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'



class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Historicalevents(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
    ]
    
    CATEGORY_CHOICES = [
        ('political', 'Political'),
        ('scientific', 'Scientific'),
        ('cultural', 'Cultural'),
        ('military', 'Military'),
        ('other', 'Other'),
    ]


    #create table accounts_historicalevents (
    #id int auto_increment primary key,
    #eventdate date default current_date not null,
    #title varchar(255) unique not null,
    #submitted_by_id int null,
    #status varchar(10) default 'pending' not null,
    #rejection_reason text null,
    #points_awarded int default 0 not null,
    #source varchar(500) null,
    #created_at datetime default current_timestamp not null,
    #updated_at datetime default current_timestamp on update current_timestamp not null,
    
    #foreign key (submitted_by_id) references auth_user(id) on delete set null,
    #foreign key (reviewed_by_id) references auth_user(id) on delete set null,
    #foreign key (category) references accounts_category(id) on delete cascade,
    
    #index (eventdate) :

    # Required Fields
    eventdate = models.DateField(default=timezone.now)
    title = models.CharField(max_length=255, help_text="Title of the historical event")
    description = models.TextField(help_text="Detailed description of the event")
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='other',
        help_text="Category of the historical event"
    )
    location = models.CharField(max_length=100, help_text="Location where the event occurred")
    importance = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Importance level from 1 (low) to 10 (high)"
    )
    
    # Optional Fields
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_events'
    )
    
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_events'
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    rejection_reason = models.TextField(blank=True, null=True)
    points_awarded = models.IntegerField(default=0)
    source = models.URLField(max_length=500, blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Historical Event'
        verbose_name_plural = 'Historical Events'
        ordering = ['-eventdate', 'title']

    def __str__(self):
        return f"{self.title} ({self.eventdate.year})" if self.eventdate else self.title

    def clean(self):
        """Additional model-wide validation"""
        if self.eventdate:
            # Convert both to date objects for comparison
            current_date = timezone.now().date()
            event_date = self.eventdate
            if isinstance(event_date, datetime.datetime):
                event_date = event_date.date()
            if event_date > current_date:
                raise ValidationError("Event date cannot be in the future")
        
        if self.importance and (self.importance < 1 or self.importance > 10):
            raise ValidationError("Importance must be between 1 and 10")
    def get_vote_count(self, vote_type):
        """Returns the count of upvotes or downvotes."""
        return self.votes.filter(vote_type=vote_type).count()

    def process_vote(self, user, vote_type):
        """Handles voting logic for upvotes and downvotes."""
        from .models import HistoricalEventUpvote

        if not user.is_authenticated:
            raise PermissionError("User must be logged in to vote.")

        # Prevent users from voting on their own events
        if user == self.submitted_by:
            raise ValueError("You cannot vote on your own event.")

        # Get or create the vote
        vote, created = HistoricalEventUpvote.objects.get_or_create(
            user=user,
            historicalevent=self,
            defaults={"vote_type": vote_type},
        )

        if not created and vote.vote_type == vote_type:
            # Remove vote if the same vote is clicked again
            self.points_awarded -= 10 if vote_type == "upvote" else -10
            vote.delete()
            self.save()
            return "removed"

        elif not created:
            # Change existing vote (e.g., upvote -> downvote)
            if vote.vote_type == "upvote":
                self.points_awarded -= 10
            elif vote.vote_type == "downvote":
                self.points_awarded += 10

            # Update to the new vote type
            vote.vote_type = vote_type
            vote.save()

        # New vote
        self.points_awarded += 10 if vote_type == "upvote" else -10
        self.save()
        return "added"    

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('approval', 'Event Approved'),
        ('rejection', 'Event Rejected'),
        ('verification', 'Account Verified'),
        ('points', 'Points Awarded'),
    )
    #CREATE TABLE accounts_notification (
    #id INT AUTO_INCREMENT PRIMARY KEY,                            
    #is_read BOOLEAN NOT NULL DEFAULT FALSE,                         
    #created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,         
    #related_event_id INT NULL,                                      
    #FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE, 
    #FOREIGN KEY (related_event_id) REFERENCES accounts_historicalevents(id) );
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_event = models.ForeignKey(Historicalevents, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_type_display()} for {self.user.username}"
class HistoricalEventUpvote(models.Model):
    VOTE_CHOICES = [
        ('upvote', 'Upvote'),
        ('downvote', 'Downvote'),
    ]

    
    # create table accounts_historicalevents_upvotes (
    #id int auto_increment primary key,
    #accounts_historicalevents_id int not null,
    #accounts_profile int not null,
    #vote_type enum('upvote', 'downvote') not null default 'upvote',
    #foreign key (accounts_historicalevents_id) references accounts_historicalevents(id) on delete cascade,
    #foreign key (accounts_profile) references accounts_profile(id) on delete cascade,
    #unique key (accounts_historicalevents_id, accounts_profile) ;    
    historicalevent = models.ForeignKey(
        'Historicalevents', 
        on_delete=models.CASCADE,
        related_name='votes',
        db_column='accounts_historicalevents_id'
    )

    # This represents the user who is voting
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # This is the user casting the vote
        on_delete=models.CASCADE,
        db_column='accounts_profile'
    )

    # This stores the type of vote
    vote_type = models.CharField(
        max_length=10,
        choices=VOTE_CHOICES,
        default='upvote',
        db_column='vote_type'
    )

    class Meta:
        db_table = 'accounts_historicalevents_upvotes'
        unique_together = ('historicalevent', 'user')  # Ensure each user can only vote once per event    
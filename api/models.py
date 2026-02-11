
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# ==============================================================================
# UTILITIES & VALIDATORS
# ==============================================================================

def validate_file_size(value):
    """
    Validates that the file size is not negative and within reasonable limits (e.g., 5GB).
    """
    limit_gb = 5
    if value < 0:
        raise ValidationError(_('File size cannot be negative.'))
    if value > limit_gb * 1024 * 1024 * 1024:
        raise ValidationError(_(f'File size exceeds the limit of {limit_gb}GB.'))

def validate_hex_color(value):
    """
    Validates that the value is a valid HEX color code.
    """
    if not value.startswith('#') or len(value) not in [4, 7]:
        raise ValidationError(_('Invalid HEX color code.'))

# ==============================================================================
# MODELS
# ==============================================================================

class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created_at`` and ``updated_at`` fields.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        abstract = True


class Profile(TimeStampedModel):
    """
    Extends the default Django User model with additional profile information.
    """
    ROLE_CHOICES = [
        ('user', 'Regular User'),
        ('admin', 'Administrator'),
        ('developer', 'Developer'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True, verbose_name=_("Full Name"))
    avatar_url = models.URLField(max_length=500, blank=True, null=True, verbose_name=_("Avatar URL"))
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='user', verbose_name=_("Role"))
    bio = models.TextField(blank=True, verbose_name=_("Bio"))
    phone_number = models.CharField(max_length=20, blank=True, verbose_name=_("Phone Number"))
    is_verified = models.BooleanField(default=False, verbose_name=_("Is Verified"))
    preferences = models.JSONField(default=dict, blank=True, verbose_name=_("User Preferences"))

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} ({self.full_name or 'No Name'})"

    @property
    def email(self):
        return self.user.email

    @property
    def username(self):
        return self.user.username

    def is_admin(self):
        return self.role == 'admin'

    def is_developer(self):
        return self.role == 'developer'


class StorageCredential(TimeStampedModel):
    """
    Stores API credentials for external storage providers like ImageKit, Cloudinary, or S3.
    Sensitive keys are stored (ideally should be encrypted, handled here as text for simulation).
    """
    PROVIDER_CHOICES = [
        ('imagekit', 'ImageKit'),
        ('cloudinary', 'Cloudinary'),
        ('aws_s3', 'AWS S3'),
        ('google_drive', 'Google Drive'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='storage_credentials')
    name = models.CharField(max_length=255, verbose_name=_("Credential Name"))
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES, default='imagekit', verbose_name=_("Provider"))
    
    # Credentials
    public_key = models.CharField(max_length=255, verbose_name=_("Public Key / Access Key"))
    private_key_encrypted = models.TextField(verbose_name=_("Private Key (Encrypted)"))
    url_endpoint = models.URLField(max_length=500, verbose_name=_("URL Endpoint"))
    
    # Configuration
    region = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Region"))
    bucket_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Bucket Name"))
    
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    is_default = models.BooleanField(default=False, verbose_name=_("Is Default"))

    class Meta:
        verbose_name = _("Storage Credential")
        verbose_name_plural = _("Storage Credentials")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'provider']),
        ]

    def __str__(self):
        return f"{self.name} - {self.get_provider_display()}"

    def save(self, *args, **kwargs):
        # Ensure only one default credential per user per provider (optional logic)
        if self.is_default:
            StorageCredential.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class Category(TimeStampedModel):
    """
    Categories for organizing files.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=255, verbose_name=_("Category Name"))
    color = models.CharField(
        max_length=7, 
        default='#3B82F6', 
        validators=[validate_hex_color],
        verbose_name=_("Color Label")
    )
    icon = models.CharField(max_length=50, default='folder', verbose_name=_("Icon Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    sort_order = models.IntegerField(default=0, verbose_name=_("Sort Order"))
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['sort_order', 'name']
        unique_together = ['user', 'name']

    def __str__(self):
        return self.name

    @property
    def file_count(self):
        return self.files.count()


class File(TimeStampedModel):
    """
    Represents a file uploaded to an external storage provider.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    storage_account = models.ForeignKey(StorageCredential, on_delete=models.SET_NULL, null=True, blank=True, related_name='files')
    
    # File Metadata
    name = models.CharField(max_length=255, verbose_name=_("File Name"))
    original_name = models.CharField(max_length=255, blank=True, verbose_name=_("Original Filename"))
    url = models.URLField(max_length=1000, verbose_name=_("File URL"))
    thumbnail_url = models.URLField(max_length=1000, blank=True, null=True, verbose_name=_("Thumbnail URL"))
    file_type = models.CharField(max_length=100, verbose_name=_("MIME Type"))
    extension = models.CharField(max_length=20, blank=True, verbose_name=_("File Extension"))
    size = models.BigIntegerField(validators=[validate_file_size], verbose_name=_("Size (Bytes)"))
    
    # Provider Info
    file_id = models.CharField(max_length=255, verbose_name=_("Provider File ID"))
    folder_path = models.CharField(max_length=255, default='/', verbose_name=_("Virtual Folder Path"))
    
    # Organization
    categories = models.ManyToManyField(Category, related_name='files', blank=True, verbose_name=_("Categories"))
    tags = models.JSONField(default=list, blank=True, verbose_name=_("Tags"))
    is_favorite = models.BooleanField(default=False, verbose_name=_("Is Favorite"))
    is_public = models.BooleanField(default=False, verbose_name=_("Is Public"))
    
    # Analytics
    download_count = models.IntegerField(default=0, verbose_name=_("Download Count"))
    last_accessed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Last Accessed"))

    class Meta:
        verbose_name = _("File")
        verbose_name_plural = _("Files")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'file_type']),
            models.Index(fields=['user', 'folder_path']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.extension and self.name:
            import os
            _, ext = os.path.splitext(self.name)
            self.extension = ext.lower().replace('.', '')
        super().save(*args, **kwargs)

    @property
    def size_formatted(self):
        """Returns size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if self.size < 1024.0:
                return f"{self.size:.2f} {unit}"
            self.size /= 1024.0
        return f"{self.size:.2f} PB"


class ActivityLog(models.Model):
    """
    Logs user activities for audit and history purposes.
    """
    ACTION_TYPES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('upload', 'File Upload'),
        ('delete', 'File Delete'),
        ('update', 'File Update'),
        ('create_category', 'Category Created'),
        ('api_key_generated', 'API Key Generated'),
        ('settings_update', 'Settings Updated'),
        ('other', 'Other Action'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES, default='other')
    description = models.CharField(max_length=255, verbose_name=_("Description"), default='')
    details = models.JSONField(default=dict, blank=True, verbose_name=_("Metadata"))
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("IP Address"))
    user_agent = models.TextField(blank=True, null=True, verbose_name=_("User Agent"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Activity Log")
        verbose_name_plural = _("Activity Logs")
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] {self.user.username}: {self.action_type}"


class ApiKey(TimeStampedModel):
    """
    API Keys for programmatic access (e.g., CI/CD, external scripts).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    name = models.CharField(max_length=255, verbose_name=_("Key Name"))
    key = models.CharField(max_length=255, unique=True, editable=False, verbose_name=_("API Key"))
    prefix = models.CharField(max_length=10, editable=False, verbose_name=_("Key Prefix"), default='')
    
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Last Used At"))
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Expires At"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    scopes = models.JSONField(default=list, blank=True, verbose_name=_("Scopes/Permissions"))

    class Meta:
        verbose_name = _("API Key")
        verbose_name_plural = _("API Keys")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.prefix}...)"

    def is_valid(self):
        if not self.is_active:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True


class ShareLink(TimeStampedModel):
    """
    Publicly shareable links for files or folders.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='share_links')
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='shares', null=True, blank=True)
    
    token = models.CharField(max_length=100, unique=True, verbose_name=_("Share Token"))
    password_hash = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Password Hash"))
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Expires At"))
    max_downloads = models.IntegerField(default=0, verbose_name=_("Max Downloads (0 for unlimited)"))
    current_downloads = models.IntegerField(default=0, verbose_name=_("Current Downloads"))
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Share Link")
        verbose_name_plural = _("Share Links")

    def __str__(self):
        return f"Share {self.token} for {self.file.name if self.file else 'Unknown'}"

    @property
    def url(self):
        return f"/s/{self.token}"


# ==============================================================================
# SIGNALS
# ==============================================================================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(post_save, sender=File)
def log_file_upload(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            user=instance.user,
            action_type='upload',
            description=f"Uploaded file: {instance.name}",
            details={'file_id': str(instance.id), 'size': instance.size}
        )

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

User = get_user_model()

class LaunchPromotion(models.Model):
    """Promociones especiales de lanzamiento"""
    
    PROMOTION_TYPES = [
        ('WELCOME_BONUS', 'Bono de Bienvenida'),
        ('FIRST_DEPOSIT', 'Bono Primer Depósito'),
        ('REFERRAL_BONUS', 'Bono por Referido'),
        ('DAILY_BONUS', 'Bono Diario'),
        ('LAUNCH_SPECIAL', 'Promoción de Lanzamiento'),
    ]
    
    name = models.CharField(max_length=100)
    promotion_type = models.CharField(max_length=20, choices=PROMOTION_TYPES)
    description = models.TextField()
    bonus_amount = models.DecimalField(max_digits=10, decimal_places=2)
    min_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_bonus = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    max_uses = models.IntegerField(null=True, blank=True, help_text="Máximo número de usos (null = ilimitado)")
    current_uses = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_promotion_type_display()}"
    
    def is_available(self):
        """Verifica si la promoción está disponible"""
        now = timezone.now()
        
        if not self.is_active:
            return False
            
        if self.start_date > now:
            return False
            
        if self.end_date and self.end_date < now:
            return False
            
        if self.max_uses and self.current_uses >= self.max_uses:
            return False
            
        return True
    
    def can_user_claim(self, user):
        """Verifica si un usuario puede reclamar esta promoción"""
        if not self.is_available():
            return False
            
        # Verificar si el usuario ya reclamó esta promoción
        if UserPromotion.objects.filter(user=user, promotion=self).exists():
            return False
            
        return True

class UserPromotion(models.Model):
    """Promociones reclamadas por usuarios"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='claimed_promotions')
    promotion = models.ForeignKey(LaunchPromotion, on_delete=models.CASCADE)
    bonus_amount = models.DecimalField(max_digits=10, decimal_places=2)
    claimed_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.promotion.name}"

class ReferralProgram(models.Model):
    """Sistema de referidos"""
    
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referred_by')
    referral_code = models.CharField(max_length=20, unique=True)
    bonus_amount = models.DecimalField(max_digits=10, decimal_places=2, default=5.00)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.referrer.username} -> {self.referred_user.username}"

class LaunchAchievement(models.Model):
    """Logros especiales de lanzamiento"""
    
    ACHIEVEMENT_TYPES = [
        ('PIONEER', 'Pionero - Primeros 100 usuarios'),
        ('FOUNDER', 'Fundador - Usuario del primer día'),
        ('CHAMPION', 'Campeón Inaugural - Ganador del primer torneo'),
        ('EARLY_BIRD', 'Madrugador - Primeros 10 usuarios'),
        ('SOCIAL_BUTTERFLY', 'Mariposa Social - Invitó 5 amigos'),
    ]
    
    name = models.CharField(max_length=100)
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='fas fa-trophy')
    bonus_credits = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    max_recipients = models.IntegerField(null=True, blank=True)
    current_recipients = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def can_award(self):
        """Verifica si se puede otorgar este logro"""
        if not self.is_active:
            return False
            
        if self.max_recipients and self.current_recipients >= self.max_recipients:
            return False
            
        return True

class UserAchievement(models.Model):
    """Logros otorgados a usuarios"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(LaunchAchievement, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)
    bonus_credits = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"

from django.contrib import admin
from cs.models import *
# Register your models here.


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name','email','subscribedate','playing','score','level')
admin.site.register(Player, PlayerAdmin)

admin.site.register(Category)

class BattleAdmin(admin.ModelAdmin):
    list_display = ('name','category','level','encounters')
admin.site.register(Battle, BattleAdmin)

class EncounterAdmin(admin.ModelAdmin):
    list_display = ('name', 'player1_name', 'player2_name', 'created', 'battle')
admin.site.register(Encounter, EncounterAdmin)


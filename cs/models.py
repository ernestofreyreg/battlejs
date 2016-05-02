import uuid
from datetime import timedelta
from django.db import models

# Create your models here.
from django.db.models import Q
from django.utils import timezone
from cs.emails import send_wellcome_email, send_award_email, send_challenge_email, send_challenge_completion_email, \
    send_win_email, send_lose_email, send_no_winner_email
from csmail.settings import MAX_LEVEL

UNKNOW_PLAYER = "UNKNOW"


def timedelta_format(td):
    mins = td.seconds / 60
    sec = td.seconds % 60
    return "%02dm %02ds"%(mins, sec)

class Player(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=100)
    subscribedate = models.DateField()
    playing = models.BooleanField(default=True)
    score = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    authtoken = models.CharField(max_length=100, null=True, blank=True, default='')

    def __unicode__(self):
        return u"%s - %s"%(self.name, self.email)

    class Meta:
        verbose_name = "Player"
        verbose_name_plural = "Players"

    def avatar(self):
        return "%d.png"%(self.id%39)

    def avatar_number(self):
        return self.id%39

    def badges(self):
        return xrange(1, self.level+1)

    def encounters(self):
        a = []
        for x in self.player1.all():
            if x.player1notified and x.player1_time().seconds==0 and x.submission1created==None:
                x.player1expired = True
            if x.player2notified and x.player2_time().seconds==0 and x.submission2created==None:
                x.player2expired = True
            x.save()

            if x.player1expired:
                if x.player2==None:
                    x.delete()
                    continue
                elif x.player2!=None and x.player2expired:
                    x.closed = True
                    x.save()


            a.append({
                "against": x.player2.name if x.player2 else UNKNOW_PLAYER,
                "category": x.battle.category,
                "result": x.winner_id == self.id,
                'against_avatar': x.player2.avatar_number() if x.player2 else 39,
                "against_level": x.player2.level if x.player2 else "?",
                "id": x.id,
                "remaining_time": timedelta_format(x.player1_time()),
                "remaining_time_seconds": x.player1_time(),
                "player_no": 1 if x.player1 == self else 2,
                "expired": x.player1expired,
                "closed": x.closed,
                "mutually_expired": x.player1expired and x.player2expired,
                "waiting_results": x.submission1created!=None and x.submission2created==None,
                "waiting": not x.closed and x.submission1created and x.submission2created
            })

        for x in self.player2.all():
            if x.player1notified and x.player1_time().seconds==0 and x.submission1created==None:
                x.player1expired = True
            if x.player2notified and x.player2_time().seconds==0 and x.submission2created==None:
                x.player2expired = True
            x.save()

            if x.player2expired:
                if x.player1==None:
                    x.delete()
                    continue
                elif x.player1!=None and x.player1expired:
                    x.closed = True
                    x.save()


            a.append({
                "against": x.player1.name if x.player1 else UNKNOW_PLAYER,
                "category": x.battle.category,
                "result": x.winner_id == self.id,
                'against_avatar': x.player1.avatar_number() if x.player1 else 39,
                "against_level": x.player1.level if x.player1 else "?",
                "id": x.id,
                "remaining_time": timedelta_format(x.player2_time()),
                "remaining_time_seconds": x.player2_time(),
                "player_no": 1 if x.player1 == self else 2,
                "expired": x.player2expired,
                "closed": x.closed,
                "mutually_expired": x.player1expired and x.player2expired,
                "waiting_results": x.submission2created!=None and x.submission1created==None,
                "waiting": not x.closed and x.submission1created and x.submission2created
            })

        return a

    def advance_level(self):
        self.level = self.level + 1
        self.save()
        send_award_email(self)

    def cannot_create_match(self):
        return Encounter.objects.filter(player1=self, closed=False).exists() or Encounter.objects.filter(player2=self, closed=False).exists()

    def play_now(self, online=False):
        # First remove mutually expired matches
        Encounter.objects.filter(Q(player1=self)|Q(player2=self)).filter(player1expired=True, player2expired=True).delete()

        # First Check for Empty games on my level
        if Encounter.objects.filter(player2=None, battle__level=self.level).exists():
            possibles = Encounter.objects.filter(player2=None, battle__level=self.level)

            match = None

            for encounter in possibles:
                if Encounter.objects.filter(player1=self,battle=encounter.battle).exists():
                    continue
                if Encounter.objects.filter(player2=self,battle=encounter.battle).exists():
                    continue
                match = encounter
                break

            if match:
                match.player2 = self
                match.save()

                if not online:
                    send_challenge_email(self, match.player1, match)

                send_challenge_completion_email(match.player1, self, match)

                return match


        # Did not found any previous Match, so, create a new one

        selected_battle = None

        while not selected_battle:
            for battle in Battle.objects.filter(level=self.level):
                if Encounter.objects.filter(player1=self, battle=battle).exists():
                    continue
                if Encounter.objects.filter(player2=self, battle=battle).exists():
                    continue
                selected_battle = battle
                break

            if not selected_battle:
                # Advanced a level after completing every level
                self.advance_level()

                if self.level > MAX_LEVEL:
                    break

        # Play as Player 1 against Unknow

        if not selected_battle:
            return None

        match = Encounter(
            battle = selected_battle,
            created = timezone.now(),

            player1 = self,
            player2 = None,

            player1notified = None,
            player2notified = None,

            submission1 = None,
            submission2 = None,

            submission1created = None,
            submission2created = None,

            passedtests1 = False,
            passedtests2 = False,

            winner = None,
            pointsawarded = 0,

            closed = False,

            submission1testtime = 0,
            submission2testtime = 0
        )

        match.save()

        if not online:
            send_challenge_email(self, None, match)

        return match






class Category(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

class Battle(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category)
    description = models.TextField()
    level = models.IntegerField()
    visibletests = models.TextField()
    invisibletests = models.TextField()
    maxtime = models.IntegerField(default=0)

    def __unicode__(self):
        return u"%s - %s"%(self.name, self.category.name)

    class Meta:
        verbose_name = "Battle"
        verbose_name_plural = "Battles"

    def encounters(self):
        return self.encounter_set.count()

    def visibletests_html(self):
        return ", ".join(self.visibletests.splitlines())

class Encounter(models.Model):
    battle = models.ForeignKey(Battle)
    created = models.DateTimeField()

    player1 = models.ForeignKey(Player, related_name='player1', null=True, blank=True)
    player2 = models.ForeignKey(Player, related_name='player2', null=True, blank=True)

    player1notified = models.DateTimeField(null=True, blank=True)
    player2notified = models.DateTimeField(null=True, blank=True)

    submission1 = models.TextField(null=True, blank=True)
    submission2 = models.TextField(null=True, blank=True)

    submission1created = models.DateTimeField(null=True, blank=True)
    submission2created = models.DateTimeField(null=True, blank=True)

    passedtests1 = models.BooleanField(default=False)
    passedtests2 = models.BooleanField(default=False)

    winner = models.ForeignKey(Player, related_name='winner', null=True, blank=True)
    pointsawarded = models.IntegerField(default=0)

    closed = models.BooleanField(default=False)

    submission1testtime = models.IntegerField(default=0)
    submission2testtime = models.IntegerField(default=0)

    player1expired = models.BooleanField(default=False)
    player2expired = models.BooleanField(default=False)

    def name(self):
        return self.__unicode__()

    def __unicode__(self):
        if self.player2 != None:
            return u"Battle %d %s vs %s"%(self.id, self.player1.name, self.player2.name)
        else:
            return u"Battle %d %s vs [RANDOM PLAYER]"%(self.id, self.player1.name)

    class Meta:
        verbose_name = "Encounter"
        verbose_name_plural = "Encounters"

    def player1_name(self):
        if self.player1:
            return self.player1
        return "RANDOM"

    def player2_name(self):
        if self.player2:
            return self.player2
        return "RANDOM"

    def player1_wins(self):
        self.closed = True
        self.winner = self.player1
        self.pointsawarded = 1
        self.save()

        winner = self.player1
        winner.score = winner.score + 1
        winner.save()

        send_win_email(self, 1)
        send_lose_email(self, 2)

    def player2_wins(self):
        self.closed = True
        self.winner = self.player2
        self.pointsawarded = 1
        self.save()

        winner = self.player2
        winner.score = winner.score + 1
        winner.save()

        send_win_email(self, 2)
        send_lose_email(self, 1)

    def no_winner(self):
        self.closed = True
        self.winner = None
        self.pointsawarded = 0
        self.save()
        send_no_winner_email(self, 1)
        send_no_winner_email(self, 2)

    def perform_checks(self):

        if self.submission1created and self.submission2created:

            # No one passes NO WINNER
            if not self.passedtests1 and not self.passedtests2:
                self.no_winner()

            # Player 2 WON
            if not self.passedtests1 and self.passedtests2:
                self.player2_wins()

            # Player 1 WON
            if not self.passedtests2 and self.passedtests1:
                self.player1_wins()

            # Both passes
            if self.passedtests1 and self.passedtests2:

                # First decide by lambda test times
                if self.submission1testtime < self.submission2testtime:
                    self.player1_wins()
                elif self.submission1testtime > self.submission2testtime:
                    self.player2_wins()
                else:

                    # Submission Time (Problem solving)
                    if self.player1_time().seconds < self.player2_time().seconds:
                        self.player1_wins()
                    elif self.player2_time().seconds < self.player1_time().seconds:
                        self.player2_wins()
                    else:
                        self.no_winner()
            return

        # Expires
        # Player 2 expires
        if self.submission1created and self.player2expired:
            if self.passedtests1:
                self.player1_wins()
            else:
                self.no_winner()

        # Player 1 expires
        if self.submission2created and self.player1expired:
            if self.passedtests2:
                self.player2_wins()
            else:
                self.no_winner()




    def player1_time(self):
        if (timezone.now() - self.player1notified).seconds > timedelta(seconds=self.battle.maxtime * 60).seconds:
            return timedelta(seconds=0)

        rigth_now = timedelta(seconds=self.battle.maxtime * 60) - (timezone.now() - self.player1notified)

        return rigth_now

    def player2_time(self):
        if (timezone.now() - self.player2notified).seconds > timedelta(seconds=self.battle.maxtime * 60).seconds:
            return timedelta(seconds=0)

        rigth_now = timedelta(seconds=self.battle.maxtime * 60) - (timezone.now() - self.player2notified)

        return rigth_now














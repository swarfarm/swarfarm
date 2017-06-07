from celery import shared_task
from datetime import datetime, timezone, timedelta

from django.contrib.auth.models import User
from django.core import mail


@shared_task
def warn_inactive_users():
    # Send an email to user accounts which are due to have their accounts deleted
    warn_threshold = datetime.now(timezone.utc) - timedelta(weeks=4 * 6 - 1)
    death_row = User.objects.filter(last_login__lte=warn_threshold)[:100]  # Limit quantity of users. Task is called frequently.

    subject = 'SWARFARM - Inactive Account Deletion Warning'
    body = (
        "Hello {},\n\n"
        "Your SWARFARM account has been inactive for almost 6 months! "
        "After 6 months of inactivity, your account will be automatically deleted. "
        "This will result in all of your monsters, teams, runes, and notes being permanently erased. "
        "If you wish to prevent this, simply go to swarfarm.com and log in.\n\n"
        "-SWARFARM"
    )

    # Construct the individual messages
    emails = []
    for user in death_row:
        emails.append((
            subject,
            body.format(user.username),
            'noreply@swarfarm.com',
            [user.email]
        ))

    mail.send_mass_mail(emails)


@shared_task
def delete_inactive_users():
    # Remove any user inactive for 6+ months
    delete_threshold = datetime.now(timezone.utc) - timedelta(weeks=4 * 6)
    death_row = User.objects.filter(last_login__lte=delete_threshold)[:100]  # Limit quantity of users. Task is called frequently.

    for user in death_row:
        # Unassociate all logs related to this user, if any
        user.summoner.summonlog_set.update(summoner=None)
        user.summoner.runlog_set.update(summoner=None)
        user.summoner.riftdungeonlog_set.update(summoner=None)
        user.summoner.runecraftlog_set.update(summoner=None)
        user.summoner.shoprefreshlog_set.update(summoner=None)
        user.summoner.worldbosslog_set.update(summoner=None)
        user.summoner.riftraidlog_set.update(summoner=None)
        user.summoner.wishlog_set.update(summoner=None)

        user.delete()

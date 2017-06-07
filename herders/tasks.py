from celery import shared_task
from datetime import datetime, timezone, timedelta

from django.contrib.auth.models import User
from django.core import mail


@shared_task
def delete_inactive_users():
    # Remove any user inactive for 6+ months
    delete_threshold = datetime.now(timezone.utc) - timedelta(weeks=4 * 6)
    death_row = User.objects.filter(last_login__lte=delete_threshold)[:100]  # Limit quantity of users. Task is called frequently.

    emails = []
    subject = 'SWARFARM - Inactive Account Deleted'
    body = (
        "Hello {},\n\n"
        "Your SWARFARM account has been inactive for 6 months or more! "
        "Due to this, your account has been deleted along with all associated data.\n\n" 
        "-SWARFARM"
    )
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

        emails.append((
            subject,
            body.format(user.username),
            'noreply@swarfarm.com',
            [user.email]
        ))

        user.delete()

    # Notify of account deletion
    mail.send_mass_mail(emails)

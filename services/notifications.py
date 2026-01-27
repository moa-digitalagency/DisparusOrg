"""
 * Nom de l'application : DISPARUS.ORG
 * Description : Service de notifications
 * Produit de : MOA Digital Agency, www.myoneart.com
 * Fait par : Aisance KALONJI, www.aisancekalonji.com
 * Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
def send_notification(notification_type, recipient, data):
    pass


def send_email_notification(to_email, subject, body):
    pass


def send_sms_notification(phone_number, message):
    pass


def notify_new_contribution(disparu, contribution):
    if disparu.contacts:
        for contact in disparu.contacts:
            if contact.get('email'):
                send_email_notification(
                    contact['email'],
                    f"Nouvelle contribution pour {disparu.first_name} {disparu.last_name}",
                    f"Une nouvelle contribution a ete ajoutee pour {disparu.first_name} {disparu.last_name}."
                )
            if contact.get('phone'):
                send_sms_notification(
                    contact['phone'],
                    f"Nouvelle contribution pour {disparu.first_name} {disparu.last_name} sur disparus.org"
                )


def notify_person_found(disparu):
    if disparu.contacts:
        for contact in disparu.contacts:
            if contact.get('email'):
                send_email_notification(
                    contact['email'],
                    f"BONNE NOUVELLE: {disparu.first_name} {disparu.last_name} a ete retrouve(e)",
                    f"{disparu.first_name} {disparu.last_name} a ete retrouve(e)! Consultez disparus.org pour plus de details."
                )

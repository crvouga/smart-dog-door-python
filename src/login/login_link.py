from datetime import datetime, timedelta


class LoginLink:

    @staticmethod
    def to_requested_at_utc_iso(login_link: dict) -> datetime:
        return datetime.fromisoformat(login_link["login_link__requested_at_utc_iso"])

    @staticmethod
    def to_age(login_link: dict) -> timedelta:
        link_age = datetime.now() - LoginLink.to_requested_at_utc_iso(login_link)
        return link_age

    @staticmethod
    def is_expired(login_link: dict) -> bool:
        link_age = LoginLink.to_age(login_link)
        is_expired = link_age > timedelta(minutes=10)
        return is_expired

    @staticmethod
    def is_used(login_link: dict) -> bool:
        used_at_utc_iso = login_link["login_link__used_at_utc_iso"]
        return used_at_utc_iso is not None

# import mailer
# from mailer.report import Report

from Library.Utility import HTML
from Library.Logging import VerboseLevel, ReportLoggingAPI, WebLoggingAPI

class EmailLoggingAPI(ReportLoggingAPI, WebLoggingAPI):

    _email_title_: str = None
    _email_from_address_: str = None
    _email_to_addresses_: list[str] | str = None
    _email_cc_addresses_: list[str] | str = None
    _email_default_address_ = "lisbon.eqd.exo.monitoring@bnpparibas.com"
    _email_download_hyperlink_: str = None

    @classmethod
    def _setup_class_(cls) -> None:
        super()._setup_class_()
        # cls.set_email_from_address(from_address=cls.user_info.email)
        cls.set_email_to_addresses(to_addresses=[cls._email_default_address_])
        # cls.set_email_cc_addresses(cc_addresses=[cls.user_info.email])

    @classmethod
    def set_email_title(cls, title: str) -> None:
        with cls._class_lock_:
            if cls.is_entered(): return
            cls._email_title_ = title

    @classmethod
    def set_email_from_address(cls, from_address: str) -> None:
        with cls._class_lock_:
            if cls.is_entered(): return
            cls._email_from_address_ = from_address

    @classmethod
    def set_email_to_addresses(cls, to_addresses: list[str] | str) -> None:
        with cls._class_lock_:
            if cls.is_entered(): return
            cls._email_to_addresses_ = to_addresses

    @classmethod
    def set_email_cc_addresses(cls, cc_addresses: list[str] | str) -> None:
        with cls._class_lock_:
            if cls.is_entered(): return
            cls._email_cc_addresses_ = cc_addresses

    @classmethod
    def set_email_download_hyperlink(cls, download_hyperlink: str) -> None:
        with cls._class_lock_:
            if cls.is_entered(): return
            cls._email_download_hyperlink_ = download_hyperlink

    @classmethod
    def output(cls, verbose: VerboseLevel, log: str) -> None:
        mailer.send(
            subject=verbose.name,
            from_=cls._email_from_address_,
            to=cls._email_to_addresses_,
            cc=cls._email_cc_addresses_,
            content=log
        )

    @classmethod
    def _exit_(cls):
        if cls.is_success_report():
            result_tag = cls._FAILURE_TAG_
            result_color = "red"
        elif cls.is_failure_report():
            result_tag = cls._SUCCESS_TAG_
            result_color = "green"
        else: return

        if not cls._email_title_: return
        if not cls._email_from_address_: return
        if not cls._email_to_addresses_: return
        if not cls._email_cc_addresses_: return
        if not cls._email_download_hyperlink_: return

        threshold_tag = f"[Threshold = {cls._class_verbose_threshold_.name}]"
        execution_tag = f"[{cls._host_info_} - {cls._exec_info_} - {cls._path_info_}]"
        timestamp_tag = f"[{cls.timestamp()}]"
        time_tag = f"[{cls.class_timer.result()}]"
        title = " @ ".join([result_tag, execution_tag, timestamp_tag]) if not cls._email_title_ else cls._email_title_

        r = Report()
        r.append(HTML.div(content=result_tag, font_size="10pt", font_weight="bold", font_color=result_color, font_family="Consolas"))
        r.append(HTML.div(content=threshold_tag, font_size="10pt", font_weight="bold", font_family="Consolas"))
        r.append(HTML.blank_line())
        r.append(HTML.div(content=execution_tag, font_size="10pt", font_weight="bold", font_family="Consolas"))
        r.append(HTML.div(content=timestamp_tag, font_size="10pt", font_weight="bold", font_family="Consolas"))
        r.append(HTML.div(content=time_tag, font_size="10pt", font_weight="bold", font_family="Consolas"))
        r.append(HTML.div(content=HTML.hyperlink(link=cls._email_download_hyperlink_, content="Download Log (S3)"), font_size="10pt", font_weight="bold", font_family="Consolas"))

        mailer.send(
            subject=title,
            from_=cls._email_from_address_,
            to=cls._email_to_addresses_,
            cc=cls._email_cc_addresses_,
            content=r.generate()
        )

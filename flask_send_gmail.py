# -*- coding: utf-8 -*-

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app

try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

class SendGmail(object):

    def __init__(self, app=None):
        self.app = app
        # support factory pattern
        if app is not None:
            self.init_app(app)

    def init_app(self, app):

        # assure proper config
        for k in ["SEND_GMAIL_USERNAME", "SEND_GMAIL_PASSWORD",]:
            if not k in current_app.config:
                raise ValueError("%s required in config."%k)

        # set a default gmail port if not configured
        if not "SEND_GMAIL_PORT" in current_app.config:
            current_app.config["SEND_GMAIL_PORT"] = 587

        if hasattr(app, "teardown_appcontext"):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

    def teardown(self, exception):
        current_app.logger.debug(exception)
        # cleanup - still unsure if this is going to actually do anything or
        # if it's satisfying the need for a placeholder. :-)
        # there is no further tidying needed for smtplib, so I think we're good.

    def address_okay(self, addr):
        # TODO decide how picky you want to be, here.
        return True

    def check_inputs(self, obj):

        # check for minimum inputs
        for req in ["Subject", "To", "From"]:

            if not req in obj["headers"]:
                raise ValueError("%s value required in obj['headers']."%req)

            if not isinstance(obj["headers"][req], list):
                raise ValueError("%s in obj['headers'] must be list."%req)

        # some sort of payload, please
        if not any(["text" in obj, "html" in obj]):
            raise ValueError("need at least one of 'text' or 'html' in obj")

        # assure email addresses are email addresses
        for addr in obj["To", "From", "Cc", "Bcc"]:
            if addr in obj["headers"]:
                if not self.address_ok(obj["headers"][addr]):
                    raise ValueError("%s not in recognized email format"%\
                            obj["headers"][addr])

        if len(obj["headers"]["Subject"]) > 130:
            current_app.logger.warning(
                    "Subject > 130 characters. Gmail will truncate!")

    def send(self, obj):
        """
        accept obj {dict} Requires "headers" object with minimum:
            "To" [list]
            "From" [list]
            containing one or more well formatted email addresses, and 
            "Subject" string with a suggested length of <= 130 characters. A
            longer subject will be truncated by gmail, and we'll be enablers
            and spit a warning in spite of RFC 2047.

        {
            headers: {
                "To": ["foo@foo.com"],
                "Cc": ["bar@foo.com", "bat@foo.com"],
                "Bcc": ["quux@foo.com"],
                "Subject: "Example Subject",
            },
            "text": "Example TEXT email.",
            "html": "<h1>Example</h1><p>HTML email.</p>",
        }
        """
        self.check_inputs(obj)

        message = MIMEMultipart("related")
        alternative = MIMEMultipart("alternative")
        message.attach(alternative)
        message.preamble = "This is a multi-part message in MIME format."
        
        # add headers values to message
        for k in in obj["headers"]:
            if isinstance(obj["headers"][k], list):
                message[k] = ", ".join(obj["headers"][k])
            else:
                "Subject is a string"
                message[k] = obj["headers"][k]

        if "text" in obj:
            text = MIMEText(obj["text"].encode("utf-8"), _charset="utf-8")
            alternative.attach(text)

        if "html" in obj: 
            html = MIMEText(
                    obj["html"].encode("utf-8"), "html", _charset="utf-8")
            alternative.attach(html)
        
        to_list = []
        for k in ["To", "Cc", "Bcc"]:
            to_list += obj["headers"].get(k, [])

        try:
            smtp = smtplib.SMTP(
                    "smtp.gmail.com", current_app.config["SEND_GMAIL_PORT"])
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(
                    current_app.config["SEND_GMAIL_USERNAME"],
                    current_app.config["SEND_GMAIL_PASSWORD"]
                    )
            smtp.sendmail(
                    obj["headers"]["From"],
                    to_list,
                    message.as_string()
                    )
            smtp.close()
        except Exception as error:
            current_app.logger.warning(error)
            return False
        return True

    @property
    def sender(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, "send_gmail"):
                ctx.send_gmail = self.send
            return ctx.send_gmail

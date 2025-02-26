# Copyright 2014 OpenMarket Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import urllib
from typing import TYPE_CHECKING, Dict, Optional

from sydent.db.valsession import ThreePidValSessionStore
from sydent.util import time_msec
from sydent.util.emailutils import sendEmail
from sydent.validators import common

if TYPE_CHECKING:
    from sydent.sydent import Sydent
    from sydent.validators import ValidationSession

logger = logging.getLogger(__name__)


class EmailValidator:
    def __init__(self, sydent: "Sydent") -> None:
        self.sydent = sydent

    def requestToken(
        self,
        emailAddress: str,
        clientSecret: str,
        sendAttempt: int,
        nextLink: str,
        ipaddress: Optional[str] = None,
        brand: Optional[str] = None,
    ) -> int:
        """
        Creates or retrieves a validation session and sends an email to the corresponding
        email address with a token to use to verify the association.

        :param emailAddress: The email address to send the email to.
        :param clientSecret: The client secret to use.
        :param sendAttempt: The current send attempt.
        :param nextLink: The link to redirect the user to once they have completed the
            validation.
        :param ipaddress: The requester's IP address.
        :param brand: A hint at a brand from the request.

        :return: The ID of the session created (or of the existing one if any)
        """
        valSessionStore = ThreePidValSessionStore(self.sydent)

        valSession = valSessionStore.getOrCreateTokenSession(
            medium="email", address=emailAddress, clientSecret=clientSecret
        )

        valSessionStore.setMtime(valSession.id, time_msec())

        templateFile = self.sydent.get_branded_template(
            brand,
            "verification_template.eml",
            ("email", "email.template"),
        )

        if int(valSession.sendAttemptNumber) >= int(sendAttempt):
            logger.info(
                "Not mailing code because current send attempt (%d) is not less than given send attempt (%s)",
                int(sendAttempt),
                int(valSession.sendAttemptNumber),
            )
            return valSession.id

        ipstring = ipaddress if ipaddress else "an unknown location"

        substitutions = {
            "ipaddress": ipstring,
            "link": self.makeValidateLink(valSession, clientSecret, nextLink),
            "token": valSession.token,
        }
        logger.info(
            "Attempting to mail code %s (nextLink: %s) to %s",
            valSession.token,
            nextLink,
            emailAddress,
        )
        sendEmail(self.sydent, templateFile, emailAddress, substitutions)

        valSessionStore.setSendAttemptNumber(valSession.id, sendAttempt)

        return valSession.id

    def makeValidateLink(
        self, valSession: "ValidationSession", clientSecret: str, nextLink: str
    ) -> str:
        """
        Creates a validation link that can be sent via email to the user.

        :param valSession: The current validation session.
        :param clientSecret: The client secret to include in the link.
        :param nextLink: The link to redirect the user to once they have completed the
            validation.

        :return: The validation link.
        """
        base = self.sydent.cfg.get("http", "client_http_base")
        link = "%s/_matrix/identity/api/v1/validate/email/submitToken?token=%s&client_secret=%s&sid=%d" % (
            base,
            urllib.parse.quote(valSession.token),
            urllib.parse.quote(clientSecret),
            valSession.id,
        )
        if nextLink:
            # manipulate the nextLink to add the sid, because
            # the caller won't get it until we send a response,
            # by which time we've sent the mail.
            if "?" in nextLink:
                nextLink += "&"
            else:
                nextLink += "?"
            nextLink += "sid=" + urllib.parse.quote(str(valSession.id))

            link += "&nextLink=%s" % (urllib.parse.quote(nextLink))
        return link

    def validateSessionWithToken(
        self, sid: int, clientSecret: str, token: str
    ) -> Dict[str, bool]:
        """
        Validates the session with the given ID.

        :param sid: The ID of the session to validate.
        :param clientSecret: The client secret to validate.
        :param token: The token to validate.

        :return: A dict with a "success" key which is True if the session
            was successfully validated, False otherwise.
        """
        return common.validateSessionWithToken(self.sydent, sid, clientSecret, token)

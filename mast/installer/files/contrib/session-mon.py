# -*- coding: utf-8 -*-
"""
session-mon.py

This is a special-case script written for an as-of-yet undiagnosed
problem where one user account is building up a tremendous number
of active logins. This script will look at ActiveUsers, and if one
account has more than 20 active sessions it will disconnect all
of their sessions.
"""
import mast.datapower.datapower as datapower
from mast.logging import make_logger
from itertools import groupby
from mast.cli import Cli


class UserSession(object):
    def __init__(self, node):
        """UserSession: A class representing an active user session
        on an IBM DataPower appliance.

        node must be an xml.etree.Element object representing the
        active login as returned by get-status("ActiveUsers")."""

        self.session_id      = node.find("session").text
        self.user            = node.find("name").text
        self.connection_type = node.find("connection").text
        self.ip_address      = node.find("address").text
        self.login_date      = node.find("address").text
        self.domain          = node.find("domain").text


def find_sessions(response_xml):
    xpath = "{}{}".format(datapower.STATUS_XPATH, "ActiveUsers")
    sessions = []
    for node in response_xml.findall(xpath):
        sessions.append(UserSession(node))
    return sessions


def get_users_with_sessions(sessions):
    return list(set([session.user for session in sessions]))


def get_users_session_ids(sessions, user):
    return [session.session_id for session in sessions if session.user == user]


def disconnect_all(appliance, user, ids):
    logger = make_logger("session_mon")
    for session_id in ids:
        resp = appliance.Disconnect(id=session_id)
        if resp:
            logger.debug(
                "Successfully disconnected {} - {} from {}".format(
                    user,
                    session_id,
                    appliance.hostname
                )
            )
        else:
            logger.error(
                "Failed to disconnect {} - {} from {}. Response: {}".format(
                    user,
                    session_id,
                    appliance.hostname,
                    repr(resp)
                )
            )


def main(appliances=[],
         credentials=[],
         no_check_hostname=False,
         max_sessions=20,
         timeout=120):
    logger = make_logger("session_mon")
    check_hostname = not no_check_hostname

    env = datapower.Environment(
        appliances,
        credentials,
        timeout,
        check_hostname=check_hostname)

    for appl in env.appliances:
        response = appl.get_status("ActiveUsers")
        sessions = find_sessions(response_xml=response.xml)
        logger.debug(
            "{} total active sessions found on {}".format(
                len(sessions), appl.hostname
            )
        )

        users = get_users_with_sessions(sessions)
        for user in users:
            users_sessions = get_users_session_ids(sessions, user)
            logger.debug(
                "user {} found with {} active sessions".format(
                    user, len(users_sessions)
                )
            )
            if len(users_sessions) > max_sessions:
                logger.info(
                    "user {} found with {} active sessions, this is greater than max, disconnecting.".format(
                        user, len(users_sessions)
                    )
                )
                disconnect_all(appl, user, users_sessions)


if __name__ == "__main__":
    try:
        cli = Cli(main=main)
        cli.run()
    except:
        logger = make_logger("error")
        logger.exception(
            "Sorry, an unhandled exception occurred "
            "during execution of log_user_out.py"
        )
        raise

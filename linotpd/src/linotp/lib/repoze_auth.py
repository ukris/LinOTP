# -*- coding: utf-8 -*-
#
#    LinOTP - the open source solution for two factor authentication
#    Copyright (C) 2010 - 2015 LSE Leading Security Experts GmbH
#
#    This file is part of LinOTP server.
#
#    This program is free software: you can redistribute it and/or
#    modify it under the terms of the GNU Affero General Public
#    License, version 3, as published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the
#               GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#    E-mail: linotp@lsexperts.de
#    Contact: www.linotp.org
#    Support: www.lsexperts.de
#
""" user authentication with repoze module """

import logging
log = logging.getLogger(__name__)

from linotp.lib.user import getRealmBox, getSplitAtSign
from linotp.lib.realm import getDefaultRealm
from linotp.lib.selftest import isSelfTest
from linotp.lib.util import str2unicode

import traceback

from linotp.lib.user import get_authenticated_user


class UserModelPlugin(object):

    def authenticate(self, environ, identity):
        log.info("[authenticate] entering repoze authenticate function.")
        # log.debug( identity )
        username = None
        realm = None
        authUser = None
        try:
            if isSelfTest():
                if ('login' not in identity and
                    'repoze.who.plugins.auth_tkt.userid' in identity):

                    uid = identity.get('repoze.who.plugins.auth_tkt.userid')
                    identity['login'] = uid
                    identity['password'] = uid

            if getRealmBox():
                username = identity['login']
                realm = identity['realm']
            else:
                log.info("[authenticate] no realmbox")
                if '@' in identity['login']:
                    if getSplitAtSign():
                        log.debug("trying to split the loginname")
                        username, _at_, realm = identity['login'].rpartition('@')
                    else:
                        log.debug("no split for the @ of the loginname")
                        username = identity['login']
                        realm = identity.get('realm', getDefaultRealm())

                else:
                    username = identity['login']
                    realm = getDefaultRealm()

            log.info("[authenticate]: username: %r, realm: %r"
                     % (username, realm))
            password = identity['password']

        except KeyError as e:
            log.error("[authenticate] Keyerror in identity: %r." % e)
            log.error("[authenticate] %s" % traceback.format_exc())
            return None

        # as repoze does not run through the std pylons middleware, we have to
        # convert the input which might be UTF8 to unicode
        username = str2unicode(username)
        password = str2unicode(password)

        # check username/realm, password
        if isSelfTest():
            authUser = "%s@%s" % (username, realm)
        else:
            authUser = get_authenticated_user(username, realm, password)

        return authUser

    def add_metadata(self, environ, identity):
        # username = identity.get('repoze.who.userid')
        # user = User.get(username)
        # user = "clerk maxwell"
        # log.info( "add_metadata: %s" % identity )

        # pp = pprint.PrettyPrinter(indent=4)
        # log.info("add_meta: environ %s" % pp.pformat(environ)
        log.debug("[add_metadata] add some metatata")
        # for k in environ.keys():
        #    log.debug("add_metadata: environ[%s]: %s" % ( k, environ[k] ))

        for k in identity.keys():
            log.debug("[add_metadata] identity[%s]: %s" % (k, identity[k]))

        # if identity.has_key('realm'):
        #    identity.update( { 'realm' : identity['realm'] } )
        #    log.info("add_metadata: added realm: %s" % identity['realm'] )

        return identity

# -*- coding: utf-8 -*-

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

def threePidAssocFromDict(d):
    assoc = ThreepidAssociation(d['medium'], d['address'], d['mxid'], d['ts'], d['not_before'], d['not_after'])
    return assoc

class ThreepidAssociation:
    def __init__(self, medium, address, mxid, ts, not_before, not_after):
        """
        :param medium: The medium of the 3pid (eg. email).
        :type medium: str
        :param address: The identifier (eg. email address).
        :type address: str
        :param mxid: The matrix ID the 3pid is associated with.
        :type mxid: str
        :param ts: The creation timestamp of this association, ms.
        :type ts: int
        :param not_before: The timestamp, in ms, at which this association
            becomes valid.
        :type not_before: int
        :param not_after: The timestamp, in ms, at which this association
            ceases to be valid.
        :type not_after: int
        """
        self.medium = medium
        self.address = address
        self.mxid = mxid
        self.ts = ts
        self.not_before = not_before
        self.not_after = not_after
        self.extra_fields = {}

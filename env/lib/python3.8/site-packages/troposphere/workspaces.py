# Copyright (c) 2015, Mark Peek <mark@peek.org>
# All rights reserved.
#
# See LICENSE file for full license.

from . import AWSObject, AWSProperty, Tags
from .validators import boolean, integer


class WorkspaceProperties(AWSProperty):
    props = {
        'ComputeTypeName': (str, False),
        'RootVolumeSizeGib': (integer, False),
        'RunningMode': (str, False),
        'RunningModeAutoStopTimeoutInMinutes': (integer, False),
        'UserVolumeSizeGib': (integer, False),
    }


class Workspace(AWSObject):
    resource_type = "AWS::WorkSpaces::Workspace"

    props = {
        'BundleId': (str, True),
        'DirectoryId': (str, True),
        'UserName': (str, True),
        'RootVolumeEncryptionEnabled': (boolean, False),
        'Tags': (Tags, False),
        'UserVolumeEncryptionEnabled': (boolean, False),
        'VolumeEncryptionKey': (str, False),
        'WorkspaceProperties': (WorkspaceProperties, False),
    }

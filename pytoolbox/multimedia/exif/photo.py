# -*- encoding: utf-8 -*-

#**********************************************************************************************************************#
#                                        PYTOOLBOX - TOOLBOX FOR PYTHON SCRIPTS
#
#  Main Developer : David Fischer (david.fischer.ch@gmail.com)
#  Copyright      : Copyright (c) 2012-2015 David Fischer. All rights reserved.
#
#**********************************************************************************************************************#
#
# This file is part of David Fischer's pytoolbox Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the EUPL v. 1.1 as provided
# by the European Commission. This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the European Union Public License for more details.
#
# You should have received a copy of the EUPL General Public License along with this project.
# If not, see he EUPL licence v1.1 is available in 22 languages:
#     22-07-2013, <https://joinup.ec.europa.eu/software/page/eupl/licence-eupl>
#
# Retrieved from https://github.com/davidfischer-ch/pytoolbox.git

from __future__ import absolute_import, division, print_function, unicode_literals

import inspect

from ... import module

_all = module.All(globals())


class Photo(object):

    @staticmethod
    def clean_number(number):
        return number if number and number > 0 else None

    def __init__(self, metadata):
        self.metadata = metadata

    @property
    def aperture(self):
        return self.clean_number(self.metadata.exiv2.get_fnumber())

    @property
    def date(self):
        return self.metadata.get_date()

    @property
    def exposure_time(self):
        return self.metadata.exiv2.get_exposure_time() or None

    @property
    def focal_length(self):
        return self.clean_number(self.metadata.exiv2.get_focal_length())

    @property
    def height(self):
        return self.metadata.exiv2.get_pixel_height() or None

    @property
    def iso(self):
        return self.metadata.exiv2.get_iso_speed() or None

    @property
    def orientation(self):
        orientation = self.metadata.exiv2.get_orientation()
        return orientation.value_nick if orientation else None

    @property
    def width(self):
        return self.metadata.exiv2.get_pixel_width() or None

    def properties(self):
        return ((n, getattr(self, n)) for n, p in inspect.getmembers(self.__class__, lambda m: isinstance(m, property)))

__all__ = _all.diff(globals())

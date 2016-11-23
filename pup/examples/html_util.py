#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2016 Dirk Toewe
#
# This file is part of PUP.
#
# PUP is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# PUP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with PUP. If not, see <http://www.gnu.org/licenses/>.

from tempfile import NamedTemporaryFile
import webbrowser

from pup.util.html_util import embed_file


def main():
  with NamedTemporaryFile(mode='w', delete=False, suffix='.html') as file:
    file.write(
      '''
      <!DOCTYPE html>
      <html lang="en">
        <head>
          <meta charset="utf-8" />
        </head>
        <body>
        {content}
        </body>
      </html>
      '''.format( content = embed_file('frankfurt_weather.csv', jszip='include') )
    )
    webbrowser.open('file://'+file.name)

if '__main__' == __name__:
  main()
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

from base64 import b64encode
import io
from uuid import uuid4
from zipfile import ZipFile, ZIP_DEFLATED

from pkg_resources import resource_string

import pup


_html_embed_file     = resource_string(__name__,"html_embed_file.template" ).decode('utf8')
_html_embed_file_zip = resource_string(__name__,"html_embed_file_zip.template").decode('utf8')
_jszip_min_js = (
    '<script type="text/javascript">\n'
  + resource_string(pup._plot_pandas.__name__,'jszip.min.js').decode('utf8')
  + '\n</script>'
)

def embed_file( file, name=None, text=None, jszip='include' ):
  '''
  Reads a file and returns an HTML div with the file embeded and attached to an a-tag
  as download link.

  Parameters
  ----------
  file: str
    The file to be embeded into HTML.
  name: str
    The name of the file on download.
  text: str
    The text displayed as download link.
  jszip: True, False or 'include':
    Specifies whether the file is zipped or included directly. If set to 'include', the
    JSZip library is embeded as well.

  Returns
  -------
  An HTML string containing with the file embeded.
  '''
  if None is name: name = file
  if None is text: text = name

  aid = uuid4()
    
  if False == jszip:

    with open(file,'rb') as file:
      b64str = b64encode( file.read() ).decode('utf8')

    return _html_embed_file.format( **locals() )

  else:

    jszip = _jszip_min_js if jszip == 'include' else ''

    b64str = io.BytesIO()
    with ZipFile(b64str,'w',compression=ZIP_DEFLATED) as zipFile:
      zipFile.write(file,name)
    b64str = b64encode( b64str.getvalue() ).decode('utf8')

    return _html_embed_file_zip.format( **locals() )


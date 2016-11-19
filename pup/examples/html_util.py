'''
Created on Nov 19, 2016

@author: dtitx
'''
from pup.util.html_util import embed_file
from tempfile import NamedTemporaryFile
import webbrowser

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
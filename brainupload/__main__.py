"""
Copyright 2017 Deepgram
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from deepgram import Brain
import argparse, os, time, urllib.parse, webbrowser, time
from glob import glob
FILE_TYPES = '.mp3 .3gp .aifc .mp4 .ogg .aif .wav .amr .flac .wmv .mpg .mkv .mp2 .mov .webm .3gpp .m4a .wma .aiff .aac .3ga .links'.split()


def loadLink(brainAPI, link):
  urlPath = urllib.parse.urlsplit(link)[2].strip()
  basename = os.path.basename(urlPath)
  print('Loading: {}'.format(basename))
  # We want to make this async so that we can let brain process while we load more assets
  assetId = brainAPI.createAssetFromURL(link, async=True, metadata={'filename': basename})['asset_id']
  return assetId, basename

def loadFile(brainAPI, path):
  basename = os.path.basename(path)
  print('Loading: {}'.format(basename))
  with open(path, mode='rb') as data:
    # We want to make this async so that we can let brain process while we load more assets
    assetId = brainAPI.uploadAsset(data, async=True, metadata={'filename': basename})['asset_id']
    return assetId, basename

def main():

  parser = argparse.ArgumentParser()
  parser.add_argument('-u', '--user', help='API user id', required=True)
  parser.add_argument('-t', '--token', help='API user token', required=True)
  parser.add_argument('-s', '--server', help='URL of the API server to use.')
  parser.add_argument('-f', '--file', help='Files or path to files to upload.', action='append')
  parser.add_argument('-l', '--link', help='Link to search.', action='append')


  args = parser.parse_args()

  #Argparse is great, but unfortunately specifying a default will append it to the list so we will check for it
  # explicitly
  fileArgs = args.file
  if fileArgs is None or len(fileArgs) == 0:
    fileArgs = ['./*']
  files = []
  #Now strip out only the files that have the right file extension
  for file in fileArgs:
    files += [file for file in glob(file) if (os.path.splitext(file)[1].lower() in FILE_TYPES)]

  if len(files) == 0 and args.link is None and not args.brain_assets:
    print('No valid inputs found.')
    exit(0)

  #Connect to Brain
  if args.server is not None:
    brainAPI = Brain(url=args.server, user_id= args.user, token = args.token)
  else:
    brainAPI = Brain(user_id=args.user, token=args.token)

  #now lets load the files into brain
  assetIds = {}
  loadingAssets = set()
  for file in files:
    if os.path.splitext(file)[1].lower() == '.links':
      with open(file) as inFile:
        for link in inFile:
          assetId, basename = loadLink(brainAPI, link)
          assetIds[assetId] = basename
          loadingAssets.add(assetId)

    else:
      assetId, basename = loadFile(brainAPI, file)
      assetIds[assetId] = basename
      loadingAssets.add(assetId)

  #now lets load any urls into brain or re-use them if they are already there
  if args.link is not None:
    for link in args.link:
      assetId, basename = loadLink(brainAPI, link)
      assetIds[assetId] = basename

  #Since we loaded asynchronously we need to wait untill all assets have finished loading to search them
  allAssets = {}
  while len(loadingAssets) > 0:
    print('Waiting for assets to process...')
    for assetId in loadingAssets.copy():
      asset = brainAPI.asset(assetId)
      if asset['status'] == 'finished':
        loadingAssets.remove(assetId)
        allAssets[asset['metadata']['filename']] = (asset['asset_id'], asset['content_url_wav'], asset['duration'])
      elif asset['status'] == 'failed':
        loadingAssets.remove(assetId)
        print('Unable to load: {}'.format(assetIds[assetId]))

    if len(loadingAssets) > 0:
      #give it a few second until we check again
      time.sleep(2.0)
  print('Loaded:')
  for asset in allAssets:
    assetInfo = allAssets[asset]
    print('{}: id {}, duration {}'.format(asset, assetInfo[0], assetInfo[2]))

if __name__ == '__main__':
  main()



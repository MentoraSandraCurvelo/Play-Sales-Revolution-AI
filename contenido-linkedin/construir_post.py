import json, re, sys
RESERVED = r'\|{}@[]()<>#*_~'
FIXED = ["IAM","IAMIntelligent","IAMInfluence","IAMCommercial","IAMSocial","IAMAmbassadors"]
def esc(t):
    return ''.join('\\'+c if c in RESERVED else c for c in t)
def inline_tags(t):
    # "#Palabra" written in the draft becomes a real LinkedIn hashtag
    return re.sub(r'\\#(\w+)', r'{hashtag|\\#|\1}', t)
def commentary(body, tags):
    tagtxt = ' '.join('{hashtag|\\#|%s}' % t for t in tags + FIXED)
    return inline_tags(esc(body)).rstrip() + '\n\n' + tagtxt
body = open(sys.argv[1], encoding='utf-8').read()
tags = [t for t in sys.argv[2].split(',') if t]
text = commentary(body, tags)
if len(sys.argv) > 4 and sys.argv[4] == 'patch':
    out = {"patch": {"$set": {"commentary": text}}}
else:
    out = {
      "author": "urn:li:person:tsJbwdb3B2",
      "commentary": text,
      "visibility": "PUBLIC",
      "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []},
      "lifecycleState": "PUBLISHED",
      "isReshareDisabledByAuthor": False
    }
json.dump(out, open(sys.argv[3], 'w', encoding='utf-8'), ensure_ascii=False)
print(text)
print("\nCARACTERES:", len(text))
